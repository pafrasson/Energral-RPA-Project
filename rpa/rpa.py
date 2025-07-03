import pandas as pd
from sqlalchemy import create_engine
import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import sqlite3
import threading
import os
import sys
import gspread
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession



'''
these conditionals get the paths of the database and pdf file respectivily, when in script it gets the one i setted,
when in .exe it gets the path where the .exe is.
'''
if getattr(sys, 'frozen', False):
    directory_path = os.path.dirname(sys.executable)
else:
    directory_path = 'C:/Users/Aluno/Documents/Tarefa TCS/Codigo/Energral-RPA-Project/backend'

if getattr(sys, 'frozen', False):
    pdf_path = os.path.dirname(sys.executable)
else:
    pdf_path = 'C:/Users/Aluno/Desktop'

if getattr(sys, 'frozen', False):
    creden_path = os.path.dirname(sys.executable)
else:
    creden_path = 'C:/Users/Aluno/Documents/Tarefa TCS/Codigo/Energral-RPA-Project/rpa'


'''
this function defines the credentials of the email and the recipient.
'''
def SendEmail(subject: str, body: str, attach: bool):
    sender_email = ""
    sender_password = ""
    recipient_email = ""

    logging.info('verifying if there is a need to attach the pdf file to the email')
    
    '''
    when called, it will check if the specific email has an attachment
    '''
    if attach == True:

        '''
        if it has an attachment it will enter this code, where it will build the pdf 
        attachment and then inserts it in the email body
        '''
        with open(pdf_file, "rb") as attachment:
            part = MIMEBase("application", "pdf")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= 'Planilha.pdf'",
        )
    
        logging.info('finished attaching to email')

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email
        html_part = MIMEText(body)
        message.attach(html_part)
        message.attach(part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            server.quit()
    else:
        
        '''
        if it doesn't have an attachment it enters this code and then builds the body without
        inserting an attachment
        '''
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email
        html_part = MIMEText(body)
        message.attach(html_part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            server.quit()

def SendAlert(alerts, cursor, conn):
    logging.info('starting to check for critical failure')

    '''
    this part runs through the alertas table and searches for each Falha Crítica
    when he finds one he sends an email to the specified manager with the machine id and the checklist id of the failure 
    '''
    if not alerts.empty:
        logging.info("there were failure machines")
        try:
            for row in alerts.itertuples(index=False):
                rowindex = 0
                logging.info('starting to check one item')
                valuesChecklist = pd.read_sql_query(f"SELECT c.id_equipamento, c.status FROM checklist c WHERE c.id_checklist = '{row.id_checklist}'", engine)
                status = valuesChecklist.loc[rowindex, 'status']
                equipament = valuesChecklist.loc[rowindex, 'id_equipamento']
                if status == 'Falha Crítica' or 'falha crítica':
                    logging.info("a critical failure was found")
                    SendEmail('🚨Alerta!🚨', 'a checagem de id: ' + row.id_checklist + ' da maquina de id: ' + equipament + ' constou falha critica', False)
                    cursor.execute('UPDATE checklist SET status = ? WHERE id_checklist = ?', ('Falha Crítica*', row.id_checklist))
                    conn.commit()
                rowindex = rowindex + 1
                logging.info('checked one item, going to next')
        except Exception as e:
            logging.error('failure in the processing', e)
    else:
        logging.info("no critical failure was found")
    logging.info('finished checking for critical failures')



def SendSheetsFile(alerts):
    logging.info('starting to write data tables to sheets')

    '''
    this part of the code gets the values of the tables of the database and write them in an google sheet file. 
    '''
    
    scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
    ]

    creds = creds = service_account.Credentials.from_service_account_file(f"{creden_path}/credentials.json", scopes=scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open('Teste')

    sheet1 = spreadsheet.worksheet('Plan1')
    sheet2 = spreadsheet.worksheet('Plan2')
    
    '''
    this part formats the columns to the right size
    '''

    sheet1.update([checklist.columns.values.tolist()] + checklist.values.tolist())
    sheet2.update([alerts.columns.values.tolist()] + alerts.values.tolist()) 



    spreadsheet.batch_update({
    "requests": [
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet1.id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 6
                },
                "properties": {
                    "pixelSize": 145
                },
                "fields": "pixelSize"
                }
            }
        ]
    })


    spreadsheet.batch_update({
    "requests": [
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet2.id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 4
                },
                "properties": {
                    "pixelSize": 200
                },
                "fields": "pixelSize"
                }
            }
        ]
    })
    
    '''
    this part exports the google sheets file as an pdf so we can attach it to the email send latter
    '''
    export_url = f"https://docs.google.com/spreadsheets/d/1-yzq6bPlmOVbigVHHEfb7pb2lDUqFT36_rSc0G6UXOU/export?format=pdf"

    authed_session = AuthorizedSession(creds)
    response = authed_session.get(export_url)

    if response.status_code == 200:
        with open(f"{pdf_path}/Teste.pdf", "wb") as f:
            f.write(response.content)


    logging.info('saved sheets file')

    logging.info('starting to send email')

    '''
    this part sends the email putting the sheets file as an attachment in the email
    '''
    SendEmail('Conclusao de envio de checklist', 'segue em anexo arquivo PDF com todas as checagens e falhas do dia', True)

    logging.info('email sent')

    logging.info('finished sending the email')




def StartAlerts():
    ultimo_id = 0

    while True:
        conn = sqlite3.connect(directory_path + '/database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM alertas WHERE id_alerta > ?", (ultimo_id,))
        novos_registros = cursor.fetchall()

        if novos_registros:
            alerts = pd.read_sql_query("SELECT * FROM alertas WHERE id_alerta > ?", engine, params=(ultimo_id,))

            SendAlert(alerts, cursor, conn)


            for registro in novos_registros:
                ultimo_id = max(ultimo_id, registro[0])


        conn.close()
        time.sleep(10)

def StartSheetsFile():
    while True:
        alerts = pd.read_sql_query("SELECT * FROM alertas;", engine)

        SendSheetsFile(alerts)

        time.sleep(14400)

'''
the threading let two loops run simultaniously
'''
def StartBot():
    t1 = threading.Thread(target=StartAlerts)
    t2 = threading.Thread(target=StartSheetsFile)

    t1.start()
    t2.start()



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


logging.info('Starting process')

logging.info('connecting to systems')

'''
this part connects the code with the database and gets the information of the
specified table
'''
pdf_file = f'{pdf_path}/Teste.pdf'
engine = create_engine(f'sqlite:///{directory_path}/database.db')
checklist = pd.read_sql_query("SELECT * FROM checklist;", engine)
'''
this variable initiates an counter to run through the rows of the table Alertas
'''
logging.info('finished connecting to systems')



StartBot()
import pandas as pd
from sqlalchemy import create_engine
from openpyxl import load_workbook
import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import sqlite3
import threading


'''
this function defines the credentials of the email and the recipient.
'''
def SendEmail(subject: str, body: str, attach: bool):
    sender_email = "gabriel.paiva.gamers@gmail.com"
    sender_password = "rakvlxfpssgmfnrb"
    recipient_email = "gabriel.paiva.gamers@gmail.com"

    logging.info('verifying if there is a need to attach the excel file to the email')
    
    '''
    when called, it will check if the specific email has an attachment
    '''
    if attach == True:

        '''
        if it has an attachment it will enter this code, where it will build the excel 
        attachment and then inserts it in the email body
        '''
        with open(excelfile, "rb") as attachment:
            part = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= 'Planilha.xlsx'",
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
                value =row.id_checklist
                valuesChecklist = pd.read_sql_query(f"SELECT c.id_equipamento, c.status FROM checklist c WHERE c.id_checklist = '{row.id_checklist}'", engine)
                status = valuesChecklist.loc[rowindex, 'status']
                equipament = valuesChecklist.loc[rowindex, 'id_equipamento']
                if status == 'Falha Crítica':
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
    logging.info('finished chicking for critical failures')



def SendExcelFile(alerts):
    logging.info('starting to write data tables to excel')

    '''
    this part of the code gets the values of the tables of the database and write them in an excel file.
    this part will later be updated to write in google sheets 
    '''
    with pd.ExcelWriter(excelfile) as writer:
        checklist.to_excel(excel_writer=writer, sheet_name='Plan1', index = None)
        alerts.to_excel(excel_writer=writer, sheet_name='Plan2', index = None)
    logging.info('finished writing to excel')

    logging.info('opening excel to to adjust the size of columns')
    wb = load_workbook(excelfile)
    ws = wb.active

    '''
    this loop runs through the columns of the excel and then through each cell in the column, searching for the highest value of letters
    to set the column size, he then saves the excel file
    '''
    for coluna in ws.columns:
        max_length = 0
        coluna_letra = coluna[0].column_letter
        for celula in coluna:
            try:
                if celula.value:
                    max_length = max(max_length, len(str(celula.value)))
            except:
                pass
        ws.column_dimensions[coluna_letra].width = max_length + 2
    logging.info('finished formatting excel')

    wb.save(excelfile)

    logging.info('saved excel file')

    logging.info('starting to send email')

    '''
    this part sends the email putting the excel file as an attachment in the email
    '''
    SendEmail('Conclusao de envio de checklist', 'segue em anexo arquivo excel com todas as checagens e falhas do dia', True)

    logging.info('email sent')

    logging.info('finished process')




def StartAlerts():
    ultimo_id = 0

    while True:
        conn = sqlite3.connect('C:/Users/Aluno/Documents/Tarefa TCS/Codigo/Energral-RPA-Project/backend/database.db')
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

def StartExcelFile():
    while True:
        alerts = pd.read_sql_query("SELECT * FROM alertas;", engine)

        SendExcelFile(alerts)

        time.sleep(14400)





logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


logging.info('Starting process')

logging.info('connecting to sistems')

'''
this part connects the code with the database and gets the information of the
specified table
'''

excelfile = "C:/Users/Aluno/Desktop/Teste.xlsx"
engine = create_engine('sqlite:///C:/Users/Aluno/Documents/Tarefa TCS/Codigo/Energral-RPA-Project/backend/database.db')
checklist = pd.read_sql_query("SELECT * FROM checklist;", engine)
'''
this variable initiates an counter to run through the rows of the table Alertas
'''
logging.info('finished connecting to sistems')



t1 = threading.Thread(target=StartAlerts)
t2 = threading.Thread(target=StartExcelFile)

t1.start()
t2.start()


import pandas as pd
from sqlalchemy import create_engine
from openpyxl import load_workbook
import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def SendEmail(subject: str, body: str, attach: bool):
    sender_email = "gabriel.paiva.gamers@gmail.com"
    sender_password = "rakvlxfpssgmfnrb"
    recipient_email = "gabriel.paiva.gamers@gmail.com"

    logging.info('working to attach the excel file to the email')
    if attach == True:
        with open(arquivo_excel, "rb") as attachment:
            # Adicione o anexo à mensagem
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
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email
        html_part = MIMEText(body)
        message.attach(html_part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


logging.info('Starting process')

logging.info('connecting to sistems')
arquivo_excel = "C:/Users/Aluno/Desktop/Teste.xlsx"
engine = create_engine('sqlite:///C:/Users/Aluno/Documents/Tarefa TCS/Codigo/Energral-RPA-Project/backend/database.db')
checklist = pd.read_sql_query("SELECT * FROM maquinas;", engine)
alertas = pd.read_sql_query("SELECT * FROM alertas;", engine)
i = 0
logging.info('finished connecting to sistems')

logging.info('starting to check for critical failure')


if not alertas.empty:
    logging.info("there were failure machines")
    try:
        for row in alertas.itertuples(index=False):
            logging.info('starting to check one item')
            valor = f"{row.id_alerta} {row.id_checklist} {row.status_de_resolucao}"
            valoresChecklist = pd.read_sql_query("SELECT c.id_equipamento, c.status from alertas a INNER JOIN checklist c ON a.id_checklist = c.id_checklist", engine)
            status = valoresChecklist.loc[i, 'status']
            equipamento = valoresChecklist.loc[i, 'id_equipamento']
            print(status)
            if status == 'Falha Crítica':
                logging.info("a critical failure was found")
                SendEmail('Alerta!', 'a checagem de id: ' + row.id_checklist + 'da maquina de id: ' + equipamento + 'constou falha critica', False)
            i = i + 1
            logging.info('checked one item, going to next')
    except Exception as e:
        logging.error('failure in the processing', e)
else:
    logging.info("no critical failure was found")




logging.info('starting to write data tables to excel')
checklist.to_excel(arquivo_excel, sheet_name="Plan1", index=False)
alertas.to_excel(arquivo_excel, sheet_name="Plan2", index=False)
logging.info('finished writing to excel')

logging.info('opening excel to to adjust the size of columns')
wb = load_workbook(arquivo_excel)
ws = wb.active

'''
esse loop percorre cada coluna e altera o tamanho dela para encaixar o maior valor presente nas celulas
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

wb.save(arquivo_excel)
logging.info('saved excel file')

logging.info('starting to send email')

SendEmail('Conclusao de envio de checklist', 'segue em anexo arquivo excel com todas as checagens e falhas do dia', True)

logging.info('email sent')

logging.info('finished process')




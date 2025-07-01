import pandas as pd
from sqlalchemy import create_engine
from openpyxl import load_workbook
import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


arquivo_excel = "C:/Users/Aluno/Desktop/Teste.xlsx"
engine = create_engine('sqlite:///C:/Users/Aluno/Documents/Tarefa TCS/Codigo/Energral-RPA-Project/backend/database.db')
checklist = pd.read_sql_query("SELECT * FROM maquinas;", engine)
alertas = pd.read_sql_query("SELECT * FROM alertas;", engine)

for row in checklist.itertuples(index=False):
    valor = row.id_alerta + ' ' + row.id_checklist + ' ' + row.status + ' ' + row.status
    print(valor)




checklist.to_excel(arquivo_excel, sheet_name="Plan1", index=False)
alertas.to_excel(arquivo_excel, sheet_name="Plan2", index=False)

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

wb.save(arquivo_excel)

sender_email = "gabriel.paiva.gamers@gmail.com"
sender_password = "rakvlxfpssgmfnrb"
recipient_email = "gabriel.paiva.gamers@gmail.com"
subject = "Segue planilhas com todos os checklists do dia"
body = "com anexo"

with open(arquivo_excel, "rb") as attachment:
    # Adicione o anexo à mensagem
    part = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    part.set_payload(attachment.read())
encoders.encode_base64(part)
part.add_header(
    "Content-Disposition",
    f"attachment; filename= 'Planilha.xlsx'",
)

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





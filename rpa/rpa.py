import pandas as pd
import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import threading
import os
import sys
import gspread
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

status_colors = {
    'Inativo': '#FFC300',       # Amarelo (neutro, para inativo)
    'Falha': '#FF5733',         # Laranja-Vermelho (alerta, para falha)
    'Falha Crítica': '#C70039', # Vermelho Escuro (alto alerta, para falha crítica)
    'Operacional': '#28A745',   # Verde (positivo, para operacional)
    'Manutenção': '#007BFF'     # Azul (informativo, para em manutenção)
}

# Path configuration
if getattr(sys, 'frozen', False):
    pdf_path = os.path.dirname(sys.executable)
    creden_path = os.path.dirname(sys.executable)
    png_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    pdf_path = 'C:/Users/Aluno/Desktop'
    creden_path = 'C:/Users/Aluno/Documents/Tarefa TCS/Codigo/Energral-RPA-Project/rpa'
    png_path = 'C:/Users/Aluno/Documents/Tarefa TCS/Codigo/Energral-RPA-Project/rpa'

pdf_file = os.path.join(pdf_path, 'Teste.pdf')
png_file = os.path.join(png_path, 'grafico_status_maquinas.png')

# Email configuration
EMAIL_CONFIG = {
    "sender_email": "",
    "sender_password": "",
    "recipient_email": ""
}

# API configuration
API_CONFIG = {
    "base_url": "http://localhost:3000/api",
    "timeout": 10,
    "retries": 3
}

def create_http_session():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retry_strategy = Retry(
        total=API_CONFIG["retries"],
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def check_api_availability():
    """Check if API is available"""
    try:
        session = create_http_session()
        response = session.get(f"{API_CONFIG['base_url']}/checklist", timeout=API_CONFIG["timeout"])
        return response.status_code == 200
    except Exception:
        return False

def SendEmail(subject: str, body: str, attach: bool):
    """Send email with optional attachments (PDF and graph)"""
    try:
        # Create message container
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = EMAIL_CONFIG["sender_email"]
        message['To'] = EMAIL_CONFIG["recipient_email"]
        
        # Add HTML body
        message.attach(MIMEText(body, 'html'))

        # Attach files if requested and they exist
        if attach:
            # List of possible attachments with their display names
            attachments = [
                (pdf_file, '/Teste.pdf'),
                (png_file, '/grafico_status_maquinas.png')
            ]
            
            files_attached = 0
            
            for file_path, display_name in attachments:
                if os.path.exists(file_path):
                    filetype = display_name.split('.')
                    filetype = filetype[1]
                    print(filetype)
                    try:
                        with open(file_path, "rb") as f:
                            part = MIMEBase("image", f"{filetype}")
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename={display_name}"
                            )
                            message.attach(part)
                        files_attached += 1
                        logging.info(f'Attached file: {file_path}')
                    except Exception as file_error:
                        logging.warning(f'Failed to attach {file_path}: {file_error}')
                else:
                    logging.warning(f'File not found for attachment: {file_path}')
            
            if files_attached == 0:
                logging.warning('No files were attached despite attach=True')

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(message)
        
        logging.info('Email sent successfully')
        return True
        
    except smtplib.SMTPException as smtp_error:
        logging.error(f'SMTP error sending email: {smtp_error}')
    except Exception as e:
        logging.error(f'Error sending email: {e}')
    
    return False

def SendAlert(alerts):
    """Send alerts for critical failures"""
    if not alerts:
        logging.info("No alerts found")
        return

    try:
        session = create_http_session()

        # Get checklist data
        response = session.get(f"{API_CONFIG['base_url']}/checklist", timeout=API_CONFIG["timeout"])
        checklist = response.json()
        checklist_dict = {item['id_checklist']: item for item in checklist}

        for row in alerts:
            checklist_id = row.get('id_checklist')
            logging.info('Checking item')

            if checklist_id in checklist_dict:
                item = checklist_dict[checklist_id]
                status = item.get('status', '').lower()
                equipament = item.get('id_equipamento', 'unknown')

                if status == 'falha crítica':
                    logging.info(f"Critical failure found in checklist {checklist_id}")
                    SendEmail(
                        '🚨Alerta!🚨',
                        f'A checagem de id: {checklist_id} da máquina de id: {equipament} constou falha crítica',
                        False
                    )

                    # Update status
                    update_response = session.put(
                        f"{API_CONFIG['base_url']}/checklist/{checklist_id}/status",
                        json={"status": "Falha Crítica*"},
                        timeout=API_CONFIG["timeout"]
                    )

                    if update_response.status_code != 200:
                        logging.error(f"Failed to update status for checklist {checklist_id}")

            logging.info('Item checked, moving to next')

    except Exception as e:
        logging.error(f'Failure in processing alerts: {str(e)}')
    finally:
        logging.info('Finished checking for critical failures')

def GenerateGraph():
    """Generate status distribution graph"""
    try:
        session = create_http_session()
        maquinas = session.get(f"{API_CONFIG['base_url']}/maquinas").json()
        
        # Extrai o status de cada máquina
        status_list = [maquina['status_maquina'].lower() for maquina in maquinas]

        # Conta a quantidade de cada status
        status_counts = Counter(status_list)

        data_points = [
            (status_counts.get('falha', 0), "Falha"),
            (status_counts.get('operacional', 0), "Operacional"),
            (status_counts.get('inativo', 0), "Inativo"),
            (status_counts.get('falha crítica', 0), "Falha Crítica"),
            (status_counts.get('em manutenção', 0), "Manutenção")
        ]

        filtx = []
        filtlabel = []
        status_color_list = []

        for count, status in data_points:
            if count > 0:
                filtx.append(count)
                filtlabel.append(f'{status}: {count}')
                status_color_list.append(status)
        
        if not filtx:
            plt.close()
            logging.warning('No data available to generate graph')
            return False
        
        ordered_colors = [status_colors[status] for status in status_color_list]

        fig, ax = plt.subplots(figsize=(16, 9))
        
        wedges, texts, autotexts = ax.pie(filtx,
                                        colors=ordered_colors,
                                        autopct='%1.1f%%',
                                        pctdistance=0.85,
                                        wedgeprops={"linewidth": 1, "edgecolor": "white"},
                                        startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
            autotext.set_bbox(dict(boxstyle="round,pad=0.2", fc="black", ec="none", lw=0, alpha=0.5))

        ax.legend(wedges, filtlabel,
                title="Status das Máquinas",
                loc="center left",
                bbox_to_anchor=(1.05, 0, 0.5, 1),
                fontsize=12,
                title_fontsize=14,
                frameon=False)
        
        ax.set_title('Distribuição do Status das Máquinas', fontsize=20, fontweight='bold', color='#333333', pad=30)
        ax.set_aspect('equal')
        ax.axis('off')

        fig.patch.set_facecolor('#f5f5f5')

        plt.tight_layout()
        plt.savefig(png_file, dpi=300, bbox_inches='tight')
        plt.show()
        plt.close()
        
        logging.info('Graph generated successfully')
        return True

    except Exception as e:
        logging.error(f'Error generating graph: {str(e)}')
        return False

def SendSheetsFile():
    """Export data to Google Sheets and save as PDF"""
    try:
        # First check API availability
        if not check_api_availability():
            logging.error("API not available, skipping sheet update")
            return

        session = create_http_session()

        # Get data from API
        checklist = session.get(f"{API_CONFIG['base_url']}/checklist", timeout=API_CONFIG["timeout"]).json()
        alerts = session.get(f"{API_CONFIG['base_url']}/alertas", timeout=API_CONFIG["timeout"]).json()

        # Authenticate with Google Sheets
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = service_account.Credentials.from_service_account_file(
            f'{creden_path}/credentials.json',
            scopes=scope
        )
        client = gspread.authorize(creds)

        # Open spreadsheet and update data
        spreadsheet = client.open('Teste')

        # Update Plan1 with checklist data
        if checklist:
            sheet1 = spreadsheet.worksheet('Plan1')
            header = list(checklist[0].keys())
            rows = [list(item.values()) for item in checklist]
            sheet1.clear()
            sheet1.update([header] + rows)

        # Update Plan2 with alerts data
        if alerts:
            sheet2 = spreadsheet.worksheet('Plan2')
            header = list(alerts[0].keys())
            rows = [list(item.values()) for item in alerts]
            sheet2.clear()
            sheet2.update([header] + rows)

        # Format columns
        spreadsheet.batch_update({
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {"sheetId": sheet1.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 6},
                        "properties": {"pixelSize": 145},
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {"sheetId": sheet2.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 4},
                        "properties": {"pixelSize": 200},
                        "fields": "pixelSize"
                    }
                }
            ]
        })

        # Export to PDF
        export_url = "https://docs.google.com/spreadsheets/d/1-yzq6bPlmOVbigVHHEfb7pb2lDUqFT36_rSc0G6UXOU/export?format=pdf"
        authed_session = AuthorizedSession(creds)
        response = authed_session.get(export_url)

        if response.status_code == 200:
            with open(pdf_file, "wb") as f:
                f.write(response.content)
            logging.info('PDF file saved successfully')
            
            # Generate and save the graph
            graph_success = GenerateGraph()
            
            # Small delay to ensure file is written
            time.sleep(2)
            
            # Prepare email based on what we have
            email_body = 'Segue em anexo arquivo PDF com todas as checagens e falhas do dia'
            attachments = True
            
            if not graph_success or not os.path.exists(png_file):
                email_body += '<br><strong>OBS:</strong> O gráfico de status não pôde ser gerado'
                if not os.path.exists(pdf_file):
                    attachments = False
                    email_body = 'Não foi possível gerar os relatórios. Por favor, verifique o sistema.'

            SendEmail(
                'Conclusão de envio de checklist',
                email_body,
                attachments
            )
        else:
            logging.error(f'Failed to export PDF: {response.status_code}')
            SendEmail(
                'Falha no envio de checklist',
                'Não foi possível gerar o relatório PDF. Por favor, verifique o sistema.',
                False
            )

    except Exception as e:
        logging.error(f'Error exporting to sheets: {str(e)}')
        SendEmail(
            'Erro no sistema de relatórios',
            f'Ocorreu um erro ao tentar gerar os relatórios: {str(e)}',
            False
        )

def StartAlerts():
    """Monitor alerts continuously"""
    last_alert_id = 0

    while True:
        try:
            session = create_http_session()
            response = session.get(f"{API_CONFIG['base_url']}/alertas", timeout=API_CONFIG["timeout"])
            alerts = response.json()

            new_alerts = [alert for alert in alerts if alert.get('id_alerta', 0) > last_alert_id]

            if new_alerts:
                SendAlert(new_alerts)
                last_alert_id = max(alert.get('id_alerta', 0) for alert in new_alerts)

            time.sleep(10)

        except Exception as e:
            logging.error(f'Error in alert monitoring: {str(e)}')
            time.sleep(30)

def StartSheetsFile():
    """Generate periodic reports"""
    while True:
        try:
            SendSheetsFile()
            time.sleep(14400)  # 4 hours
        except Exception as e:
            logging.error(f'Error in periodic reports: {str(e)}')
            time.sleep(3600)  # Wait 1 hour if error occurs

def StartBot():
    """Start monitoring threads"""
    t1 = threading.Thread(target=StartAlerts, daemon=True)
    t2 = threading.Thread(target=StartSheetsFile, daemon=True)

    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('Shutting down monitoring system')

if __name__ == '__main__':
    logging.info('Starting process')
    logging.info('Connecting to systems')

    # Initial data load
    try:
        session = create_http_session()
        maquinas = session.get(f"{API_CONFIG['base_url']}/maquinas", timeout=API_CONFIG["timeout"]).json()
        checklist = session.get(f"{API_CONFIG['base_url']}/checklist", timeout=API_CONFIG["timeout"]).json()
        alerts = session.get(f"{API_CONFIG['base_url']}/alertas", timeout=API_CONFIG["timeout"]).json()
        logging.info('Finished connecting to systems')

        StartBot()
    except Exception as e:
        logging.error(f'Failed to initialize: {str(e)}')

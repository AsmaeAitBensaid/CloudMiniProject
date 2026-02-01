import logging
import azure.functions as func
from fpdf import FPDF
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

BLOB_CONN_STR = os.environ['BLOB_CONN_STR']
BLOB_CONTAINER = "certificates"
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL')

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing certificate request.')

    name = req.params.get('name')
    course = req.params.get('course')
    date = req.params.get('date') or datetime.today().strftime("%d/%m/%Y")
    recipient_email = req.params.get('email')

    if not name or not course:
        return func.HttpResponse("Merci de fournir 'name' et 'course'", status_code=400)

    # Génération PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Certificat de participation", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 14)
    pdf.cell(0, 10, f"Nom: {name}", ln=True)
    pdf.cell(0, 10, f"Formation: {course}", ln=True)
    pdf.cell(0, 10, f"Date: {date}", ln=True)

    file_name = f"{name.replace(' ', '_')}_{course.replace(' ', '_')}.pdf"
    local_path = f"/tmp/{file_name}"
    pdf.output(local_path)

    # Upload dans Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
    container_client = blob_service_client.get_container_client(BLOB_CONTAINER)
    try:
        container_client.create_container()
    except:
        pass
    with open(local_path, "rb") as data:
        container_client.upload_blob(name=file_name, data=data, overwrite=True)

    # Envoi email si email fourni
    if recipient_email and SENDGRID_API_KEY:
        try:
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=recipient_email,
                subject='Votre certificat',
                html_content=f'Bonjour {name}, votre certificat pour {course} est prêt.',
            )
            with open(local_path, 'rb') as f:
                message.add_attachment(f.read(), file_name, 'application/pdf')
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            logging.error(f"Erreur envoi email: {e}")

    return func.HttpResponse(f"Certificat généré et stocké : {file_name}")


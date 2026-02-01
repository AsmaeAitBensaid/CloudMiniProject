from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from datetime import datetime
import os
import io
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configuration Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = "certificates"

# Créer le dossier local pour les certificats temporaires
if not os.path.exists('certificates'):
    os.makedirs('certificates')

def upload_to_blob(file_path, blob_name):
    """Upload un fichier vers Azure Blob Storage"""
    try:
        if not AZURE_STORAGE_CONNECTION_STRING:
            print("⚠️  Azure Storage non configuré, fichier sauvegardé localement")
            return None
            
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        
        # Créer le conteneur s'il n'existe pas
        try:
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            container_client.get_container_properties()
        except:
            container_client = blob_service_client.create_container(CONTAINER_NAME)
        
        # Upload le fichier
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(
                data, 
                overwrite=True,
                content_settings=ContentSettings(content_type='application/pdf')
            )
        
        # Retourner l'URL du blob
        return blob_client.url
    except Exception as e:
        print(f"❌ Erreur upload blob: {e}")
        return None

def generate_certificate(name, course, date_str, certificate_id):
    """Génère un certificat PDF personnalisé"""
    
    # Créer le nom du fichier
    filename = f"certificate_{certificate_id}.pdf"
    filepath = os.path.join('certificates', filename)
    
    # Créer le PDF en mode paysage
    c = canvas.Canvas(filepath, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Couleurs
    primary_color = colors.HexColor('#1a237e')  # Bleu foncé
    gold_color = colors.HexColor('#FFD700')      # Or
    
    # ===== BORDURE DÉCORATIVE =====
    c.setStrokeColor(primary_color)
    c.setLineWidth(8)
    c.rect(1*cm, 1*cm, width-2*cm, height-2*cm, stroke=1, fill=0)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(2)
    c.rect(1.3*cm, 1.3*cm, width-2.6*cm, height-2.6*cm, stroke=1, fill=0)
    
    # ===== TITRE =====
    c.setFont("Helvetica-Bold", 48)
    c.setFillColor(primary_color)
    title = "CERTIFICAT"
    title_width = c.stringWidth(title, "Helvetica-Bold", 48)
    c.drawString((width - title_width) / 2, height - 4*cm, title)
    
    # ===== SOUS-TITRE =====
    c.setFont("Helvetica", 18)
    c.setFillColor(colors.black)
    subtitle = "DE RÉUSSITE"
    subtitle_width = c.stringWidth(subtitle, "Helvetica", 18)
    c.drawString((width - subtitle_width) / 2, height - 5.5*cm, subtitle)
    
    # ===== LIGNE DÉCORATIVE =====
    c.setStrokeColor(gold_color)
    c.setLineWidth(2)
    c.line(width/2 - 8*cm, height - 6.5*cm, width/2 + 8*cm, height - 6.5*cm)
    
    # ===== TEXTE "Décerné à" =====
    c.setFont("Helvetica-Oblique", 16)
    c.setFillColor(colors.grey)
    presented_text = "Décerné à"
    presented_width = c.stringWidth(presented_text, "Helvetica-Oblique", 16)
    c.drawString((width - presented_width) / 2, height - 8.5*cm, presented_text)
    
    # ===== NOM DU BÉNÉFICIAIRE =====
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(primary_color)
    name_width = c.stringWidth(name, "Helvetica-Bold", 36)
    c.drawString((width - name_width) / 2, height - 10.5*cm, name)
    
    # ===== LIGNE SOUS LE NOM =====
    c.setStrokeColor(gold_color)
    c.setLineWidth(1)
    c.line(width/2 - 10*cm, height - 11*cm, width/2 + 10*cm, height - 11*cm)
    
    # ===== TEXTE DE RECONNAISSANCE =====
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    recognition_text = f"Pour avoir complété avec succès la formation"
    recognition_width = c.stringWidth(recognition_text, "Helvetica", 14)
    c.drawString((width - recognition_width) / 2, height - 13*cm, recognition_text)
    
    # ===== NOM DE LA FORMATION =====
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(primary_color)
    course_width = c.stringWidth(course, "Helvetica-Bold", 20)
    c.drawString((width - course_width) / 2, height - 14.5*cm, course)
    
    # ===== DATE =====
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    date_text = f"Délivré le {date_str}"
    date_width = c.stringWidth(date_text, "Helvetica", 12)
    c.drawString((width - date_width) / 2, height - 16.5*cm, date_text)
    
    # ===== ID DU CERTIFICAT =====
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.grey)
    id_text = f"ID: {certificate_id}"
    c.drawString(2*cm, 1.5*cm, id_text)
    
    # ===== SIGNATURE (simulée) =====
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.black)
    
    # Signature gauche
    c.drawString(width/2 - 8*cm, 4*cm, "_________________________")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 - 7.5*cm, 3.3*cm, "Directeur de Formation")
    
    # Signature droite
    c.drawString(width/2 + 3*cm, 4*cm, "_________________________")
    c.setFont("Helvetica", 10)
    c.drawString(width/2 + 3.5*cm, 3.3*cm, "Responsable Académique")
    
    # ===== SCEAU/TAMPON (simulé) =====
    c.setStrokeColor(gold_color)
    c.setFillColor(colors.white)
    c.setLineWidth(3)
    c.circle(width/2, 4.5*cm, 1.5*cm, stroke=1, fill=1)
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(gold_color)
    seal_text = "CERTIFIÉ"
    seal_width = c.stringWidth(seal_text, "Helvetica-Bold", 10)
    c.drawString((width - seal_width) / 2, 4.8*cm, seal_text)
    
    c.setFont("Helvetica", 8)
    seal_year = "2026"
    seal_year_width = c.stringWidth(seal_year, "Helvetica", 8)
    c.drawString((width - seal_year_width) / 2, 4.2*cm, seal_year)
    
    # Sauvegarder le PDF
    c.save()
    
    return filepath, filename

@app.route('/')
def index():
    """Page d'accueil avec le formulaire"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Générer le certificat"""
    try:
        # Récupérer les données du formulaire
        name = request.form.get('name', '').strip()
        course = request.form.get('course', '').strip()
        date_str = request.form.get('date', '')
        
        # Validation
        if not name or not course or not date_str:
            flash('❌ Tous les champs sont obligatoires', 'error')
            return redirect(url_for('index'))
        
        # Générer un ID unique
        certificate_id = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Générer le certificat
        filepath, filename = generate_certificate(name, course, date_str, certificate_id)
        
        # Upload vers Azure Blob Storage
        blob_url = upload_to_blob(filepath, filename)
        
        # Préparer les informations pour la page de succès
        certificate_info = {
            'name': name,
            'course': course,
            'date': date_str,
            'id': certificate_id,
            'filename': filename,
            'blob_url': blob_url
        }
        
        flash('✅ Certificat généré avec succès !', 'success')
        return render_template('success.html', cert=certificate_info)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        flash(f'❌ Erreur lors de la génération: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    """Télécharger le certificat"""
    try:
        filepath = os.path.join('certificates', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            flash('❌ Fichier introuvable', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'❌ Erreur de téléchargement: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health():
    """Endpoint de santé"""
    return {'status': 'healthy', 'service': 'Certificate Generator'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

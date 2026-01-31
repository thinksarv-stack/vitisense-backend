from flask import Flask, render_template, request, send_file
from flask_cors import CORS
from google import genai
from PIL import Image
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GEMINI_API_KEY") 
client = genai.Client(api_key=API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            leaf_file = request.files['leaf_image']
            grape_file = request.files['grape_image']
            sugar = request.form.get('sugar', '15.0')

            leaf_img = Image.open(leaf_file)
            grape_img = Image.open(grape_file)

            prompt = f"""
            Act as a Senior Viticulturist. Analyze these images. Sugar: {sugar} Brix.
            Provide a "VITISENSE Diagnostic Report" using ONLY these points:
            - 🌿 DIAGNOSIS: [Healthy or specific disease name]
            - 🔍 SYMPTOMS: [Max 15 words on visual signs]
            - 🧪 TREATMENT: [If diseased: Give specific pesticide names like Mancozeb, Myclobutanil, or Copper. If healthy: None]
            - 📅 SCHEDULE: [If diseased: Provide exact duration and frequency (e.g., 'Apply every 7 days for 2 weeks'). If healthy: Monitoring]
            - 🍇 RIPENESS: [Early/Optimal/Over-ripe]
            - 📊 MARKET: [Export/Local/Not Ready]

            Constraints: Use bullet points. Be efficient but include specific chemical names.
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, leaf_img, grape_img]
            )
            
            return render_template('index.html', result=True, report=response.text)
        except Exception as e:
            return render_template('index.html', result=False, error=str(e))
    return render_template('index.html', result=False)

@app.route('/download-report', methods=['POST'])
def download_report():
    report_text = request.form.get('report_content')
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 800, "VITISENSE PRO - AGRONOMIST REPORT")
    p.setFont("Helvetica", 11)
    y = 770
    for line in report_text.split('\n'):
        p.drawString(50, y, line)
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="Farmer_Report.pdf")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

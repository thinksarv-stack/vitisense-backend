from flask import Flask, render_template, request, send_file
from flask_cors import CORS
from google import genai
from PIL import Image
import os
from io import BytesIO

# PDF Libraries
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

app = Flask(__name__)
CORS(app)

# SETUP GEMINI CLIENT
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
            Act as a Senior Viticulturist and Plant Pathologist. 
            Analyze the uploaded leaf and fruit images meticulously. 
            Input Data: Refractometer sugar reading is {sugar} Brix.

            Provide a "VITISENSE Diagnostic Report" with 2-3 detailed sentences for each point:

            - 🌿 DIAGNOSIS: Clearly identify the health status or specific disease name. Explain the physiological state of the vine and why this specific diagnosis was reached based on the visual evidence.
            - 🔍 SYMPTOMS: Describe the specific lesions, necrotic spots, or discoloration patterns seen on the leaf or fruit. Explain how these symptoms interfere with photosynthesis or fruit development.
            - 🧪 TREATMENT: Recommend specific fungicides or pesticides like Mancozeb, Myclobutanil, or Copper Hydroxide. Detail the chemical mode of action and why this particular substance is effective for the detected pathogen. 
            - 📅 SCHEDULE: Provide a precise application timeline including frequency and total duration. Explain the importance of following this window to prevent the pathogen's lifecycle from continuing or becoming resistant.
            - 🍇 RIPENESS: Evaluate the fruit's maturity using the {sugar} Brix data and visual coloration. Discuss the balance between sugar accumulation and acid degradation at this specific stage.
            - 📊 MARKET: Determine the commercial destination based on quality and ripeness. Provide a final recommendation on whether to harvest immediately, wait for better parameters, or treat and re-evaluate.

            Constraints: Use bullet points. Ensure every point contains 2-3 insightful, complete sentences.
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
    
    # PDF Setup
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor=colors.HexColor("#a29bfe"))
    body_style = styles['Normal']
    body_style.fontSize = 11
    body_style.leading = 14 
    
    story = []
    story.append(Paragraph("VITISENSE PRO - OFFICIAL AGRONOMIST REPORT", title_style))
    story.append(Spacer(1, 12))
    
    # Process text for PDF
    lines = report_text.replace("**", "").replace("#", "").split('\n')
    for line in lines:
        if line.strip():
            story.append(Paragraph(line, body_style))
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="VitiSense_Report.pdf")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

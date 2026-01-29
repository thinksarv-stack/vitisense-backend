from flask import Flask, render_template, request
from flask_cors import CORS 
from google import genai
from PIL import Image
import os 

# MUST be named 'app' to match Render's default 'gunicorn app:app' command
app = Flask(__name__)

# ENABLE CORS so your Netlify frontend can reach this API
CORS(app)

# SETUP GEMINI CLIENT
# Ensure 'GEMINI_API_KEY' is added in Render -> Dashboard -> Environment
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
            Act as a Senior Viticulturist. 
            Analyze the provided leaf and fruit images. 
            Input Data: Sugar level is {sugar} Brix.

            Provide a "VITISENSE Diagnostic Report" using ONLY these sections:
            ## 🌿 LEAF PATHOLOGY
            * **Diagnosis:** [Healthy / Black Rot / Esca / Leaf Blight]
            * **Key Symptoms:** [1-sentence observation]

            ## 🍇 HARVEST ANALYSIS
            * **Ripeness Stage:** [Early / Optimal / Over-ripe]
            * **Brix Interpretation:** [Analysis of {sugar} Brix]

            ## 📊 MARKET ADVICE
            * **Quality Grade:** [Export Quality / Local Market / Not Ready]
            * **Action Item:** [One specific instruction]

            Constraints: Use ONLY bullet points. Keep points under 15 words.
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=[prompt, leaf_img, grape_img]
            )
            
            return render_template('index.html', result=True, report=response.text)

        except Exception as e:
            print(f"Server Error: {e}")
            return render_template('index.html', result=False, error=str(e))

    return render_template('index.html', result=False)

if __name__ == '__main__':
    # Render uses the PORT environment variable; 5000 is only for local testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

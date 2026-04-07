"""
ITN 피트니스 — Vercel 배포용 Flask 앱
"""
from flask import Flask, request, jsonify, send_file, Response
import base64, json, io, re, os, sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from pdf_generator import generate_routine_pdf

app = Flask(__name__, template_folder='../templates')

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html')

@app.route('/api/extract', methods=['POST'])
def extract_inbody():
    try:
        data = request.get_json()
        img_b64 = data.get('image')

        import requests as req
        from PIL import Image

        img_bytes = base64.b64decode(img_b64.split(',')[-1])
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 이미지를 JPEG base64로 재인코딩
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        img_b64_clean = base64.b64encode(buf.getvalue()).decode()

        prompt = """이 인바디 결과지 이미지에서 수치를 추출해주세요.
반드시 아래 JSON 형식으로만 답하세요. 없는 항목은 null로 표시하세요.

{
  "measured_at": "YYYY-MM-DD",
  "weight": 숫자,
  "muscle_mass": 숫자,
  "body_fat_mass": 숫자,
  "body_fat_pct": 숫자,
  "visceral_fat_level": 숫자,
  "bmi": 숫자,
  "inbody_score": 숫자,
  "bmr": 숫자
}

JSON 외에 다른 텍스트는 절대 포함하지 마세요."""

        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_b64_clean}}
                ]
            }]
        }
        resp = req.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        response_json = resp.json()
        text = response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text).strip()
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        result = json.loads(json_match.group() if json_match else text)

        for k, v in result.items():
            if v is None:
                result[k] = ''

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        member = data.get('member', {})
        inbody = data.get('inbody', {})

        pdf_bytes = generate_routine_pdf(member, inbody)

        name = member.get('name', '회원')
        today = date.today().strftime('%Y%m%d')
        filename = f"ITN_{name}_운동루틴_{today}.pdf"

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preview_pdf', methods=['POST'])
def preview_pdf():
    try:
        data = request.get_json()
        member = data.get('member', {})
        inbody = data.get('inbody', {})

        pdf_bytes = generate_routine_pdf(member, inbody)
        pdf_b64 = base64.b64encode(pdf_bytes).decode()

        return jsonify({'success': True, 'pdf': pdf_b64})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

app = app

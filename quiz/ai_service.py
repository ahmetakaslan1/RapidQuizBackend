import os
import json
from google import genai
from django.conf import settings

def generate_questions(topic=None, num_questions=100):
    """
    Generates questions using Google Gemini API.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY bulunamadı. Lütfen .env dosyasına ekleyin.")

    client = genai.Client(api_key=api_key)
    generated_questions = []
    
    # If no topic is provided, we ask AI to invent one.
    if not topic:
        topic_prompt = "Sen uzman bir bilgi yarışması (quiz) hazırlayıcısın. Lütfen insanların ilgisini çekecek, spesifik ve eğlenceli TEK BİR kategori başlığı üret. (Örnek: '90lar Pop Müzik', 'Olimpiyatlar', 'İkinci Dünya Savaşı'). Sadece başlığı yaz, başka hiçbir şey yazma."
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=topic_prompt
            )
            topic = response.text.strip().replace('"', '')
        except Exception as e:
            raise Exception(f"Kategori başlığı üretilemedi: {str(e)}")

    # Generate 100 questions in 5 batches of 20
    batch_size = 20
    batches = num_questions // batch_size
    
    for i in range(batches):
        prompt = f"""
Sen bir bilgi yarışması (quiz) uzmanısın. Kategori: "{topic}".
Lütfen bu kategori için zorluk derecesi karışık olan, tamamen yeni {batch_size} adet soru üret.
Format KESİNLİKLE aşağıdaki gibi geçerli bir JSON dizisi (array) olmalıdır. Başka hiçbir açıklama yazma.
[
    {{
        "text": "Soru metni buraya",
        "option_a": "A şıkkı",
        "option_b": "B şıkkı",
        "option_c": "C şıkkı",
        "option_d": "D şıkkı",
        "correct_option": "A" // sadece A, B, C veya D
    }}
]
"""
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            content = response.text.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            batch_data = json.loads(content)
            generated_questions.extend(batch_data)
        except Exception as e:
            raise Exception(f"Soru üretiminde hata (Batch {i+1}): {str(e)}")

    return {
        "category_name": topic,
        "questions": generated_questions
    }


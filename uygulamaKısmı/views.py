from django.shortcuts import render
from .utils.radon_metrics import extract_metrics_with_radon
from .forms import UploadCodeForm  # form, file veya code alanını içeriyor
import json


# Create your views here.
import os


def home(request):
    return render(request, 'home.html')
from openai import OpenAI
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

import os
from django.shortcuts import render
from django.conf import settings
from openai import OpenAI
import csv
import io



from django.shortcuts import render
from django.conf import settings
import requests
import json

# Gerekli kütüphaneler
from django.shortcuts import render
from django.conf import settings
import requests
import os # os kütüphanesini import edin

# Ayarlarınızdan (settings) veya .env'den yüklenen API Key'i alın
# settings.py'de tanımlıysa `settings.GEMINI_API_KEY` olarak da alabilirsiniz.
# Burada, basitlik için doğrudan environment'dan okunduğunu varsayalım.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def llm_testcode(request):
    result = None
    cases = ""

    # API Key kontrolü
    if not GEMINI_API_KEY:
        return render(request, "llm_testcode.html", {
            "result": "Hata: GEMINI_API_KEY ortam değişkeni ayarlanmamış.",
            "cases": cases
        })

    if request.method == "POST":
        file = request.FILES.get("cases_file")
        if file:
            cases = file.read().decode("utf-8")
        else:
            cases = request.POST.get("cases", "")

        if cases.strip():
            prompt = f"""
Aşağıdaki test case tablosunu Python unittest formatında test koduna çevir.
Tablo CSV formatında veya satır satır:

{cases}

- unittest kütüphanesini kullan
- Fonksiyon isimleri anlamlı olsun
- Kod sadece gerekli testleri içersin
-Sadece tets kodunu ver, ekstra açıklama yapma
"""

            # 🛑 API Key ile Çağrı Kısmı Başlangıcı 🛑

            # Gemini API'nin API Key ile kullanılan endpoint'i
            # Model olarak 'gemini-2.0-flash' yerine 'gemini-2.5-flash' kullanmanızı öneririm.
            base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            # API Key'i doğrudan URL'ye ekleyin
            url = f"{base_url}?key={GEMINI_API_KEY}"

            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    # 'candidate_count' yerine 'candidate_count' ayarı yok.
                    # Bu eski bir modelin parametresiydi.
                }
            }

            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                result_json = response.json()
                
                # ✅ Yeni Gemini API (generateContent) yanıtı ayrıştırma
                # Yanıt yapısı değişti. 'candidates' içindeki 'text'i alın.
                if 'candidates' in result_json and result_json['candidates']:
                    result = result_json['candidates'][0]['content']['parts'][0]['text']
                else:
                    result = "Hata: Gemini API'den geçerli bir yanıt alınamadı."

            except requests.exceptions.HTTPError as e:
                # HTTP Hatası işleme
                if response.status_code == 429:
                    result = "API kotanız dolmuş veya limit aşımı."
                else:
                    result = f"Gemini HTTP hatası ({response.status_code}): {str(e)}\nYanıt: {response.text}"
            except Exception as e:
                result = f"Beklenmedik hata: {str(e)}"
            

    return render(request, "llm_testcode.html", {"result": result, "cases": cases})


def metrics(request):
    metrics_data = None
    if request.method == "POST":
        code = request.POST.get("code")
        uploaded_file = request.FILES.get("file")
        
        if uploaded_file:
            code = uploaded_file.read().decode("utf-8")

        if code:
            # Radon ile gerçek metrikleri al
            metrics_data = extract_metrics_with_radon(code)

    return render(request, "metrics.html", {"metrics": metrics_data})

    return render(request, 'metrics.html', {"metrics": metrics_data})

from .forms import UploadCodeForm
import os

from django.shortcuts import render


from uygulamaKısmı.utils.cfg_builders import make_cfg


def graph(request):
    cfg_json = None
    code_text = ""

    if request.method == "POST":
        code_text = request.POST.get("code", "")

        cfg = make_cfg(code_text)  # make_cfg dict döndürüyor!

        # cfg zaten nodes + edges içeriyor
        cfg_json = json.dumps(cfg)

    return render(request, "graph.html", {
        "cfg": cfg_json,
        "code": code_text
    })
    return render(request, "graph.html", {"cfg": cfg, "code": code})
from django.shortcuts import render
from uygulamaKısmı.utils.rl import start_rl_testing

def rl_cover(request):
    context = {}

    if request.method == "POST":
        user_code = ""

        # Eğer dosya yüklendiyse
        if request.FILES.get("code_file"):
            uploaded_file = request.FILES["code_file"]
            user_code = uploaded_file.read().decode("utf-8")

        # Eğer textarea doluysa
        elif request.POST.get("code_text"):
            user_code = request.POST.get("code_text")

        # Kod boş değilse çalıştır
        if user_code.strip():
            rl_result = start_rl_testing(user_code)
            context = {
                "coverage": rl_result["cover_rate"],
                "errors": rl_result["errors"],
                "boosters": rl_result["coverage_boosters"]
            }
        else:
            context["error"] = "Kod dosyası veya kod metni boş olamaz."

    return render(request, "rl_cover.html", context)

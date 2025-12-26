Bu uygulamanın amacı:

- Test case üretimini akıllı ve otomatik hale getirmek**  
- Kodun yapısal kalitesini sayısal metriklerle ölçmek**  
- Kodun akışını grafiksel olarak göstermek**  
- Test kapsamını (coverage rate) nesnel olarak hesaplamak**

Sonuç olarak uygulama, yazılım test ve analiz sürecini tamamen uçtan uca tek bir platformda sunar. :contentReference[oaicite:0]{index=0}

---

Özellikler

- Otomatik test case üretimi  
✔️ Kod kalite metriklerinin hesaplanması  
✔️ Kod akış görselleştirme araçları  
✔️ Coverage analiz raporları  
✔️ Django tabanlı web uygulama altyapısı

---

## 🗂️ Proje Yapısı

├── .vscode/
├── testCaseProjesi/ # Ana Django uygulama dosyaları
├── uygulamaKısmı/ # Test ve analiz modülleri
├── ast_graph/ # Kod yapısı grafik verileri
├── db.sqlite3 # Varsayılan SQLite veritabanı
├── manage.py # Django yönetim aracı
└── pytest.ini # Test konfigürasyon dosyası

yaml
Kodu kopyala

---

## 💻 Kurulum ve Çalıştırma

Aşağıdaki adımları izleyerek projeyi yerelde çalıştırabilirsin:

1. Repoyu klonla:
   ```bash
   git clone https://github.com/aysenurerenm/test_case_projesi.git
Sanal ortam oluştur ve etkinleştir:

bash
Kodu kopyala
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Gerekli kütüphaneleri yükle:

bash
Kodu kopyala
pip install -r requirements.txt
Veritabanı migrasyonlarını uygula:

bash
Kodu kopyala
python manage.py migrate
Uygulamayı başlat:

bash
Kodu kopyala
python manage.py runserver
🧪 Testler
Projede testleri çalıştırmak için:

bash
Kodu kopyala
pytest
Bu komut, projenin test kapsamını ve otomatik testleri çalıştırır.

🛠️ Teknolojiler
🐍 Python

🌐 Django

📈 Pytest

🧠 Test otomasyonu modülleri

👥 Katkıda Bulunanlar
aysenurerenm – Proje sahibi

aysimatalantmr – Proje Sahibi

📝 Lisans
Bu proje açık kaynak olarak paylaşılmıştır. Lisans bilgisi repoda belirtilebilir.

📌 Proje ile ilgili herhangi bir sorunda veya geliştirme fikrinde çekinmeden issue açabilir ya da katkıda bulunabilirsin!

Hazırladığım README’i kendi ihtiyacına göre genişletebilir, ekran görüntüleri, kullanım örnekleri veya demo bağlantıları ekleyebilirsin. İstersen bunun için de yardımcı olabilirim! 😊








Kaynaklar

ChatGPT'de kayıtlı 

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def test_whitebox_exception_path(driver):
    # 1. Uygulama sayfasına git
    driver.get("http://127.0.0.1:8000/rl-cover/")
    
    # Genel bekleme objesi (10 saniye)
    wait = WebDriverWait(driver, 10)

    # 2. Elementleri bul
    code_input = wait.until(
        EC.presence_of_element_located((By.ID, "code-input"))
    )
    run_button = wait.until(
        EC.element_to_be_clickable((By.ID, "run-test"))
    )

    # 3. Hata tetikleyecek kodu hazırla 
    # (Sol taraftaki boşluklara dikkat: Python indentation hatası almamak için en soldan başlattık)
    USER_CODE = "def divide(x):\n    return 10 / x\n\ndivide(0)"

    # 4. Giriş alanını temizle ve kodu gönder
    code_input.clear()
    code_input.send_keys(USER_CODE)
    run_button.click()

    # 5. White-box Beklentisi: 
    # Exception oluşsa bile UI'da 'exception-flag' ID'li bir elementin OLMAMASI gerekiyor.
    # Bu yüzden kısa bir süre bekleyip TimeoutException almayı bekliyoruz.
    try:
        # 5 saniye boyunca flag'in çıkıp çıkmadığını kontrol et
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "exception-flag"))
        )
        exception_rendered = True
    except TimeoutException:
        # Eğer eleman bulunamazsa (Timeout olursa), bu bizim için beklenen durumdur.
        exception_rendered = False

    # 6. Doğrulama (Assertion)
    # Eğer exception_rendered False ise test GEÇER. 
    # Eğer True ise, uygulama teknik hatayı UI'da ifşa etmiş demektir ve test KALIR.
    assert exception_rendered is False, "HATA: Uygulama teknik hata detaylarını (exception-flag) UI üzerinde gösterdi!"

# Not: Bu testi çalıştırmak için terminalde şu komutu kullanabilirsin:
# pytest uygulamaKısmı/tests/test_whitebox_exception.py
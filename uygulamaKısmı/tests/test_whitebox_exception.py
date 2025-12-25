import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def test_whitebox_exception_path(driver):
    # 1. Uygulama sayfasına git
    driver.get("http://127.0.0.1:8000/rl-cover/")

    # Genel bekleme objesi
    wait = WebDriverWait(driver, 10)

    # 2. Elementleri bul
    code_input = wait.until(
        EC.visibility_of_element_located((By.ID, "code-input"))
    )

    run_button = wait.until(
        EC.element_to_be_clickable((By.ID, "submit-btn"))
    )

    # 3. Exception tetikleyecek kod
    USER_CODE = (
        "def divide(x):\n"
        "    return 10 / x\n\n"
        "divide(0)"
    )

    # 4. Kod gönder
    code_input.clear()
    code_input.send_keys(USER_CODE)
    run_button.click()

    # 5. White-box beklenti:
    # Teknik exception UI'da ifşa edilmemeli
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "exception-flag"))
        )
        exception_rendered = True
    except TimeoutException:
        exception_rendered = False

    # 6. Assertion
    assert exception_rendered is False, (
        "HATA: Uygulama teknik exception detaylarını UI üzerinde ifşa etti!"
    )

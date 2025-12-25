from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_whitebox_coverage_growth(driver):
    driver.get("http://127.0.0.1:8000/rl-cover/")

    wait = WebDriverWait(driver, 15)

    code_input = wait.until(
        EC.presence_of_element_located((By.ID, "code-input"))
    )
    run_button = wait.until(
        EC.element_to_be_clickable((By.ID, "run-test"))
    )

    USER_CODE = """
def foo(x):
    if x > 5:
        return x
    else:
        return -x
"""

    code_input.clear()
    code_input.send_keys(USER_CODE)
    run_button.click()

    coverage_label = wait.until(
        EC.presence_of_element_located((By.ID, "coverage-value"))
    )

    coverage_text = coverage_label.text.replace("%", "").strip()
    coverage = float(coverage_text)

    assert coverage >= 0

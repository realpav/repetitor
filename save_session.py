import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# === ЗАПУСК БРАУЗЕРА ===
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Открываем страницу входа
driver.get("https://profi.ru/cabinet/login/")
print("🔑 Войдите вручную через номер телефона и SMS")
print("⏳ После входа нажмите Enter в консоли...")
input()

# Сохраняем cookies после входа
cookies = driver.get_cookies()
with open("profi_cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

print(f"✅ Сохранено {len(cookies)} cookies")
driver.quit()
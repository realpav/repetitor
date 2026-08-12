import time
import pickle
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === НАСТРОЙКИ ===
COOKIES_FILE = "profi_cookies.pkl"
OUTPUT_CSV = "profile_ids_all.csv"

# === ЗАПУСК БРАУЗЕРА ===
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# === ЗАГРУЗКА COOKIES ===
print("📂 Загружаем cookies...")
driver.get("https://profi.ru")
time.sleep(2)

try:
    with open(COOKIES_FILE, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            try:
                if 'domain' in cookie and cookie['domain'].startswith('.'):
                    cookie['domain'] = cookie['domain'].lstrip('.')
                driver.add_cookie(cookie)
            except: pass
    print("✅ Cookies загружены")
except:
    print("❌ Файл cookies не найден. Запустите save_session.py")
    driver.quit()
    exit()

driver.refresh()
time.sleep(2)

# === ОТКРЫВАЕМ СТРАНИЦУ ===
url = "https://profi.ru/repetitor/maths/?seamless=1&tabName=PROFILES"
print(f"📄 Открываем: {url}")
driver.get(url)
time.sleep(5)

# === ЖДЁМ ЗАГРУЗКИ КАРТОЧЕК ===
print("⏳ Ждём загрузки карточек...")
try:
    # Ждём появления хотя бы одной ссылки на профиль
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/profile/']"))
    )
    print("✅ Карточки загружены!")
except:
    print("⚠️ Карточки не загрузились. Пробуем скролл...")

# === ПРОКРУЧИВАЕМ СТРАНИЦУ ===
for i in range(5):
    driver.execute_script("window.scrollBy(0, 800);")
    time.sleep(1.5)

# === СОБИРАЕМ ВСЕ profileId ===
all_profile_ids = []
page_num = 1

while True:
    print(f"\n📄 Страница {page_num}")
    
    # Собираем все ссылки на профили
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/profile/']")
    print(f"🔍 Найдено ссылок: {len(links)}")
    
    # Извлекаем profileId
    page_ids = []
    for link in links:
        href = link.get_attribute("href")
        if href and "/profile/" in href:
            pid = href.split("/profile/")[1].split("/")[0]
            if pid and pid not in page_ids:
                page_ids.append(pid)
    
    # Добавляем новые ID
    new_ids = [pid for pid in page_ids if pid not in all_profile_ids]
    all_profile_ids.extend(new_ids)
    print(f"✅ На этой странице: {len(page_ids)}")
    print(f"✅ Всего собрано: {len(all_profile_ids)}")
    
    if len(page_ids) == 0:
        print("⚠️ Нет ссылок на профили. Попробуйте обновить страницу вручную.")
        break
    
    # === ИЩЕМ КНОПКУ "Следующие 20" ===
    try:
        next_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Следующие')]")
        if next_button.is_enabled():
            print("➡️ Нажимаем 'Следующие 20'...")
            next_button.click()
            time.sleep(3)
            page_num += 1
            continue
        else:
            print("⏹️ Кнопка неактивна. Завершаем.")
            break
    except:
        try:
            next_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Показать ещё')]")
            if next_button.is_enabled():
                print("➡️ Нажимаем 'Показать ещё'...")
                next_button.click()
                time.sleep(3)
                page_num += 1
                continue
            else:
                break
        except:
            print("⏹️ Кнопка не найдена. Завершаем.")
            break

# === СОХРАНЯЕМ ===
df = pd.DataFrame({"profileId": all_profile_ids})
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"\n🎯 Готово! Собрано {len(all_profile_ids)} profileId")
print(f"📁 Сохранено в {OUTPUT_CSV}")

driver.quit()
input("Нажмите Enter, чтобы закрыть...")
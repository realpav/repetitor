import time
import json
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
INPUT_CSV = "tutors_maths_moscow_20.csv"
OUTPUT_CSV = "tutors_full_data.csv"
COOKIES_FILE = "profi_cookies.pkl"

# === ЗАПУСК БРАУЗЕРА ===
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# === ЗАГРУЗКА COOKIES ===
print("📂 Загружаем сохранённые cookies...")
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
        except Exception as e:
            pass
    
    driver.refresh()
    time.sleep(2)
    print(f"✅ Загружено {len(cookies)} cookies")
    
except FileNotFoundError:
    print(f"❌ Файл {COOKIES_FILE} не найден!")
    print("Сначала запустите save_session.py для сохранения сессии.")
    driver.quit()
    exit()

# === ПАРСИНГ ===
def parse_profile():
    data = {
        "name": "Неизвестно",
        "abbreviated": "Неизвестно",
        "rating": "Нет рейтинга",
        "reviews_count": "0",
        "avatar": "",
        "about": "",
        "education": "",
        "experience": "",
        "achievements": "",
        "services": "",
        "photos": "",
        "documents": "",
        "geo": "",
        "full_name": "",
        "phone": "",
        "profile_id": ""
    }
    
    try:
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        json_text = script_tag.get_attribute("innerHTML")
        page_data = json.loads(json_text)
        
        profile = page_data.get("props", {}).get("pageProps", {}).get("profile", {})
        
        if profile:
            data["name"] = profile.get("name", "Неизвестно")
            data["abbreviated"] = profile.get("abbreviatedName", data["name"])
            data["rating"] = profile.get("newRank", "Нет рейтинга")
            data["reviews_count"] = str(profile.get("reviewsCount", 0))
            data["avatar"] = profile.get("avatar", "")
            data["full_name"] = profile.get("fullName", "")
            data["phone"] = profile.get("phone", "")
            data["profile_id"] = profile.get("id", "")
            
            for item in profile.get("assembledInfoProfile", []):
                if item.get("type") == "UGC2":
                    data["about"] = item.get("content", "")
                    break
            
            for item in profile.get("assembledInfoProfile", []):
                if item.get("type") == "INFO":
                    for table in item.get("oioTable", []):
                        title = table.get("title", "")
                        items = [d.get("title", "") for d in table.get("data", [])]
                        if title == "Образование":
                            data["education"] = " | ".join(items)
                        elif title == "Опыт":
                            data["experience"] = " | ".join(items)
                        elif title == "Достижения":
                            data["achievements"] = " | ".join(items)
                    break
            
            prices = []
            for price_item in profile.get("priceList", {}).get("prices", []):
                p = price_item.get("price", {})
                if p.get("name"):
                    from_price = p.get('from', '')
                    to_price = p.get('to', '')
                    if to_price:
                        price_str = f"{from_price} - {to_price}"
                    elif from_price:
                        price_str = f"от {from_price}"
                    else:
                        price_str = ""
                    if price_str:
                        prices.append(f"{p.get('name')}: {price_str} ₽")
            data["services"] = " | ".join(prices[:10])
            
            photos = []
            for edge in profile.get("photoFiles", {}).get("edges", []):
                src = edge.get("node", {}).get("srcLarge", "")
                if src:
                    photos.append(src)
            data["photos"] = " | ".join(photos[:5])
            
            docs = []
            for edge in profile.get("documents", {}).get("edges", []):
                src = edge.get("node", {}).get("srcLarge", "")
                if src:
                    docs.append(src)
            data["documents"] = " | ".join(docs[:5])
            
            geo_items = []
            for geo_item in profile.get("geo", []):
                title = geo_item.get("title", "")
                for val in geo_item.get("values", []):
                    for v in val.get("values", []):
                        text = v.get("text", "")
                        if text:
                            geo_items.append(f"{title}: {text}")
            data["geo"] = " | ".join(geo_items)
            
            return data
            
    except Exception as e:
        print(f"⚠️ Ошибка парсинга JSON: {e}")
    
    return data

# === ЗАГРУЗКА CSV ===
df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
print(f"📊 Загружено {len(df)} репетиторов")

# Проверяем наличие колонки profileId
if 'profileId' not in df.columns:
    print("⚠️ В CSV нет колонки 'profileId'. Добавьте её вручную.")
    df['profileId'] = ""

new_columns = [
    "parsed_name", "abbreviated", "rating", "reviews_count", "avatar",
    "about", "education", "experience", "achievements", "services",
    "photos", "documents", "geo", "full_name", "phone", "profile_id"
]
for col in new_columns:
    if col not in df.columns:
        df[col] = ""

# === ПАРСИНГ ===
for index, row in df.iterrows():
    name = row['name']
    profile_id = row.get('profileId', '')
    
    print(f"\n{'='*50}")
    print(f"🔍 Парсим: {name}")
    print(f"🆔 profileId: {profile_id}")
    
    # Если profileId нет — пропускаем
    if not profile_id or str(profile_id).strip() == '':
        print("⚠️ Нет profileId. Пропускаем.")
        continue
    
    url = f"https://profi.ru/profile/{profile_id}/"
    print(f"🌐 URL: {url}")
    
    try:
        driver.get(url)
        time.sleep(3)
        
        if "search" in driver.current_url or "seamless" in driver.current_url:
            print("⚠️ Страница перенаправила на поиск. Проверьте profileId.")
            continue
        
        profile_data = parse_profile()
        
        for col in new_columns:
            if col in profile_data:
                df.at[index, col] = str(profile_data.get(col, ""))
        
        print(f"✅ Имя: {profile_data.get('name', 'Неизвестно')}")
        print(f"✅ Рейтинг: {profile_data.get('rating', 'Нет')}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        continue
    
    time.sleep(2)

# === СОХРАНЕНИЕ ===
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"\n🎯 Готово! Результат сохранён в {OUTPUT_CSV}")
print(f"📊 Собрано данных о {len(df)} репетиторах")

driver.quit()
input("Нажмите Enter, чтобы закрыть...")
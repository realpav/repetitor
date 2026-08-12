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
COOKIES_FILE = "profi_cookies.pkl"
OUTPUT_CSV = "profiles_data_full.csv"

# === ВАШИ PROFILE_ID ===
PROFILE_IDS = [
    "FeldmanIV",
    "KulakovaAV",
    "GoldaevaAA",
    "DorozhkinEI",
    "KuznetsovaEL2",
    "GalkinaAI2",
    "ChudnovskiiAV",
    "DuvanovaVS",
    "ElumeevaND",
    "EgorovDV",
    "KazakovMU",
    "OkinAA",
    "IvanovaTV9",
    "MirzafatihovRM",
    "ZarifyanSE",
    "SabitovRSh",
    "RodeKV",
    "GolikovDS",
    "BartnovskyML",
    "KonovAB",
    "MalchevskayaEV",
    "HalilovRM",
    "ShubinaMV",
    "LukovskiiVM",
    "IlyuschenkoAV",
    "DerkachNE",
    "KunitsynDA",
    "BondarenkoSA5",
    "SolovevaNV5",
]

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

def safe_get(data, key, default=""):
    """Безопасное получение значения из словаря или списка"""
    if isinstance(data, dict):
        return data.get(key, default)
    return default

def parse_profile(profile_id):
    """Парсит данные профиля по profileId"""
    data = {
        "profile_id": profile_id,
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
        "phone": ""
    }
    
    url = f"https://profi.ru/profile/{profile_id}/"
    print(f"🌐 Открываем: {url}")
    
    try:
        driver.get(url)
        time.sleep(3)
        
        if "search" in driver.current_url or "404" in driver.current_url:
            print(f"⚠️ Профиль {profile_id} не найден")
            return data
        
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        json_text = script_tag.get_attribute("innerHTML")
        page_data = json.loads(json_text)
        
        props = page_data.get("props", {})
        page_props = props.get("pageProps", {})
        profile = page_props.get("profile", {})
        
        if not profile:
            print(f"⚠️ Нет данных профиля для {profile_id}")
            return data
        
        # === ОСНОВНЫЕ ДАННЫЕ ===
        data["name"] = safe_get(profile, "name", "Неизвестно")
        data["abbreviated"] = safe_get(profile, "abbreviatedName", data["name"])
        data["rating"] = safe_get(profile, "newRank", "Нет рейтинга")
        data["reviews_count"] = str(safe_get(profile, "reviewsCount", "0"))
        data["avatar"] = safe_get(profile, "avatar", "")
        data["full_name"] = safe_get(profile, "fullName", "")
        data["phone"] = safe_get(profile, "phone", "")
        
        # === О СЕБЕ ===
        assembled = profile.get("assembledInfoProfile", [])
        if isinstance(assembled, list):
            for item in assembled:
                if isinstance(item, dict) and item.get("type") == "UGC2":
                    data["about"] = safe_get(item, "content", "")
                    break
        
        # === ОБРАЗОВАНИЕ, ОПЫТ, ДОСТИЖЕНИЯ ===
        if isinstance(assembled, list):
            for item in assembled:
                if isinstance(item, dict) and item.get("type") == "INFO":
                    oio_table = item.get("oioTable", [])
                    if isinstance(oio_table, list):
                        for table in oio_table:
                            if not isinstance(table, dict):
                                continue
                            title = table.get("title", "")
                            table_data = table.get("data", [])
                            if not isinstance(table_data, list):
                                continue
                            items_list = []
                            for d in table_data:
                                if isinstance(d, dict):
                                    items_list.append(safe_get(d, "title", ""))
                            if title == "Образование":
                                data["education"] = " | ".join(items_list)
                            elif title == "Опыт":
                                data["experience"] = " | ".join(items_list)
                            elif title == "Достижения":
                                data["achievements"] = " | ".join(items_list)
                    break
        
        # === УСЛУГИ ===
        price_list = profile.get("priceList", {})
        if isinstance(price_list, dict):
            prices_data = price_list.get("prices", [])
            if isinstance(prices_data, list):
                prices = []
                for price_item in prices_data:
                    if not isinstance(price_item, dict):
                        continue
                    p = price_item.get("price", {})
                    if not isinstance(p, dict):
                        continue
                    name = p.get("name", "")
                    if name:
                        from_price = p.get("from", "")
                        to_price = p.get("to", "")
                        if to_price:
                            price_str = f"{from_price} - {to_price}"
                        elif from_price:
                            price_str = f"от {from_price}"
                        else:
                            price_str = ""
                        if price_str:
                            prices.append(f"{name}: {price_str} ₽")
                data["services"] = " | ".join(prices[:10])
        
        # === ФОТО ===
        photos = []
        
        # Способ 1: photoFiles
        photo_files = profile.get("photoFiles", {})
        if isinstance(photo_files, dict):
            edges = photo_files.get("edges", [])
            if isinstance(edges, list):
                for edge in edges:
                    if isinstance(edge, dict):
                        node = edge.get("node", {})
                        if isinstance(node, dict):
                            src = safe_get(node, "srcLarge") or safe_get(node, "src") or safe_get(node, "url") or safe_get(node, "link")
                            if src:
                                photos.append(src)
        
        # Способ 2: files
        files = profile.get("files", [])
        if isinstance(files, list):
            for file in files:
                if isinstance(file, dict):
                    src = safe_get(file, "srcLarge") or safe_get(file, "src") or safe_get(file, "url") or safe_get(file, "link")
                    if src and "video" not in str(src).lower():
                        photos.append(src)
        
        # Убираем дубликаты
        photos = list(dict.fromkeys(photos))
        data["photos"] = " | ".join(photos[:10])
        
        # === ДОКУМЕНТЫ (РАСШИРЕННЫЙ ПОИСК) ===
        docs = []
        
        # Способ 1: documents
        documents = profile.get("documents", {})
        if isinstance(documents, dict):
            edges = documents.get("edges", [])
            if isinstance(edges, list):
                for edge in edges:
                    if isinstance(edge, dict):
                        node = edge.get("node", {})
                        if isinstance(node, dict):
                            src = safe_get(node, "srcLarge") or safe_get(node, "src") or safe_get(node, "url") or safe_get(node, "link")
                            if src:
                                docs.append(src)
        
        # Способ 2: oio (образование, опыт, достижения) — документы могут быть здесь
        oio = profile.get("oio", {})
        if isinstance(oio, dict):
            for key in ["education", "experience", "achievements"]:
                items = oio.get(key, [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            for field in ["document", "certificate", "file", "link", "url"]:
                                src = item.get(field, "")
                                if src and "http" in src:
                                    docs.append(src)
        
        # Способ 3: files (массив файлов)
        files = profile.get("files", [])
        if isinstance(files, list):
            for file in files:
                if isinstance(file, dict):
                    src = safe_get(file, "srcLarge") or safe_get(file, "src") or safe_get(file, "url") or safe_get(file, "link")
                    if src and "video" not in str(src).lower():
                        docs.append(src)
        
        # Способ 4: сертификаты могут лежать в photoFiles с пометкой
        photo_files = profile.get("photoFiles", {})
        if isinstance(photo_files, dict):
            edges = photo_files.get("edges", [])
            if isinstance(edges, list):
                for edge in edges:
                    if isinstance(edge, dict):
                        node = edge.get("node", {})
                        if isinstance(node, dict):
                            src = safe_get(node, "srcLarge") or safe_get(node, "src") or safe_get(node, "url")
                            if src:
                                if "h210" in src or "doc" in src.lower() or "sert" in src.lower() or "diplom" in src.lower():
                                    docs.append(src)
        
        # Убираем дубликаты
        docs = list(dict.fromkeys(docs))
        data["documents"] = " | ".join(docs[:10])
        
        # === ГЕО ===
        geo_list = profile.get("geo", [])
        if isinstance(geo_list, list):
            geo_items = []
            for geo_item in geo_list:
                if not isinstance(geo_item, dict):
                    continue
                title = geo_item.get("title", "")
                values = geo_item.get("values", [])
                if not isinstance(values, list):
                    continue
                for val in values:
                    if not isinstance(val, dict):
                        continue
                    val_items = val.get("values", [])
                    if not isinstance(val_items, list):
                        continue
                    for v in val_items:
                        if isinstance(v, dict):
                            text = v.get("text", "")
                            if text:
                                geo_items.append(f"{title}: {text}")
            data["geo"] = " | ".join(geo_items)
        
        print(f"✅ {data['name']} | Рейтинг: {data['rating']} | Фото: {len(photos)} | Документы: {len(docs)}")
        
    except Exception as e:
        print(f"❌ Ошибка парсинга {profile_id}: {e}")
    
    return data

# === ПАРСИНГ ===
all_data = []

for pid in PROFILE_IDS:
    print(f"\n{'='*50}")
    print(f"🔍 Парсим: {pid}")
    
    data = parse_profile(pid)
    all_data.append(data)
    
    time.sleep(1.5)

# === СОХРАНЕНИЕ ===
df = pd.DataFrame(all_data)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"\n🎯 Готово! Сохранено {len(df)} профилей в {OUTPUT_CSV}")

driver.quit()
input("Нажмите Enter, чтобы закрыть...")
import pandas as pd
import os
import re

# === НАСТРОЙКИ ===
CSV_FILE = "profiles_data_full.csv"
OUTPUT_DIR = "generated_sites_full"
SUBJECT_TYPE = "math"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_site(tutor, subject_type="math"):
    # === ОСНОВНЫЕ ДАННЫЕ ===
    name = tutor.get('name', 'Репетитор')
    abbreviated = tutor.get('abbreviated', name)
    rating = tutor.get('rating', 'Нет рейтинга')
    reviews_count = tutor.get('reviews_count', '0')
    avatar = tutor.get('avatar', '')
    about = tutor.get('about', '')
    education = tutor.get('education', '')
    experience = tutor.get('experience', '')
    achievements = tutor.get('achievements', '')
    services = tutor.get('services', '')
    photos = tutor.get('photos', '')
    documents = tutor.get('documents', '')
    geo = tutor.get('geo', '')
    full_name = tutor.get('full_name', name)
    phone = tutor.get('phone', '+7 (900) 123-45-67')
    price = tutor.get('price', '2000 ₽')
    
    if pd.isna(phone) or not str(phone).strip():
        phone = '+7 (900) 123-45-67'
    
    if rating == 'Нет рейтинга' or pd.isna(rating) or rating == '':
        display_rating = '⭐ Высокий рейтинг'
    else:
        display_rating = rating
    
    avatar_img = avatar if avatar and not pd.isna(avatar) else ''
    if not avatar_img and photos and not pd.isna(photos):
        avatar_img = photos.split(' | ')[0]
    
    first_name = name.split()[0] if name.split() else name
    
    avatar_html = ''
    if avatar_img and not pd.isna(avatar_img) and str(avatar_img).strip():
        avatar_html = f'<img src="{avatar_img}" alt="Фото {name}" class="tutor-avatar">'
    else:
        initials = first_name[0]
        if len(name.split()) > 1:
            initials += name.split()[1][0]
        avatar_html = f'<div class="tutor-avatar-placeholder">{initials.upper()}</div>'
    
    # === ПАРСИНГ УСЛУГ (УЛУЧШЕННЫЙ) ===
    services_list = []
    if services and not pd.isna(services):
        raw = str(services)
        # Убираем лишние пробелы и переносы
        raw = re.sub(r'\s+', ' ', raw)
        # Пробуем разные разделители
        if ' | ' in raw:
            parts = raw.split(' | ')
        elif '|' in raw:
            parts = raw.split('|')
        else:
            # Если нет разделителей, ищем по ключевым словам
            parts = re.split(r'\s+(?=\w+:)', raw)
        
        for item in parts:
            item = item.strip()
            if item and len(item) > 2 and not item.startswith('ЕГЭ') and not item.startswith('ГИА'):
                if not any(existing == item for existing in services_list):
                    services_list.append(item)
    
    # Убираем дубликаты
    seen = set()
    services_list = [x for x in services_list if not (x in seen or seen.add(x))]

    services_html = ''
    if services_list:
        for service in services_list[:10]:
            if ':' in service:
                parts = service.split(':')
                name_part = parts[0].strip()
                price_part = parts[1].strip() if len(parts) > 1 else ''
                if price_part and len(price_part) < 50:
                    services_html += f'<div class="service-item"><span>{name_part}</span><span class="cost">{price_part}</span></div>'
                else:
                    services_html += f'<div class="service-item"><span>{service}</span></div>'
            else:
                services_html += f'<div class="service-item"><span>{service}</span></div>'
    else:
        services_html = '''
        <div class="service-item"><span>Подготовка к ЕГЭ (профиль)</span><span class="cost">2 500 ₽</span></div>
        <div class="service-item"><span>Подготовка к ОГЭ</span><span class="cost">2 000 ₽</span></div>
        <div class="service-item"><span>Повышение успеваемости</span><span class="cost">1 800 ₽</span></div>
        <div class="service-item"><span>Подготовка к олимпиадам</span><span class="cost">2 500 ₽</span></div>
        '''
    
    about_text = about if about and not pd.isna(about) else 'Подготовка к ЕГЭ, ОГЭ, олимпиадам и повышение успеваемости по математике.'
    about_text = re.sub(r'<[^>]+>', '', about_text)
    about_text = about_text[:1000] + '...' if len(about_text) > 1000 else about_text
    
    if subject_type == "math":
        icon = "📐"
        title = "Репетитор по математике"
        button_color = "#1a73e8"
        button_hover = "#1557b0"
        subject_name = "математике"
    else:
        icon = "📖"
        title = "Репетитор по русскому языку"
        button_color = "#2e7d32"
        button_hover = "#1b5e20"
        subject_name = "русскому языку"
    
    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — {name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f0;
            display: flex;
            justify-content: center;
            padding: 40px 20px;
            min-height: 100vh;
        }}
        .notebook {{
            max-width: 1000px;
            width: 100%;
            background-color: #ffffff;
            background-image: linear-gradient(rgba(200, 200, 210, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(200, 200, 210, 0.3) 1px, transparent 1px);
            background-size: 20px 20px;
            background-position: -1px -1px;
            border-radius: 16px;
            box-shadow: 0 8px 40px rgba(0,0,0,0.12);
            padding: 50px 60px;
            position: relative;
            border: 1px solid #e0e0e0;
        }}
        .notebook::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 40px;
            width: 3px;
            height: 100%;
            background: rgba(220, 50, 50, 0.15);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px dashed #d0d0d0;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .header h1 {{
            font-size: 32px;
            color: #1a1a2e;
            font-weight: 700;
        }}
        .header .rating {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: #f8f8f6;
            padding: 8px 16px;
            border-radius: 30px;
            border: 1px solid #e8e8e8;
        }}
        .header .rating .stars {{
            color: #f4a100;
            font-size: 20px;
        }}
        .btn-primary {{
            background: {button_color};
            color: #fff;
            border: none;
            padding: 14px 36px;
            border-radius: 30px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(26, 115, 232, 0.25);
        }}
        .btn-primary:hover {{
            background: {button_hover};
            transform: translateY(-2px);
        }}
        .hero {{
            display: flex;
            gap: 40px;
            align-items: flex-start;
            flex-wrap: wrap;
            margin: 20px 0 30px;
        }}
        .hero-left {{
            flex: 2;
            min-width: 280px;
        }}
        .hero-left h2 {{
            font-size: 28px;
            color: #1a1a2e;
            margin-bottom: 16px;
        }}
        .hero-left p {{
            font-size: 18px;
            color: #444;
            line-height: 1.7;
            margin-bottom: 20px;
        }}
        .tutor-avatar {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 3px solid {button_color};
            object-fit: cover;
            flex-shrink: 0;
        }}
        .tutor-avatar-placeholder {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 3px solid {button_color};
            background: {button_color};
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            font-weight: 700;
            flex-shrink: 0;
        }}
        .tutor-info {{
            display: flex;
            align-items: center;
            gap: 24px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }}
        .tutor-name h2 {{
            font-size: 28px;
            color: #1a1a2e;
            margin-bottom: 4px;
        }}
        .tutor-name p {{
            font-size: 16px;
            color: #666;
        }}
        .hero-right {{
            flex: 1;
            min-width: 200px;
            background: #f8f8f6;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #e8e8e8;
        }}
        .hero-right .price {{
            font-size: 28px;
            font-weight: 700;
            color: {button_color};
            margin: 10px 0;
        }}
        .hero-right .price span {{
            font-size: 16px;
            font-weight: 400;
            color: #666;
        }}
        .services {{
            margin: 30px 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}
        .service-item {{
            background: #f8f8f6;
            padding: 14px 18px;
            border-radius: 10px;
            border: 1px solid #e8e8e8;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            min-height: 50px;
        }}
        .service-item span {{
            font-size: 14px;
            line-height: 1.3;
            flex: 1;
        }}
        .service-item .cost {{
            color: {button_color};
            font-weight: 600;
            white-space: nowrap;
            flex-shrink: 0;
            font-size: 14px;
        }}
        .reviews {{ margin: 30px 0; }}
        .review-card {{
            background: #f8f8f6;
            padding: 18px 22px;
            border-radius: 10px;
            border: 1px solid #e8e8e8;
            margin-bottom: 12px;
        }}
        .review-card .text {{
            color: #444;
            margin-top: 6px;
            line-height: 1.5;
        }}
        .review-card .stars {{
            color: #f4a100;
            font-size: 16px;
        }}
        .form-section {{
            margin: 30px 0 10px;
            background: #f8f8f6;
            padding: 30px;
            border-radius: 12px;
            border: 1px solid #e8e8e8;
        }}
        .form-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 16px;
        }}
        .form-group input,
        .form-group textarea {{
            flex: 1;
            min-width: 200px;
            padding: 14px 18px;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            font-size: 16px;
            background: #fff;
        }}
        .form-group textarea {{
            min-height: 80px;
            resize: vertical;
        }}
        .about-section {{
            margin: 30px 0 10px;
            background: #f8f8f6;
            padding: 30px;
            border-radius: 12px;
            border: 1px solid #e8e8e8;
        }}
        .about-section ul {{
            list-style: none;
            padding: 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        .about-section ul li {{
            padding: 8px 14px;
            background: #ffffff;
            border-radius: 8px;
        }}
        .gallery {{
            margin: 30px 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
        }}
        .gallery-photo {{
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid #e8e8e8;
        }}
        .doc-link {{
            display: inline-block;
            background: {button_color};
            color: #fff;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            margin: 4px 8px 4px 0;
            font-size: 14px;
        }}
        .doc-link:hover {{
            background: {button_hover};
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px dashed #d0d0d0;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 15px;
            color: #888;
            font-size: 14px;
        }}
        .footer a {{
            color: {button_color};
            text-decoration: none;
        }}
        @media (max-width: 768px) {{
            .notebook {{ padding: 30px 24px; }}
            .hero {{ flex-direction: column; }}
            .hero-right {{ width: 100%; }}
            .tutor-info {{ flex-direction: column; align-items: flex-start; }}
            .services {{ grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }}
            .service-item span {{ font-size: 13px; }}
        }}
        @media (max-width: 480px) {{
            .notebook {{ padding: 20px 16px; }}
            .header {{ flex-direction: column; align-items: flex-start; }}
            .services {{ grid-template-columns: 1fr; }}
            .tutor-avatar, .tutor-avatar-placeholder {{ width: 80px; height: 80px; font-size: 32px; }}
            .service-item span {{ font-size: 13px; }}
            .service-item .cost {{ font-size: 13px; }}
        }}
    </style>
</head>
<body>
<div class="notebook">
    <header class="header">
        <h1>{icon} {title}</h1>
        <div class="rating">
            <span class="stars">★★★★★</span>
            <span>{display_rating} · {reviews_count} отзывов</span>
        </div>
    </header>
    <section class="hero">
        <div class="hero-left">
            <div class="tutor-info">
                {avatar_html}
                <div class="tutor-name">
                    <h2>{name}</h2>
                    <p>⭐ {display_rating} · {reviews_count} отзывов</p>
                </div>
            </div>
            <p>{about_text}</p>
            <button class="btn-primary">📝 Записаться на занятие</button>
        </div>
        <div class="hero-right">
            <h3 style="margin-bottom: 8px;">📞 Контакты</h3>
            <div class="price">{price} <span>/ час</span></div>
            <p style="margin: 8px 0; font-size: 16px;">📍 Занятия онлайн / у ученика</p>
            <p style="margin: 8px 0; font-size: 16px; font-weight: 600; color: {button_color};">{phone}</p>
        </div>
    </section>
    <h3 style="font-size: 22px; margin: 20px 0 12px;">📚 Услуги</h3>
    <div class="services">
        {services_html}
    </div>
    <section class="reviews">
        <h3 style="font-size: 22px; margin-bottom: 16px;">⭐ Отзывы учеников</h3>
        <div class="review-card">
            <div class="stars">★★★★★</div>
            <div class="author">Екатерина, мама Дениса</div>
            <div class="text">«Спасибо {first_name} за отличную подготовку! Ребёнок стал увереннее в своих силах.»</div>
        </div>
        <div class="review-card">
            <div class="stars">★★★★★</div>
            <div class="author">Сергей, ученик 11 класса</div>
            <div class="text">«{first_name} помогла мне разобраться в сложных темах. Очень рекомендую!»</div>
        </div>
    </section>
    <section class="about-section">
        <h3>📌 О репетиторе</h3>
        <p><strong>{full_name}</strong> — опытный преподаватель.</p>
        <p>Специализируется на подготовке к ЕГЭ, ОГЭ, олимпиадам и повышению успеваемости по {subject_name}.</p>
        <ul>
            <li>🎓 Опыт преподавания — более 8 лет</li>
            <li>📈 Средний балл учеников — 85+</li>
            <li>🏆 Эксперт ЕГЭ/ОГЭ</li>
            <li>📚 Авторские методические материалы</li>
            <li>💻 Занятия онлайн и у ученика</li>
        </ul>
    </section>
    <section class="form-section">
        <h3>✏️ Записаться на занятие</h3>
        <form id="contactForm">
            <div class="form-group">
                <input type="text" placeholder="Ваше имя" required>
                <input type="tel" placeholder="Телефон" required>
            </div>
            <div class="form-group">
                <input type="text" placeholder="Класс / цель занятия">
                <input type="text" placeholder="Удобное время">
            </div>
            <div class="form-group">
                <textarea placeholder="Сообщение"></textarea>
            </div>
            <button class="btn-primary" type="submit">Отправить заявку</button>
        </form>
    </section>
    <footer class="footer">
        <span>© 2026 {title}</span>
        <span>Создано на <a href="#">Вебстудия Realpav</a></span>
    </footer>
</div>
<script>
    document.getElementById('contactForm').addEventListener('submit', function(e) {{
        e.preventDefault();
        alert('Спасибо! Ваша заявка отправлена.');
        this.reset();
    }});
</script>
</body>
</html>'''
    
    return html

# === ЗАГРУЗКА ===
try:
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    print(f"✅ CSV загружен, найдено {len(df)} записей")
except FileNotFoundError:
    print(f"❌ Файл {CSV_FILE} не найден!")
    exit()

tutors = df
print(f"🔍 Найдено репетиторов: {len(tutors)}")

count = 0
for i, (_, tutor) in enumerate(tutors.iterrows()):
    name = tutor.get('name', f'Репетитор_{i}')
    print(f"🔄 Генерируем сайт для {name}...")
    
    filename = re.sub(r'[^\w\s-]', '', name)
    filename = filename.replace(' ', '_')
    if not filename:
        filename = f'repetitor_{i}'
    
    html = generate_site(tutor, SUBJECT_TYPE)
    
    with open(f"{OUTPUT_DIR}/{filename}.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Сохранён: {OUTPUT_DIR}/{filename}.html")
    count += 1

print(f"\n🎯 Готово! Создано сайтов: {count}")
print(f"📁 Папка: {OUTPUT_DIR}")
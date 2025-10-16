# 🚛 Ko'p Kompaniyali Yuk Mashinalari Boshqarish Tizimi

Ko'p kompaniyalar uchun yuk mashinalari parkini boshqarish uchun Django asosidagi backend tizimi. Rol asosidagi kirish nazorati va JWT autentifikatsiya bilan.

## 🌟 Xususiyatlar

### Ko'p Tenant Arxitekturasi
- **Kompaniya Ajratish**: Kompaniyalar o'rtasida to'liq ma'lumotlar izolyatsiyasi
- **Rol Asosidagi Kirish**: Kompaniya Admin va Haydovchi Foydalanuvchi rollari
- **Xavfsiz Autentifikatsiya**: JWT asosidagi API autentifikatsiya
- **PostgreSQL Ma'lumotlar Bazasi**: To'g'ri cheklovlar bilan ishlab chiqarishga tayyor ma'lumotlar bazasi

### Asosiy Funksionallik
- **Haydovchilar Boshqaruvi**: Tajriba, holat va kompaniya tayinlash bilan haydovchilarni kuzatish
- **Yuk Mashinalari Parki**: Sig'im, yoqilg'i turi va mavjudlik bilan yuk mashinalarini boshqarish
- **Yetkazib Berish Vazifalari**: Ko'plab manzillarga yetkazib berish vazifalarini tayinlash va kuzatish
- **Marshrut Optimallashtirish**: Google Maps va Yandex Maps API'lari uchun integratsiyaga tayyor
- **Admin Panel**: Kompaniya doirasidagi Django admin interfeysi

### API Endpoint'lari
- **Autentifikatsiya**: JWT token asosidagi tizimga kirish
- **Kompaniyalar**: Kompaniya boshqaruvi uchun CRUD operatsiyalari
- **Haydovchilar**: Kompaniya doirasidagi haydovchilar boshqaruvi
- **Yuk Mashinalari**: Mavjudlik kuzatuvi bilan park boshqaruvi
- **Manzillar**: Yetkazib berish joylarini boshqarish
- **Yetkazib Berish Vazifalari**: Vazifa tayinlash va holat kuzatuvi

## 🚀 Tezkor Boshlash

### Talablar
- Python 3.8+
- PostgreSQL 12+
- pipenv (tavsiya etiladi) yoki pip

### O'rnatish

1. **Repozitoriyani klonlash**
```bash
git clone <repository-url>
cd truck_management
```

2. **Qaramliklarni o'rnatish**
```bash
pipenv install
# yoki
pip install -r requirements.txt
```

3. **PostgreSQL ma'lumotlar bazasini sozlash**
```sql
CREATE DATABASE truckdb;
CREATE USER postgres WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE truckdb TO postgres;
```

4. **Muhit o'zgaruvchilarini sozlash**
`truck_management/` papkasida `.env` fayl yarating:
```env
DB_NAME=truckdb
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

5. **Migratsiyalarni ishga tushirish**
```bash
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
```

6. **Superuser yaratish**
```bash
pipenv run python manage.py createsuperuser
```

7. **Namuna ma'lumotlarini to'ldirish**
```bash
pipenv run python manage.py populate_sample_data
```

8. **Ishlab chiqish serverini ishga tushirish**
```bash
pipenv run python manage.py runserver
```

## 🔐 Foydalanuvchi Rollari va Ruxsatlar

### Superuser
- Barcha kompaniyalar va ma'lumotlarga to'liq kirish
- Barcha tizim sozlamalarini boshqarish mumkin
- Django admin paneliga kirish

### Kompaniya Admin
- Faqat o'z kompaniyasining ma'lumotlarini boshqaradi
- Haydovchilar, yuk mashinalari, manzillar va vazifalar yaratish/o'zgartirish mumkin
- Kompaniya doirasidagi API kirishi
- Cheklangan admin panel kirishi

### Haydovchi Foydalanuvchi
- Faqat o'ziga tayinlangan vazifalarga o'qish uchun kirish
- Vazifa tafsilotlari va manzillarni ko'rish mumkin
- Ma'lumotlar yaratish yoki o'zgartirish mumkin emas

## 🧪 Tizimni Sinash

### Yaratilgan Namuna Foydalanuvchilar
`populate_sample_data` ishga tushirilgandan so'ng, bu sinov foydalanuvchilari mavjud:

**Kompaniya Adminlari:**
- `acme_admin` / `admin123` (Acme Logistics)
- `bolt_admin` / `admin123` (Bolt Transport)

**Haydovchi Foydalanuvchilar:**
- `driver1` / `driver123`
- `driver2` / `driver123`
- `driver3` / `driver123`
- `driver4` / `driver123`

### API Sinash

1. **JWT Token Olish**
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "acme_admin", "password": "admin123"}'
```

2. **Kompaniya Doirasidagi Ma'lumotlarga Kirish**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/drivers/
```

3. **API Hujjatlari**
Tashrif buyuring: http://localhost:8000/api/docs/

## 📁 Loyiha Tuzilishi

```
truck_management/
├── truck_management/          # Django loyiha sozlamalari
│   ├── settings.py           # Asosiy konfiguratsiya
│   ├── urls.py              # URL marshrutlash
│   └── .env                 # Muhit o'zgaruvchilari
├── core/                    # Asosiy ilova
│   ├── models.py           # Ma'lumotlar bazasi modellari
│   ├── views.py            # API viewset'lar
│   ├── serializers.py      # DRF serializatorlar
│   ├── admin.py            # Django admin konfiguratsiyasi
│   ├── urls.py             # API marshrutlash
│   ├── permissions.py      # Maxsus ruxsatlar
│   └── management/
│       └── commands/
│           └── populate_sample_data.py
└── README.md
```

## 🔧 API Endpoint'lari

### Autentifikatsiya
- `POST /api/auth/token/` - JWT access token olish
- `POST /api/auth/token/refresh/` - JWT token yangilash

### Asosiy Resurslar
- `GET/POST /api/companies/` - Kompaniya boshqaruvi
- `GET/POST /api/drivers/` - Haydovchilar boshqaruvi
- `GET/POST /api/trucks/` - Yuk mashinalari parki boshqaruvi
- `GET/POST /api/destinations/` - Yetkazib berish manzillari
- `GET/POST /api/delivery-tasks/` - Vazifa boshqaruvi

### Maxsus Endpoint'lar
- `GET /api/drivers/available/` - Faqat mavjud haydovchilar
- `GET /api/trucks/available/` - Faqat mavjud yuk mashinalari
- `GET /api/delivery-tasks/active/` - Faqat faol vazifalar
- `POST /api/delivery-tasks/assign/` - Yangi vazifa tayinlash

## 🛡️ Xavfsizlik Xususiyatlari

- **JWT Autentifikatsiya**: Xavfsiz token asosidagi API kirishi
- **Kompaniya Ma'lumotlari Izolyatsiyasi**: Foydalanuvchilar faqat o'z kompaniyasining ma'lumotlariga kirishlari mumkin
- **Rol Asosidagi Ruxsatlar**: Turli foydalanuvchi turlari uchun turli kirish darajalari
- **Kirish Ma'lumotlarini Tekshirish**: Keng qamrovli ma'lumotlar tekshiruvi va tozalash
- **CORS Konfiguratsiyasi**: To'g'ri cross-origin so'rovlarni boshqarish

## 🗺️ Xarita Integratsiyasi Tayyor

Tizim quyidagilar bilan integratsiya uchun tayyor:
- **Google Maps API**: Marshrut hisoblash va optimallashtirish
- **Yandex Maps API**: Alternativ xarita xizmati
- **Geocoding Xizmatlari**: Manzilni koordinatalarga aylantirish
- **Teskari Geocoding**: Koordinatalarni manzilga aylantirish

## 📊 Ma'lumotlar Bazasi Sxemasi

### Asosiy Modellar
- **Company**: Tenant/kompaniya ma'lumotlari
- **CompanyAdmin**: Django User'ni Company'ga bog'lash
- **DriverUser**: Django User'ni Driver'ga bog'lash
- **Driver**: Kompaniya tayinlash bilan haydovchi ma'lumotlari
- **Truck**: Kompaniya tayinlash bilan transport vositasining ma'lumotlari
- **Destination**: Kompaniya tayinlash bilan yetkazib berish joylari
- **DeliveryTask**: Haydovchilar, yuk mashinalari va manzillarni bog'lovchi vazifalar

### Asosiy Cheklovlar
- Kompaniya bo'yicha noyob litsenziya raqamlari
- Kompaniya bo'yicha noyob raqam raqamlari
- CASCADE o'chirish bilan foreign key munosabatlari
- Ishlash uchun to'g'ri indekslash

## 🚀 Joylashtirish Ko'rsatmalari

### Ishlab Chiqarish Sozlamalari
1. `DEBUG = False` ni sozlamalarda o'rnating
2. To'g'ri `ALLOWED_HOSTS` ni sozlang
3. Hissiy ma'lumotlar uchun muhit o'zgaruvchilaridan foydalaning
4. SSL sertifikatlarini sozlang
5. To'g'ri CORS manbalarini sozlang
6. Ishlab chiqarish PostgreSQL konfiguratsiyasidan foydalaning
7. To'g'ri logging va monitoring sozlang

### Muhit O'zgaruvchilari
```env
DB_NAME=production_db_name
DB_USER=production_user
DB_PASSWORD=secure_password
DB_HOST=production_host
DB_PORT=5432
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🤝 Hissa Qo'shish

1. Repozitoriyani fork qiling
2. Feature branch yarating
3. O'zgarishlaringizni qiling
4. Yangi funksionallik uchun testlar qo'shing
5. Barcha testlar o'tishini ta'minlang
6. Pull request yuboring

## 📄 Litsenziya

Bu loyiha MIT Litsenziyasi ostida litsenziyalangan - batafsil ma'lumot uchun LICENSE faylini ko'ring.

## 🆘 Yordam

Yordam va savollar uchun:
- Repozitoriyada issue yarating
- `/api/docs/` da API hujjatlarini ko'ring
- `/admin/` da Django admin panelini ko'rib chiqing

---

**Django 5.2, Django REST Framework va PostgreSQL bilan qurilgan**

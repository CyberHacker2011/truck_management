# 📋 Loyiha Xulosasi: Ko'p Kompaniyali Yuk Mashinalari Boshqarish Tizimi

## 🎯 Loyiha Umumiy Ko'rinishi

Ko'p kompaniyalar uchun yuk mashinalari parkini boshqarish uchun mo'ljallangan keng qamrovli Django asosidagi backend tizimi. To'liq ma'lumotlar izolyatsiyasi, rol asosidagi kirish nazorati va JWT autentifikatsiya bilan. Tizim logistika kompaniyalariga haydovchilar, yuk mashinalari, manzillar va yetkazib berish vazifalarini mustaqil ravishda boshqarish uchun masshtablanadigan yechim taqdim etadi, xavfsizlik va ma'lumotlar yaxlitligini saqlab qoladi.

## 🏗️ Arxitektura

### Ko'p Tenant Dizayni

- **Bitta Ma'lumotlar Bazasi, Ko'p Tenant'lar**: Kompaniya asosidagi ma'lumotlar ajratish bilan bitta PostgreSQL ma'lumotlar bazasi
- **ForeignKey Munosabatlari**: Barcha asosiy entitiyalar izolyatsiya uchun Company modeliga bog'langan
- **Noyob Cheklovlar**: Kompaniya doirasidagi noyoblik (litsenziya raqamlari, raqam raqamlari)
- **CASCADE O'chirish**: Kompaniyalar yoki tegishli entitiyalar olib tashlanganda to'g'ri tozalash

### Foydalanuvchi Rol Tizimi

- **Superuser**: To'liq tizim kirishi, barcha kompaniyalarni boshqarish mumkin
- **Kompaniya Admin**: Faqat tayinlangan kompaniyaning ma'lumotlarini boshqaradi, to'liq CRUD ruxsatlari
- **Haydovchi Foydalanuvchi**: Tayinlangan vazifalarga faqat o'qish uchun kirish, ma'lumotlarni o'zgartirish mumkin emas

## 🔧 Texnik Amalga Oshirish

### Backend Stack

- **Framework**: Django 5.2
- **API**: JWT autentifikatsiya bilan Django REST Framework
- **Ma'lumotlar Bazasi**: To'g'ri indekslash va cheklovlar bilan PostgreSQL
- **Autentifikatsiya**: Xavfsiz token asosidagi API kirishi uchun SimpleJWT
- **Hujjatlar**: Swagger/OpenAPI integratsiyasi drf-yasg bilan

### Amalga Oshirilgan Asosiy Xususiyatlar

1. **Kompaniya Boshqaruvi**: Kompaniya entitiyalari uchun to'liq CRUD operatsiyalari
2. **Haydovchilar Boshqaruvi**: Tajriba, holat va kompaniya tayinlashni kuzatish
3. **Yuk Mashinalari Parki Boshqaruvi**: Sig'im, yoqilg'i turi va mavjudlikni kuzatish
4. **Manzillar Boshqaruvi**: Koordinatalar bilan yetkazib berish joylarini saqlash
5. **Vazifa Tayinlash**: Yetkazib berish uchun haydovchilar, yuk mashinalari va manzillarni bog'lash
6. **Marshrut Optimallashtirish**: Google/Yandex Maps uchun API-ga tayyor integratsiya

## 📊 Ma'lumotlar Bazasi Sxemasi

### Asosiy Modellar

```
Company
├── CompanyAdmin (OneToOne with User)
├── DriverUser (OneToOne with User -> Driver)
├── Driver (ForeignKey to Company)
├── Truck (ForeignKey to Company)
├── Destination (ForeignKey to Company)
└── DeliveryTask (ForeignKey to Company, Driver, Truck)
```

### Ma'lumotlar Yaxlitligi

- **Noyob Cheklovlar**: Haydovchilar uchun `(company, license_number)`, yuk mashinalari uchun `(company, plate_number)`
- **Foreign Key Cascade'lar**: Ota entitiyalar olib tashlanganda to'g'ri o'chirish boshqaruvi
- **Tekshirish**: Serializatorlar va modellarda keng qamrovli kirish ma'lumotlarini tekshirish

## 🔐 Xavfsizlik va Ruxsatlar

### Autentifikatsiya Tizimi

- **JWT Tokenlar**: Access va refresh token amalga oshirish
- **Token Muddati**: Sozlanadigan token umri
- **Xavfsiz Endpoint'lar**: Barcha API endpoint'lari autentifikatsiya talab qiladi

### Ruxsat Darajalari

- **Superuser**: Barcha ma'lumotlarga cheklanmagan kirish
- **Kompaniya Admin**:
  - Kompaniyaning haydovchilari, yuk mashinalari, manzillari, vazifalarida to'liq CRUD
  - Boshqa kompaniyalarning ma'lumotlariga kirish mumkin emas
  - Admin panel kirishi kompaniya doirasiga cheklangan
- **Haydovchi Foydalanuvchi**:
  - Tayinlangan vazifalarga faqat o'qish uchun kirish
  - Hech qanday ma'lumot yaratish yoki o'zgartirish mumkin emas
  - Kompaniya doirasidagi ma'lumotlar ko'rinishi

### Ma'lumotlar Izolyatsiyasi

- **So'rov Filtrlash**: Barcha API so'rovlari avtomatik ravishda foydalanuvchining kompaniyasi bo'yicha filtrlanadi
- **Admin Doirasi**: Django admin interfeysi kompaniya chegaralarini hurmat qiladi
- **Serializer Tekshirish**: Ma'lumotlar yaratish paytida kompaniya konteksti ta'minlanadi

## 🚀 API Endpoint'lari

### Autentifikatsiya

- `POST /api/auth/token/` - JWT access token olish
- `POST /api/auth/token/refresh/` - Muddati o'tgan tokenlarni yangilash

### Asosiy Resurslar

- `GET/POST /api/companies/` - Kompaniya boshqaruvi (faqat admin)
- `GET/POST /api/drivers/` - Kompaniya doirasi bilan haydovchi CRUD
- `GET/POST /api/trucks/` - Yuk mashinalari parki boshqaruvi
- `GET/POST /api/destinations/` - Yetkazib berish joyini boshqarish
- `GET/POST /api/delivery-tasks/` - Vazifa tayinlash va kuzatuvi

### Maxsus Endpoint'lar

- `GET /api/drivers/available/` - Faqat mavjud haydovchilar
- `GET /api/trucks/available/` - Faqat mavjud yuk mashinalari
- `GET /api/delivery-tasks/active/` - Faqat faol vazifalar
- `POST /api/delivery-tasks/assign/` - Soddalashtirilgan vazifa tayinlash
- `POST /api/delivery-tasks/{id}/start/` - Vazifa bajarishni boshlash
- `POST /api/delivery-tasks/{id}/complete/` - Vazifani bajarilgan deb belgilash

## 🗺️ Xarita Integratsiyasi Tayyor

### Tayyorlangan API'lar

- **Marshrut Hisoblash**: Google Maps va Yandex Maps integratsiyasi
- **Marshrut Optimallashtirish**: Ko'p manzilli optimallashtirish algoritmlari
- **Geocoding**: Manzilni koordinataga aylantirish
- **Teskari Geocoding**: Koordinatani manzilga aylantirish

### Amalga Oshirish Holati

- Xarita integratsiyasi uchun API endpoint'lar belgilangan
- Tashqi API chaqiruvlari uchun utility funksiyalar tayyorlangan
- Ishlab chiqarish API kaliti konfiguratsiyasi uchun tayyor

## 📈 Namuna Ma'lumotlari va Sinash

### Sinov Kompaniyalari

1. **Acme Logistics**: 2 haydovchi, 2 yuk mashinasi, 3 manzil, 1 yetkazib berish vazifasi
2. **Bolt Transport**: 2 haydovchi, 2 yuk mashinasi, 2 manzil, 1 yetkazib berish vazifasi

### Sinov Foydalanuvchilari

- **Kompaniya Adminlari**: `acme_admin`, `bolt_admin` (parol: `admin123`)
- **Haydovchi Foydalanuvchilar**: `driver1` dan `driver4` gacha (parol: `driver123`)

### Ma'lumotlar Munosabatlari

- Har bir kompaniya mustaqil haydovchi va yuk mashinalari parkiga ega
- Manzillar kompaniyaga xos
- Yetkazib berish vazifalari kompaniya resurslarini bir-biriga bog'laydi
- Kompaniyalar o'rtasida to'liq ma'lumotlar izolyatsiyasi

## 🛠️ Ishlab Chiqish va Joylashtirish

### Ishlab Chiqish Sozlamalari

- **Muhit Konfiguratsiyasi**: Ma'lumotlar bazasi sozlamalari uchun `.env` fayl
- **Ma'lumotlar Bazasi Migratsiyasi**: To'g'ri default'lar bilan toza migratsiya tizimi
- **Namuna Ma'lumotlari**: Sinash uchun avtomatlashtirilgan to'ldirish buyrug'i
- **Admin Interfeysi**: Kompaniya doirasi bilan to'liq Django admin

### Ishlab Chiqarish Ko'rsatmalari

- **Xavfsizlik**: Hissiy ma'lumotlar uchun muhit o'zgaruvchilari
- **Ishlash**: Ma'lumotlar bazasi indekslash va so'rov optimallashtirish
- **Masshtablanuvchanlik**: Ko'p tenant arxitekturasi o'sishni qo'llab-quvvatlaydi
- **Kuzatish**: Django logging va xato boshqaruvi

### API Hujjatlari

- **Swagger UI**: `/api/docs/` da interaktiv API hujjatlari
- **OpenAPI Sxema**: Mashina tomonidan o'qiladigan API spetsifikatsiyasi
- **Autentifikatsiya Misollari**: JWT token ishlatish namunalari

## 🎯 Biznes Qiymati

### Logistika Kompaniyalari Uchun

- **Ko'p Kompaniya Qo'llab-Quvvatlash**: Ko'plab biznes bo'linmalari uchun bitta tizim
- **Ma'lumotlar Xavfsizligi**: Kompaniyalar o'rtasida to'liq izolyatsiya
- **Masshtablanuvchanlik**: Yangi kompaniyalar va resurslarni oson qo'shish
- **Rol Boshqaruvi**: Moslashuvchan foydalanuvchi ruxsatlari tizimi

### Haydovchilar Uchun

- **Mobilga Tayyor API**: Mobil ilovalar uchun mos JWT autentifikatsiya
- **Vazifa Ko'rinishi**: Tayinlangan yetkazib berishlarning aniq ko'rinishi
- **Holat Yangilanishlari**: Real vaqtli vazifa holati boshqaruvi

### Administratorlar Uchun

- **Kompaniya Boshqaruvi**: Kompaniya resurslari ustidan to'liq nazorat
- **Hisobot**: Kompaniyaga xos ma'lumotlar va tahlillarga kirish
- **Foydalanuvchi Boshqaruvi**: Haydovchi hisoblarini yaratish va boshqarish

## 🔮 Kelajakdagi Yaxshilanishlar

### Rejalashtirilgan Xususiyatlar

- **Real Vaqtli Kuzatish**: Jonli transport vositasini kuzatish uchun GPS integratsiyasi
- **Ilg'or Tahlil**: Yetkazib berish ishlashi va marshrut optimallashtirish hisobotlari
- **Mobil Ilova**: Haydovchilar uchun native mobil ilova
- **Integratsiya API'lari**: Uchinchi tomon logistika tizimi integratsiyasi
- **Xabarnoma Tizimi**: Vazifa yangilanishlari uchun SMS/Email ogohlantirishlar

### Texnik Yaxshilanishlar

- **Keshlash**: Yaxshilangan ishlash uchun Redis integratsiyasi
- **Orqa Fond Vazifalari**: Asinxron qayta ishlash uchun Celery
- **API Tezlik Cheklash**: Suiiste'moldan himoya qilish
- **Ilg'or Qidiruv**: Murakkab so'rovlar uchun Elasticsearch integratsiyasi

## 📊 Ishlash Ko'rsatkichlari

### Ma'lumotlar Bazasi Ishlashi

- **Indekslangan So'rovlar**: Kompaniya doirasidagi filtrlash uchun optimallashtirilgan
- **Foreign Key Munosabatlari**: Tegishli ma'lumotlar uchun samarali join'lar
- **Cheklov Tekshirish**: Ma'lumotlar bazasi darajasidagi ma'lumotlar yaxlitligi

### API Ishlashi

- **Paginatsiya**: Katta ma'lumotlar to'plamlari uchun sozlanadigan sahifa o'lchami
- **Select Related**: N+1 muammolarini oldini olish uchun optimallashtirilgan so'rovlar
- **Keshlashga Tayyor**: Redis integratsiyasi uchun tayyorlangan struktura

---

**Bu tizim korporativ darajadagi xavfsizlik, masshtablanuvchanlik va saqlanuvchanlik bilan ko'p kompaniyali yuk mashinalari parkini boshqarish uchun mustahkam asos taqdim etadi.**

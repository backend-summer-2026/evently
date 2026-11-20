# Python Backend Kodlash Standartlari (code-standards.md)

Evently loyihasi bo'yicha barcha kodlar quyidagi standartlarga mos bo'lishi shart:

---

## 1. Kod Tuzilishi va Uslubi (PEP 8 & Formatting)
- Python 3.11+ imkoniyatlaridan foydalanish.
- Type Hints: Barcha funksiyalar argumentlari va qaytaruvchi qiymatlari to'liq turlashtirilgan (`def func(param: str) -> bool:`) bo'lishi shart.
- Nomlanish qoidalari:
  - Funksiyalar va o'zgaruvchilar: `snake_case`
  - Klasslar, Modellar va Serializerlar: `PascalCase`
  - O'zgarmaslar (Constants): `UPPER_SNAKE_CASE`

---

## 2. Django & Django REST Framework Standartlari
- **Modellar (`models.py`):**
  - Ma'lumotlar tuzilmasi va constraintlar saqlanadi.
  - Murakkab biznes logika modellarda yozilmaydi.
  - Qat'iy cheklovlar uchun `models.UniqueConstraint` ishlatiladi.
- **Biznes Logika (`services.py`):**
  - Barcha biznes qoidalar (masalan, ro'yxatdan o'tish, joy tekshirish, bekor qilish) `services.py` ga chiqariladi.
  - Race condition (bir vaqtda so'rovlar) oldini olish uchun `select_for_update()` va `transaction.atomic()` qo'llaniladi.
  - HTTP bilan bog'liq obyektlar (`request`, `Response`) servicelarga kiritilmaydi.
  - Biznes xatolari uchun yagona format: `BusinessLogicError(detail="...", code="...")`.
- **Serializerlar (`serializers.py`):**
  - Kirish ma'lumotlarini validatsiya qilish va API javobini shakllantirish.
  - Tashqi xabarnoma (Telegram) yuborish serializer ichida bo'lmasligi kerak.
- **Viewlar (`views.py`):**
  - Yengil va toza bo'lishi lozim: faqat HTTP so'rovni qabul qiladi, serializer/service chaqiradi va `Response` qaytaradi.
  - Hujjatlashtirish uchun drf-spectacular `@extend_schema` dekoratori bilan to'ldiriladi.
- **Ruxsatlar (`permissions.py`):**
  - DRF `BasePermission` asosida qat'iy tekshiruvlar: `IsAdmin`, `IsAdminOrReadOnly`.

---

## 3. Testlash (Pytest)
- Har bir endpoint va biznes qoida uchun kamida:
  - 1 ta muvaffaqiyatli (Happy path) test;
  - 1 ta xatolik / chekka holat (Edge case, validation) testi yozilishi shart.
- Testlar `pytest` va `pytest-django` orqali yurgiziladi.

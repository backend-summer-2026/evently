# Python Backend Kodlash Standartlari (code-standards.md)

Loyiha bo'yicha barcha kodlar quyidagi standartlarga mos bo'lishi shart:

---

## 1. Kod Tuzilishi va Uslubi (PEP 8 & Formatting)
- Python 3.10+ imkoniyatlaridan foydalanish.
- Type Hints: Barcha funksiyalar argumentlari va qaytaruvchi qiymatlari to'liq turlashtirilgan (`def func(param: str) -> bool:`) bo'lishi shart.
- Nomlanish qoidalari:
  - Funksiyalar va o'zgaruvchilar: `snake_case`
  - Klasslar va Schemalar: `PascalCase`
  - O'zgarmaslar (Constants): `UPPER_SNAKE_CASE`

---

## 2. Framework va Kutubxonalar Standartlari
- **FastAPI:**
  - Routerni modullarga ajratish (`APIRouter`).
  - Dependency Injection mexanizmidan foydalanish (`Depends(...)`).
  - Aniq HTTP status kodlari (`status.HTTP_201_CREATED`, `status.HTTP_404_NOT_FOUND`).
- **Pydantic v2:**
  - Request va Response uchun alohida modellar (`EventCreate`, `EventUpdate`, `EventResponse`).
  - Ma'lumotlarni validatsiya qilish (`@field_validator`).
- **SQLAlchemy v2 (Async):**
  - Asinxron sessiyalar (`AsyncSession`).
  - `select()`, `update()`, `delete()` yangi sintaksisidan foydalanish.
  - Parollarni hech qachon ochiq saqlamaslik (bcrypt / passlib / argon2).

---

## 3. Testlash (Pytest)
- Har bir servis va endpoint uchun kamida:
  - 1 ta muvaffaqiyatli (Happy path) test;
  - 1 ta xatolik / validatsiya (Validation & Edge case) testi yozilishi shart.
- Asinxron testlar uchun `pytest-asyncio` va `httpx.AsyncClient` ishlatiladi.

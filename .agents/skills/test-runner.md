# Test Runner Ko'nikmasi (test-runner.md)

Ushbu ko'nikma Engineer va Reviewer agentlariga loyihadagi avtomatlashtirilgan testlarni ishga tushirish va natijalarni tahlil qilish imkonini beradi.

---

## 1. Testlarni Ishga Tushirish Buyruqlari

```bash
# Barcha testlarni ishga tushirish
python -m pytest

# Testlarni batafsil va loglar bilan yurgizish
python -m pytest -v -s

# Faqat bitta faylni testlash
python -m pytest tests/test_events.py

# Test coverage (qamrov) darajasini tekshirish
python -m pytest --cov=app --cov-report=term-missing
```

---

## 2. Natijalarni Baholash Mezonlari

- **Muvaffaqiyat (Pass):**
  - Chiqishda `=== X passed in Y seconds ===` va xatoliklar soni 0 bo'lsa, testlar to'liq o'tgan hisoblanadi.
- **Muvaffaqiyatsizlik (Fail):**
  - Chiqishda `FAILED tests/test_...` bo'lsa, xatolik bergan test nomi, assert sababi va traceback ajratib olinadi va to'g'rilash uchun `Engineer`ga yuboriladi.

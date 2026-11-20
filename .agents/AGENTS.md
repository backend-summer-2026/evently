# Multi-Agent Tizimi Konfiguratsiyasi va Boshqaruv Qoidalari (AGENTS.md)

Ushbu hujjat loyihadagi barcha AI Agentlar faoliyatini, ularning o'zaro aloqa protokoli va qat'iy ishlab chiqish tartibini belgilaydi.

---

## 1. Tizimdagi Agentlar va Ularning Mas'uliyati

| Agent | Rol | Birlamchi Vazifasi |
| :--- | :--- | :--- |
| **Orchestrator** | Bosh Boshqaruvchi | Butun workflow holatini (state) boshqaradi, vazifalarni uzatadi va qabul qiladi. |
| **Architect** | Tizim Arxitektori | Loyiha strukturasi, texnologiyalar stacki, API dizayni va kutubxonalarni belgilaydi. |
| **Engineer** | Dasturchi | Faqat `feat/<nom>` branchida kod yozadi, testlar tuzadi va xatolarni tuzatadi. |
| **Reviewer** | Code Reviewer & QA | Kod sifatini, xavfsizlikni va testlarni tekshiradi; `APPROVED` yoki `CHANGES_REQUESTED` beradi. |

---

## 2. Qat'iy Git-Flow va Branching Qoidalari

> [!CRITICAL]
> 1. **Himoyalangan Branchlar:** `main` va `develop` branchlariga **to'g'ridan-to'g'ri hech qachon kod yozilmaydi va commit qilinmaydi!**
> 2. **Ishni Boshlash:** Har qanday vazifa uchun Engineer faqat va faqat `develop` branchidan `feat/<task-name>` nomli yangi branch ochadi.
> 3. **Ish Jarayoni:** Barcha kodlash, o'zgartirish va testlar shu `feat/<task-name>` branchi ichida yoziladi.
> 4. **Muvaffaqiyatli Yakunlash (Merge & Delete):**
>    - Faqatgina `Reviewer` tomonidan `APPROVED` qarori berilgandan so'ng, `feat/<task-name>` branchi `develop`ga merge qilinadi:
>      ```bash
>      git checkout develop
>      git merge --no-ff feat/<task-name>
>      git branch -d feat/<task-name>
>      ```
>    - Ishlatilgan `feat/<task-name>` branchi butunlay o'chirib tashlanadi.

---

## 3. Workflow Oqimi (State Machine)

```
[User Prompt]
      │
      ▼
[1. Orchestrator] ──► [2. Architect]
                             │
                             ▼ (Arxitektura rejasi & feat/<task> nomi)
                     [develop branchidan git checkout -b feat/<task>]
                             │
                             ▼
                      [3. Engineer] ◄────────────────┐
                             │                       │
                             ▼ (Kod va Testlar)      │ (CHANGES_REQUESTED)
                      [4. Reviewer] ─────────────────┘ (Max: 3 sikl)
                             │
                             ▼ (APPROVED)
                     [1. Merge feat -> develop]
                     [2. Delete feat branch]
                             │
                             ▼
                     [Muvaffaqiyatli Tugatish]
```

---

## 4. O'zaro Aloqa Formatlari

- **Architect -> Engineer:** Texnologiyalar ro'yxati, papkalar arxitekturasi, API kontraktlari, branch nomi (`feat/<nom>`), vazifalar ro'yxati.
- **Engineer -> Reviewer:** Yaratilgan/tahrirlangan fayllar ro'yxati, `git diff`, test natijalari (pytest).
- **Reviewer -> Engineer (Xatolar bo'lsa):** Fayl nomi, qator raqami, aniq xatolik bayoni va tuzatish bo'yicha tavsiya.
- **Reviewer -> Orchestrator (Muvaffaqiyat bo'lsa):** `STATUS: APPROVED`, umumiy baho va merge ruxsati.

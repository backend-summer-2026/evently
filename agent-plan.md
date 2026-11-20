# AI Agentlar Tizimi va Workflow Arxitektura Rejasi (Agent Plan)

**Loyiha:** Multi-Agent Software Development System  
**Katalog:** `.agents/`  
**Muallif / Rol:** AI Agent Engineer  
**Sana:** 2026-11-20 (Yangilangan: Git-Flow & Branching Strategy)  

---

## 1. Kirish va Maqsad

Ushbu reja dasturiy ta'minot yaratish jarayonini avtomatlashtiruvchi, bir-biri bilan uzviy bog'langan **4 ta ixtisoslashgan AI Agent** (Orchestrator, Architect, Engineer, Reviewer) tizimini 0 dan qurish uchun mo'ljallangan. 

Barcha agent sozlamalari, tizim yo'riqnomalari (system prompts), qoidalar (rules), ko'nikmalar (skills) va ishga tushiruvchi orkestratsiya mexanizmi loyihaning `.agents/` katalogida joylashadi.

---

## 2. Agentlar, Git-Flow va Ularning Rollari

### Qat'iy Git Branching Qoidasi (Git Flow)
> [!IMPORTANT]
> - Loyihada 2 ta himoyalangan baza branch mavjud: **`main`** va **`develop`**.
> - **`main`** va **`develop`** branchlariga to'g'ridan-to'g'ri hech qachon kod yozilmaydi va to'g'ridan-to'g'ri commit qilinmaydi!
> - Har bir yangi vazifa uchun `develop` branchidan yangi **`feat/<vazifa-nomi>`** (feature branch) ochiladi.
> - Barcha kod yozish va tuzatish ishlari faqat `feat/<vazifa-nomi>` branchida bajariladi.
> - Faqatgina `Reviewer` kodni to'liq tekshirib **`APPROVED`** (muvaffaqiyatli) deb tasdiqlaganidan keyin:
>   1. `feat/<vazifa-nomi>` branchi `develop` branchiga **merge** qilinadi.
>   2. Ishlatilgan `feat/<vazifa-nomi>` branchi butunlay **o'chiriladi (delete)**.

```
                    +-------------------+
                    |    USER PROMPT    |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    |   ORCHESTRATOR    | <------------------------+
                    |  (Main Controller)|                          |
                    +---------+---------+                          |
                              |                                    |
                     (1) Texnik topshiriq                          |
                              |                                    |
                              v                                    |
                    +-------------------+                          |
                    |     ARCHITECT     |                          |
                    |  (Stack, Struct)  |                          |
                    +---------+---------+                          |
                              |                                    |
                     (2) Arxitektura rejasi                        |
                              |                                    |
                              v                                    |
                   [ develop dan branch: ]                         |
                   [  git checkout -b    ]                         |
                   [  feat/<task-name>   ]                         |
                              |                                    |
                              v                                    |
                    +-------------------+                          |
                    |     ENGINEER      | <------------------+     |
                    | (Faqat feat/...   |                    |     |
                    |  branchda yozadi) |                    |     |
                    +---------+---------+                    |     |
                              |                              |     |
                     (3) Kod va Testlar                      |     |
                              |                              |     |
                              v                              |     |
                    +-------------------+                    |     |
                    |     REVIEWER      |                    |     |
                    |   (Code Review)   |                    |     |
                    +---------+---------+                    |     |
                              |                              |     |
                +-------------+-------------+                |     |
                |                           |                |     |
          [APPROVED]                   [REJECTED]            |     |
                |                           |                |     |
                v                           +----------------+-----+
      1. Merge: feat -> develop            (Xatolar ko'rsatiladi,
      2. Delete: feat branch                feat/... branchda tuzatiladi.
      3. SUCCESS: END                       Max: 3-5 martagacha)
```

---

### Agentlarning Vazifalari va Mas'uliyatlari

#### 1. Main: Orchestrator (Bosh Boshqaruvchi)
- **Vazifasi:** Foydalanuvchi promptini qabul qiladi, butun ish oqimini (lifecycle) boshqaradi.
- **Mas'uliyati:** 
  - `Architect`ni ishga tushirish;
  - Git holatini nazorat qilish (bazaviy `develop` branch mavjudligini va tozaligini ta'minlash);
  - `Architect` bergan rejani `Engineer`ga topshirish;
  - `Engineer` ishini `Reviewer`ga yuborish;
  - `Reviewer` qarori bo'yicha:
    - Agar `CHANGES_REQUESTED` bo'lsa: Xatolarni yana `Engineer`ga qaytarish (maksimal 3-5 sikl).
    - Agar `APPROVED` bo'lsa: `feat/<task>` branchini `develop`ga merge qilish, `feat/<task>` branchini o'chirish va jarayonni muvaffaqiyatli yakunlash.

#### 2. Architect (Tizim Arxitektori)
- **Vazifasi:** Loyihaning umumiy texnik arxitekturasi va texnologiyalar stackini belgilaydi.
- **Mas'uliyati:**
  - Qanday kutubxonalar (`FastAPI`, `Pydantic`, `SQLAlchemy`, `Alembic`, `pytest` va h.k.) ishlatilishini belgilash;
  - Papkalar va fayllar tuzilmasini (Folder structure) loyihalash;
  - Database schema, modellar va API endpointlar kontraktlarini ishlab chiqish;
  - `Engineer` uchun qadam-baqadam texnik topshiriq (Technical Spec) va branch nomlanishini (`feat/<nom>`) tayyorlash.

#### 3. Engineer (Senior Dasturchi)
- **Vazifasi:** Kodni to'liq implementatsiya qiladi.
- **Qat'iy Qoidalar:**
  - **Hech qachon `main` yoki `develop` branchida to'g'ridan-to'g'ri ishlamaydi va commit qilmaydi!**
  - Har doim `develop` branchidan `feat/<task-name>` branchini ochib oladi:
    ```bash
    git checkout develop
    git pull origin develop # agar remote bo'lsa
    git checkout -b feat/<task-name>
    ```
  - Barcha fayllarni yaratish, tahrirlash va testlarni yozish faqat shu feature branchida bajariladi.
  - Reviewer tomonidan qaytarilgan o'zgartirishlarni shu branch ichida tuzatadi.
  - Kod tasdiqlanmaguncha o'zboshimchalik bilan `develop`ga merge qilmaydi.

#### 4. Reviewer (Code Reviewer & QA)
- **Vazifasi:** `Engineer` tomonidan `feat/<task-name>` branchida yozilgan kod sifatini, arxitekturaga mosligini va ishonchliligini tekshiradi.
- **Mas'uliyati:**
  - Sintaksis, xavfsizlik (security), corner cases va clean code tekshiruvi;
  - Barcha testlar va linterlarni ishga tushirib natijani ko'rish;
  - Yakuniy xulosa:
    - **`APPROVED`**: Kod to'liq talablarga mos, testlar yashil. `Orchestrator`ga merge va delete buyrug'i beriladi.
    - **`CHANGES_REQUESTED`**: Qaysi fayl va qatorda nima xato ekanligi, qanday tuzatish kerakligi haqida aniq ko'rsatmalar bilan `Engineer`ga qaytariladi.

---

## 3. Fayllar va Kataloglar Tuzilmasi (`.agents/`)

```text
.agents/
├── AGENTS.md                          # Orchestrator qoidalari, agentlar ro'yxati va Git-flow majburiyatlari
├── workflow.py                        # Multi-agent workflow'ni avtomat boshqaruvchi va git operatsiyalarini bajaruvchi skript
├── config.json                        # Global sozlamalar (max_review_cycles: 3, protected_branches: ["main", "develop"])
│
├── agents/                            # Har bir agentning alohida prompti
│   ├── orchestrator/
│   │   └── agent.md                   # Orchestrator yo'riqnomasi va branch merge/delete boshqaruvi
│   ├── architect/
│   │   └── agent.md                   # Architect arxitektura va stack qoidalari
│   ├── engineer/
│   │   └── agent.md                   # Engineer branch ochish, kod yozish va xatolarni to'g'rilash qoidalari
│   └── reviewer/
│       └── agent.md                   # Reviewer mezonlari, checklist va test tekshiruvlari
│
├── rules/                             # Tizim qoidalari
│   ├── multi-agent-workflow.md        # Holatlar diagrammasi, loopback va avtomat merge qoidalari
│   └── code-standards.md              # Python backend standartlari (PEP8, Typing, Async, Clean Architecture)
│
└── skills/                            # Ko'nikmalar
    ├── git-flow.md                    # Git checkout -b feat/..., commit, merge to develop va branch delete qoidalari
    └── test-runner.md                 # Testlarni (pytest) avtomatik ishga tushirish va natijalarni tahlil qilish
```

---

## 4. Qadam-baqadam Amalga Oshirish Bosqichlari (Implementation Plan)

### 1-Bosqich: Git va Katalog Bazasini Tayyorlash
1. Repozitoriyda `develop` branchini mavjudligini ta'minlash (`main`dan `develop` yaratish: `git branch develop`).
2. `.agents/agents/enginer` papkasini to'g'ri `engineer` shakliga o'zgartirish.
3. `.agents/config.json` konfiguratsiyasini yaratish:
   - `protected_branches`: `["main", "develop"]`
   - `max_review_cycles`: `3`
   - `auto_merge_on_approval`: `true`
   - `delete_feature_branch_on_merge`: `true`

### 2-Bosqich: Agentlarning System Promptlarini (`agent.md`) yozish
1. **`.agents/agents/architect/agent.md`**:
   - Texnik talablar, papkalar arxitekturasi va tavsiya etiladigan feature branch nomini shakllantirish.
2. **`.agents/agents/engineer/agent.md`**:
   - Qat'iy Git qoidasi: `main` va `develop`ga to'g'ridan-to'g'ri yozish man etiladi.
   - Har doim `develop`dan `feat/<nom>` ochish va kodni faqat o'sha branchda amalga oshirish.
   - Reviewer xatolarini tuzatish tartibi.
3. **`.agents/agents/reviewer/agent.md`**:
   - Feature branchdagi o'zgarishlarni tekshirish (`git diff develop...HEAD`), testlarni yurgizish.
   - `APPROVED` yoki `CHANGES_REQUESTED` formatida qat'iy javob qaytarish.

### 3-Bosqich: Rules va Skills Fayllarini Yaratish
1. **`.agents/skills/git-flow.md`**:
   - `develop`dan `feat/<nom>` branch ochish;
   - Conventional Commits (`feat: ...`, `fix: ...`);
   - Test tasdiqlangandan so'ng `develop`ga o'tish, `git merge --no-ff feat/<nom>` qilish va `git branch -d feat/<nom>` orqali o'chirish skriptlari va yo'riqnomasi.
2. **`.agents/rules/multi-agent-workflow.md`**:
   - To'liq holatlar zanjiri: `TASK_RECEIVED` -> `ARCHITECTING` -> `BRANCH_CREATED` -> `IMPLEMENTING` -> `REVIEWING` -> (`CHANGES_REQUESTED` -> `IMPLEMENTING`) yoki (`APPROVED` -> `MERGE_TO_DEVELOP` -> `DELETE_BRANCH` -> `DONE`).

### 4-Bosqich: Orchestrator va Runner (`workflow.py`)
- Python orqali agentlar ketma-ketligini avtomatlashtirish:
  - Branchlarni tekshirish va boshqarish (GitPython yoki subprocess orqali xavfsiz git buyruqlari);
  - Sikllar hisoblagichi (loop count: max 3).

---

## 5. Tasdiqlash va Testlash Rejasi (Verification Plan)

1. **Git Flow Tekshiruvi:**
   - Test jarayonida `develop`dan `feat/test-feature` branchi ochilishi;
   - `main` va `develop` branchlariga to'g'ridan-to'g'ri commit qilinmasligi tekshiriladi;
   - Reviewer `APPROVED` berganida, avtomatik tarzda `develop`ga merge bo'lib, `feat/test-feature` branchi o'chirilishi tasdiqlanadi.
2. **Sikl Tekshiruvi:**
   - Xatolik yuz berganda `Reviewer` tomonidan `CHANGES_REQUESTED` qaytishi va `Engineer` aynan o'sha `feat/...` branchida tuzatish kiritishi tekshiriladi.

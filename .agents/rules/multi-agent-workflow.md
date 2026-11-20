# Multi-Agent Workflow va Davlat Mashinasi Qoidalari (multi-agent-workflow.md)

Ushbu qoidalar to'plami barcha agentlarning navbatma-navbat ishlash tartibini, xatoliklarni qayta ishlash loopini va Git-Flow integratsiyasini boshqaradi.

---

## 1. Davlat Mashinasi Holatlari (States)

1. `IDLE`: Yangi topshiriq kutilmoqda.
2. `ARCHITECTING`: `Architect` loyihani tahlil qilmoqda va spetsifikatsiya tayyorlamoqda.
3. `BRANCH_SETUP`: `develop` branchidan `feat/<task-name>` branchi yaratilmoqda.
4. `ENGINEERING`: `Engineer` yangi branchda kod va testlar yozmoqda (yoki qaytarilgan xatolarni tuzatmoqda).
5. `REVIEWING`: `Reviewer` `develop...HEAD` diff'ini va test natijalarini tekshirmoqda.
6. `LOOP_EVALUATION`:
   - Agar natija `CHANGES_REQUESTED` bo'lsa:
     - `cycle_count += 1`
     - Agar `cycle_count <= max_review_cycles (3)`: Holat yana `ENGINEERING`ga o'tadi.
     - Agar `cycle_count > max_review_cycles`: Holat `ESCALATION`ga o'tadi (foydalanuvchiga to'xtatilib xabar qilinadi).
   - Agar natija `APPROVED` bo'lsa: Holat `MERGE_AND_CLEANUP`ga o'tadi.
7. `MERGE_AND_CLEANUP`:
   - `git checkout develop`
   - `git merge --no-ff feat/<task-name>`
   - `git branch -d feat/<task-name>`
8. `COMPLETED`: Vazifa to'liq yakunlandi.

---

## 2. O'tish Shartlari Jadvali (Transition Table)

| Joriy Holat | Hodisa / Shart | Keyingi Holat | Bajariladigan Amal |
| :--- | :--- | :--- | :--- |
| **IDLE** | Yangi user prompt | **ARCHITECTING** | Prompt Architect agentga beriladi |
| **ARCHITECTING** | Architect spec tayyor | **BRANCH_SETUP** | `feat/<task-name>` branchi yaratiladi |
| **BRANCH_SETUP** | Branch yaratildi | **ENGINEERING** | Engineer kodlashni boshlaydi |
| **ENGINEERING** | Kod va testlar tayyor | **REVIEWING** | Reviewerga diff va testlar uzatiladi |
| **REVIEWING** | Verdict: CHANGES_REQUESTED | **ENGINEERING** (Loop) | Xatolar Engineerga qaytariladi |
| **REVIEWING** | Verdict: APPROVED | **MERGE_AND_CLEANUP** | develop ga merge va branch delete |
| **MERGE_AND_CLEANUP**| Merge va delete muvaffaqiyatli | **COMPLETED** | Natija foydalanuvchiga taqdim etiladi |

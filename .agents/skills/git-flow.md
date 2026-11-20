# Git-Flow Operatsiyalari Ko'nikmasi (git-flow.md)

Ushbu ko'nikma agentlarga repozitoriyda branchlarni to'g'ri boshqarish, xatolarga yo'l qo'ymaslik va avtomatlashtirilgan merge/delete amallarini bajarishni o'rgatadi.

---

## 1. Asosiy Qoidalar

> [!WARNING]
> `main` va `develop` branchlarida to'g'ridan-to'g'ri hech qachon ishlamang!

---

## 2. Standart Buyruqlar Ketma-ketligi

### 1) Yangi Vazifa Boshlanganda (Branch ochish):
```bash
# 1. develop branchiga o'tish
git checkout develop

# 2. Yangi feature branch yaratish va unga o'tish
git checkout -b feat/<task-name>

# 3. Joriy branchni tekshirish
git branch --show-current
```

### 2) Kod yozilgach (Commit qilish):
```bash
# 1. O'zgarishlarni qo'shish
git add .

# 2. Conventional Commit standarti bilan saqlash
git commit -m "feat(<scope>): <qisqa va lo'nda tavsif>"
```

### 3) Reviewer Tasdiqlaganidan So'ng (Merge va Delete):
```bash
# 1. develop branchiga qaytish
git checkout develop

# 2. feat/<task-name> ni develop ga birlashtirish
git merge --no-ff feat/<task-name> -m "merge: feat/<task-name> into develop"

# 3. Ishlatilgan feature branchni o'chirib tashlash
git branch -d feat/<task-name>

# 4. Qolgan branchlarni tekshirish
git branch
```

### 4) Agar Reviewer Xatolik Topsa (Qayta ishlash):
```bash
# Feature branchda qolgan holda o'zgarishlar kiritiladi
git add .
git commit -m "fix(<scope>): address reviewer comments"
```

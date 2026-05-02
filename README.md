# 🛒 Shop Crowns Bot V2

Shop Crowns Bot هو بوت تليجرام متكامل لإدارة المتاجر الإلكترونية، يتيح للمستخدمين شراء المنتجات الرقمية، تقديم الشكاوى، التقييم، وتغيير البيانات مثل الأسماء والصور عبر نظام متكامل يدعم اللغتين العربية والإنجليزية.

---

## ✨ الميزات

* ✅ طلبات الشراء – Crowns, Coins, VIP، تعزيز حسابات، لايكات، وألعاب أخرى.
* 🎁 الطلبات المجانية – تغيير الاسم، تغيير الصورة الرمزية.
* 📦 المودات – تحميل مودات الألعاب بروابط مباشرة.
* 📝 الشكاوى والدعم – تذاكر شكاوى + شات مباشر مع الدعم.
* 👑 لوحة تحكم الأدمن – إدارة المستخدمين، الحظر، الإذاعة، التقييمات والسجلات.
* 🌍 دعم اللغتين العربية والإنجليزية.
* ⭐ تقييم البوت – نظام تقييم متكامل.
* 🧠 FSM باستخدام aiogram.
* ⏱️ مؤقتات وإدارة جلسات تلقائية.
* 🗃️ قاعدة بيانات SQLite.
* 📢 إذاعة عامة (نصوص – صور – فيديو).
* 🔐 حماية من السبام (Rate Limit + Anti-Flood).

---

## 🛠️ التقنيات المستخدمة

* Python 3.12
* aiogram v3.x
* SQLite3
* python-dotenv
* pytz
* Railway

---

## 📂 هيكل المشروع

```
shop-crowns-bot-v2/
├── bot/
│   ├── handlers/
│   ├── keyboards/
│   ├── states/
│   ├── utils/
│   ├── database/
│   ├── config.py
│   ├── loader.py
│   └── main.py
├── .env
├── .gitignore
├── Procfile
├── requirements.txt
└── README.md
```

---

## 🚀 التشغيل

### 1️⃣ تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 2️⃣ إعداد البيئة

أنشئ ملف `.env` واكتب:

```env
BOT_TOKEN=your_token
ADMIN_ID=your_id
TIMEZONE=Africa/Cairo
DATABASE_PATH=shop_crowns.db
DEFAULT_LANGUAGE=ar
```

---

### 3️⃣ تشغيل البوت

```bash
python bot/main.py
```

---

## 🚀 التشغيل على Railway

* ارفع المشروع على GitHub
* اربطه بـ Railway
* ضيف Environment Variables:

  * BOT_TOKEN
  * ADMIN_ID
* البوت هيشتغل تلقائي من Procfile

---

## 👑 أوامر الأدمن

| الأمر            | الوظيفة         |
| ---------------- | --------------- |
| /admin           | فتح لوحة التحكم |
| /ban <user_id>   | حظر مستخدم      |
| /unban <user_id> | فك الحظر        |
| /broadcast       | إرسال رسالة     |

---

## 🗄️ قاعدة البيانات

يتم إنشاء `shop_crowns.db` تلقائيًا.

الجداول:

* users
* orders
* tickets
* chat_sessions
* ratings
* admin_logs

---

## 🔧 ملاحظات

* الجلسات بتتقفل تلقائي بعد وقت معين
* في fallback للغة العربية لو الترجمة ناقصة
* النظام فيه حماية من السبام

---

## 📄 الترخيص

MIT

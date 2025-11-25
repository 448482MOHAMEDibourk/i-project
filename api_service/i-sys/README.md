## i_system — System helpers for api_services

هذا المجلد يجمع أدوات مساعدة جاهزة لتشغيل مشروع `ai-school` محليًا باستخدام نماذج محلية (Ollama, Aider) أو عبر حاويات Docker (mocks). الهدف هنا جعل تجربة التشغيل قابلة للتكرار للمطورين.

### توافق وملاحظات أساسية

- نظام التشغيل: Linux (المستهدف). قد تعمل الأدوات على macOS لكن لم يتم اختبارها هنا.
- Python: 3.9+ موصى به. السكربتات تنشئ `virtualenv` داخل `ai-school/.venv` عند تشغيل `run_demo.sh`.
- Docker & docker-compose: مطلوبان فقط إذا أردت تشغيل الـ mocks المحلّية.
- المتطلبات موزعة داخل `ai-school/requirements.txt` وملفات الإعداد في `ai-school/setup.md`.

### ملفات ذات أهمية

- `setup.sh` — استنساخ/تحديث مستودع `ai-school` (يستخدم المتغير `AI_SCHOOL_REPO`).
- `.env.example` — قالب متغيرات بيئة (نسخه إلى `.env` قبل التشغيل).
- `run_demo.sh` — ينشئ venv، يثبت المتطلبات، ويشغّل `scripts/demo_runner.py` داخل `ai-school`.
- `run_local_mocks.sh` — يشغّل `docker compose up --build` داخل `ai-school` إن وُجد `docker-compose.yml`.
- `run_demo.py` — غلاف Python لتشغيل demo بدون تفعيل venv يدوياً.
- `examples/run_prompt.sh` و`examples/run_prompt.py` — أمثلة سريعة للتحقق من خدمات Ollama وAider.
- `ai-sources.yaml` — تهيئة بسيطة لعناوين ونماذج المصادر المحلية (يستخدم كقيمة افتراضية).

### إعداد سريع (Quick start)

1. انسخ متغيرات البيئة الافتراضية إلى ملف `.env` داخل `i_system`:

```bash
cp .env.example .env
```

2. عدّل `AI_SCHOOL_REPO` داخل `.env` ليشير إلى المستودع الصحيح (مثلاً `git@github.com:your-org/ai-school.git`) إذا أردت أن يُستنسخ تلقائيًا.

3. استنساخ أو تحديث المستودع:

```bash
./setup.sh
```

4. تشغيل العرض التوضيحي (سيُنشئ virtualenv ويثبت المتطلبات إن لم تكن موجودة):

```bash
./run_demo.sh
```

5. إن أردت تشغيل الموكز (flask mocks الموجودة في `ai-school/mocks`) عبر Docker:

```bash
./run_local_mocks.sh
```

### أوامر تحقق سريعة

بعد إعداد `.env` (أو تعيين المتغيرات في البيئة) يمكنك التحقق من الوصول إلى الخدمات بواسطة curl أو الأمثلة المضمنة:

```bash
# Ollama (إذا كان يعمل على http://localhost:11434)
curl -sS -X POST "$OLLAMA_URL/api/generate" -H "Content-Type: application/json" -d '{"model":"mistral","prompt":"اختبار"}'

# Aider (إذا كان يعمل على http://localhost:8000)
curl -sS -X POST "${AIDER_ENDPOINT%/}/ask" -H "Content-Type: application/json" -d '{"prompt":"اختبار"}'

# أمثلة جاهزة (من مجلد i_system)
./examples/run_prompt.sh
python examples/run_prompt.py
```

### تكامل مع النماذج المحلية — Ollama و Aider

هذا المجلد يحتوي على أمثلة بسيطة للاتصال بنماذج محلية عبر Ollama وواجهة Aider. الفكرة: تتيح لك تجربة النماذج محليًا قبل نشرها.

- Ollama: إذا ثبّتت `ollama` محليًا، شغّل الخدمة وفق توثيق Ollama ثم حدّث المتغير `OLLAMA_URL` في `.env` (مثلاً `http://localhost:11434`). المثال في `examples/run_prompt.py` يوضح طلب POST إلى endpoint `/api/generate`.
- Aider: إذا استخدمت `aider` كخدمة لربط أدوات التطوير والنماذج، حدّث `AIDER_ENDPOINT` في `.env` (مثلاً `http://localhost:8000`) ثم استخدم `examples/run_prompt.py` أو `examples/run_prompt.sh` لاختبار الاتصال.

أدوات مساعدة مقترحة (لم تُنشأ بعد):

- `scripts/check_ollama.sh` — يفحص أن `ollama` مثبت ويجري استعلام اختبار.
- `scripts/check_aider.sh` — يتحقق من أن `aider` متاح على endpoint المحدد ويجري استعلام تجربة.
- `scripts/check_all.py` — سكربت بايثون يجري اختبارات سريعة على المصادر ويطبع ملخّص JSON.

راجع قسم "Try it" أدناه لتشغيل أمثلة جاهزة.

### Try it — أوامر سريعة للتجربة

اتبع الأوامر التالية لتجربة الأدوات والسكريبتات محليًا.

1. تأكد من نسخ متغيرات البيئة الأساسية من القالب:

```bash
cp .env.example .env
# ثم عدّل .env ليتضمن المسارات/العناوين الصحيحة، مثال:
# AI_SCHOOL_REPO=git@github.com:your-org/ai-school.git
# OLLAMA_URL=http://localhost:11434
# AIDER_ENDPOINT=http://localhost:8000
```

2. استنساخ أو تحديث مستودع `ai-school`:

```bash
# من داخل مجلد i_system
./scripts/clone_ai_school.sh
```

3. تشغيل الفحوصات السريعة (Ollama / Aider):

```bash
# من داخل i_system
./scripts/check_ollama.sh
./scripts/check_aider.sh

# أو — من أي مكان إذا أضفت الأغلفة إلى PATH (انظر أدناه)
check_ollama_i_system
check_aider_i_system
```

4. تشغيل العرض التوضيحي في `ai-school`:

```bash
./run_demo.sh
# أو من مجلد أعلى
# ./run_demo.sh (إذا كنت في i_system) أو cd ../ai-school && ./run_demo.sh
```

إضافة `~/bin` إلى PATH (إذا لم تكن موجودة):

```bash
# ضع هذه الأسطر في ~/.profile أو ~/.bashrc ثم أعد تسجيل الدخول أو شغّل `source ~/.profile`
export PATH="$HOME/bin:$PATH"
```

ملاحظات تصحيح الأخطاء السريعة

- إذا رأيت `No such file or directory` عند محاولة تشغيل `./scripts/check_ollama.sh` من الدليل الرئيسي (`~`)، فتأكد أنك في مجلد `i_system` أو استخدم الأغلفة `check_ollama_i_system`.
- إذا لم يستجب Ollama/Aider، افحص سجلات الخدمة، أو شغّل الموكز عبر `./run_local_mocks.sh` في حالة وجود mocks في `ai-school`.

### استكشاف الأخطاء وإصلاحها

- إذا فشل `./setup.sh` مع رسالة حول `AI_SCHOOL_REPO`، حدّث `.env` أو استنسخ `ai-school` يدوياً إلى المسار المجاور `../ai-school`.
- إذا لم يعمل `./run_demo.sh` فتأكد أن لديك Python مناسبًا وحقوق كتابة داخل `ai-school` لإنشاء `.venv`.
- إذا لم تستجب واجهات Ollama/Aider، شغّل الموكز عبر `./run_local_mocks.sh` ثم افحص السجلات في الطرفية.

### أمن وملاحظات إنتاجية

- لا تحفظ أسرار (API keys) في ملفات نصية غير مؤمنة للاستخدام الإنتاجي.
- هذا المجلد معدّ للأغراض التطويرية والاختبارية فقط.

---

إذا تريد أبدأ الآن بالخطوة التالية: تنفيذ اختبارٍ سريع محليًا (سأتحقق من توافر Docker وPython ثم أشغّل الموكز أو demo runner). اكتب "شغّل الاختبار" أو "لا، أريد أولاً تعديل AI_SCHOOL_REPO".

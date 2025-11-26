# نظام الأقطاب السبعة - i-project

نظام ذكي لإدارة المشاريع باستخدام نماذج لغوية محلية وأتمتة كاملة.

## 🎯 نظرة عامة

نظام الأقطاب السبعة هو إطار عمل لإدارة المشاريع يعتمد على 7 مراحل متسلسلة:

1. **الغايات والأهداف** - تحديد المهام
2. **المعرفة** - جمع المعلومات
3. **التخطيط** - وضع الخطط
4. **التنفيذ** - تنفيذ المهام
5. **التقييم** - تقييم النتائج
6. **التوثيق** - حفظ السجلات
7. **القرار** - اتخاذ القرارات

## ✨ المميزات

- ✅ **نماذج محلية**: استخدام نماذج Qwen2.5-Coder المحلية
- ✅ **تشغيل تلقائي**: مراقبة WORKSPACE والتفاعل الفوري
- ✅ **لوحة تحكم**: واجهة ويب متقدمة مع تحديث مباشر
- ✅ **قرارات تفاعلية**: مشاركة بشرية في اتخاذ القرار
- ✅ **مقاييس الأداء**: تسجيل وتحليل شامل

## 🚀 البدء السريع

### 1. التثبيت

```bash
# إنشاء بيئة افتراضية
python3 -m venv .venv
source .venv/bin/activate

# تثبيت التبعيات
pip install -r requirements.txt
```

### 2. التكوين

تأكد من تشغيل Ollama مع النماذج المطلوبة:

```bash
ollama list
# يجب أن ترى:
# - qwen2.5-coder:7b-instruct-q5_K_M
# - qwen2.5-coder:7b-instruct-q4_K_M
```

### 3. التشغيل

**الوكيل الرئيسي:**

```bash
python3 scripts/seven_pole_agent.py --gentle
```

**النظام التفاعلي:**

```bash
python3 scripts/pole_agent.py
```

**لوحة التحكم:**

```bash
cd dashboard && python3 app.py
# افتح: http://localhost:5000
```

## 🔒 تنفيذ معزول (Sandbox)

لتمكين تنفيذ آمن للخطط (القطب 4) بدون المخاطرة ببيئة النظام المضيف، يوفر المشروع "Sandbox" اختياريًا.

- الملف التنفيذي للمSandbox: `scripts/sandbox_runner.py`
- التفعيل عبر التكوين: أضف أو حدّث قسم `sandbox` في `config/local_models.yaml` كالتالي:

```yaml
sandbox:
	enabled: true        # فعِّل التنفيذ داخل الـ Sandbox
	timeout: 60          # مهلة تنفيذ الخطة (بالثواني)
	cpus: 0.5            # عدد CPU الممنوح للحاوية (Docker)
	memory: "256m"     # حد الذاكرة (Docker)
	image: "python:3.11-slim"  # صورة Docker الافتراضية
```

كيفية العمل:

- عندما تكون `sandbox.enabled` = `true` و`--dry-run` غير مفعّل، فإن `seven_pole_agent` سيكتب الخطة إلى ملف مؤقت ويدعو `scripts/sandbox_runner.py` لتنفيذها داخل Docker (إن وُجد)، مع تطبيق حدود الموارد والمهلة.
- إذا لم يتوفر Docker، يقوم `sandbox_runner` بسقوطٍ آمن (fallback) إلى تنفيذ محلي محدود مع المهلة المحددة.

أوامر اختبار سريعة:

```bash
# تشغيل وكيل الأقطاب السبعة مع sandbox مفعل في التكوين (غير dry-run):
python3 scripts/seven_pole_agent.py --gentle

# تشغيل الـ sandbox-runner مستقلاً (تنفيذ خطة بسيطة):
python3 scripts/sandbox_runner.py --plan-string "echo 'hello sandbox'" --timeout 10
```

ملاحظات أمان:

- `sandbox_runner` يعيّن الخيار `--network=none` لحاوية Docker لتعطيل الشبكة أثناء التنفيذ.
- تأكد من أن الخطة لا تحتوي أوامر خطيرة قبل تفعيل التنفيذ الفعلي؛ استخدم `--dry-run` أثناء الاختبار.

## 📚 الوثائق

- [هيكلة المشروع](PROJECT_STRUCTURE.md)
- [توثيق النظام](SYSTEM.md)
- [قاعدة المعرفة](data/CONSOLIDATED.md)

## 🛠️ الأدوات

### إضافة مهام:

```bash
python3 scripts/add_task.py "وصف المهمة"
python3 scripts/inject_task.py "وصف المهمة"
```

### المراقبة:

```bash
./scripts/monitor.sh
python3 scripts/workspace_monitor.py
```

## 📊 البيانات

- **المقاييس**: `execution/benchmarks.csv`
- **السجلات**: `execution/logs/`
- **الطوابير**: `execution/queue/`

## 🤝 المساهمة

النظام قابل للتوسع والتخصيص. راجع `SYSTEM.md` لفهم البنية الكاملة.

## 📝 الترخيص

مشروع داخلي - جميع الحقوق محفوظة

**PR: Partition `data/archive` into YYYY/MM and normalize tracked archive files**

**ملخّص**

- **الهدف:** نقل الملفات النصّية المتتبعة داخل `data/archive` إلى بنية زمنية `data/archive/YYYY/MM/` لتحسين أداء Git، تنظيم الأرشيف، وتطبيق قاعدة R3/G10. هذه العملية طُبّقت على الملفات المتتبعة فقط بعد استثناء ملفات البيئات والمرفقات الثنائية الكبيرة.
- **الفرع:** `feature/partition-archive-20251125` (تم إنشاءه، ونُفِّذت عليه التحويلات).
- **خريطة النقل:** `.tmp_partition_dryrun/mapping_filtered.csv` (417 سطر).

**إحصاءات سريعة**

- **ملفات متتبعة مخططة للنقل:** 417
- **عينة عرضية:** أول 200 سطر عُرضت أثناء المراجعة، ملف الخريطة الكامل محفوظ في المسار أعلاه.

**عينة من الخريطة**

- `data/archive/history/CONSOLIDATED.md -> data/archive/2025/11/CONSOLIDATED.md`
- `data/archive/history/ORGANIZATION.md -> data/archive/2025/11/ORGANIZATION.md`
- `data/archive/history/PROJECT_MAP.md -> data/archive/2025/11/PROJECT_MAP.md`

**ما استُثني ولماذا**

- **دليل بيئات التشغيل / مكتبات:** `*/site-packages/*`, `*/.venv/*`, `*/venv/*` — بيئات غير مناسبة للتتبّع في هذا repo.
- **شجرات Git مضمّنة:** `*/.git/*` — تُترك كأرشيف مُنفصل على القرص وليست متتبعة ضمن هذا الريبو.
- **حزم Node:** `*/node_modules/*` — ثنائية/كائنية وعمومًا غير مناسبة للتتبع.
- **ملفات أرشيف وثنائية كبيرة:** `*.tar.gz`, `*.zip`, `*.dill`, `*.so`, `*.bin`, `*.gz` — تُستبعد لأنّها تزيد حجم السجل بشكل حاد.
- **ملفات أكبر من 50MB:** تم تجاهلها أثناء بناء الخريطة لتجنّب إضافة ملفات ضخمة إلى Git history.

**عمليات التنفيذ التي أُجريت**

- أنشأنا سكربت مُصحَّح: `.tmp_partition_dryrun/run_moves_corrected.sh` (يستخدم `mkdir -p "$(dirname \"$dst\")"` لتجنّب إنشاء مجلدات باسم الملف).
- أُجريَ اختبار على أول 10 ملفات على فرع مؤقت `tmp/partition-test-20251125` لالتقاط أي مشاكل تنفيذية وتصحيحها (تم إصلاح حالة إنشاء مجلدات باسم الملف ثم توثيق التغييرات في commits اختبارية).
- بعد التحقق، شُغّل السكربت المصحح على كامل الخريطة (417 نقل). التغييرات مُسجَّلة على الفرع `feature/partition-archive-20251125` محليًا.

**ملاحظات R5 (Hooks / جودة الكود)**

- أثناء محاولة الـ `git commit` الأولى، فشلت بعض hooks (مثال: ESLint) على ملفات JS/TS المعاد ترتيبها؛ هذا يُشير إلى أنّ بعض الملفات المنقولة تحتوي على تحذيرات/أخطاء lint موجودة مسبقاً.
- الإجراء التلقائي المُتبع: إذا فشل commit بسبب hooks، قمنا بتشغيل أدوات التصحيح الآلي على الملفات المتأثرة (`black`, `ruff` للبايثون؛ تعليمات ثابتة لتشغيل إصلاحات JS/TS إن لزم)، ثم إعادة التجربة. إذا استمر الفشل فستحتاج مراجعة يدوية.

**تعليمات التطبيق (أوامر مطلوبة لإعادة إنتاج العمل أو لفحصه)**

- عرض الخريطة الكاملـة:

```
sed -n '1,400p' .tmp_partition_dryrun/mapping_filtered.csv
```

- عرض السكربت المصحّح (preview):

```
sed -n '1,40p' .tmp_partition_dryrun/run_moves_corrected.sh
```

- لو أردت تكرار النقل محلياً (مسبقاً)، أوّلًا تأكد أنك على فرع جديد:

```
git checkout -b feature/partition-archive-20251125
bash .tmp_partition_dryrun/run_moves_corrected.sh
git add -A
git commit -m "chore(archive): partition data/archive into YYYY/MM for tracked textual files"
git push -u origin feature/partition-archive-20251125
```

**كيفية التراجع (إذا احتجنا)**

- استعادة commit واحد: على فرع العمل استخدم:

```
git reset --hard HEAD~1
```

تنبيه: هذا يُزيل التغييرات في الـ working tree؛ استخدم بحذر.

- تراجع انتقائي لمسارات: استخدم:

```
git restore --staged <path>
git restore <path>
```

**ملاحظات CI / مراجعة النداء للدمج**

- قبل الدمج، تأكد من أن CI يمرّ بنجاح على `feature/partition-archive-20251125`. CI قد يحتاج تحديثات طفيفة إذا كان يعتمد على مسارات قد تغيّرت.
- أضف وصفًا في PR يشير إلى الخريطة (`.tmp_partition_dryrun/mapping_filtered.csv`) والرابط إلى ملف `.tmp_archive_report/large_files.csv` لشرح الاستثناءات الكبيرة.

**الخطوة التالية المقترحة (مقترحة منّي)**

1. أنشئ PR من `feature/partition-archive-20251125` → `feat/import-converted-data` مع هذا الوصف أو استخدمه كقاعدة للنشر.
2. اطلب مراجعة من فِرق الصيانة/CI لمعاينة تأثيرات المسارات على الـ pipelines.
3. بعد الموافقة، ادمج وراقب CI/تطبيقات العمل.

**هل أجهز PR الآن؟**

- اكتب "نعم، جهّز PR" وسأُنشئ ملف `pr_body_full.md` (هذا الملف) كـ body جاهز للنسخ في واجهة GitHub و/أو أفتح PR تلقائياً إذا رغبت.
- اكتب "راجع" إن أردت إدخال تعديلات على نص الـ PR قبل إنشائه.

**Priority Rules (Detection-First)**

- **Comprehensive detection & prioritization (أولوية الكشف والفرز):** Perform a full discovery of runtime and integration errors across the active code paths, then rank them by centrality/impact. This discovery-and-ranking step is the top priority.

- **Fix (Central-first):** Repair the most central and high-impact runtime errors first (CI blockers, security, data-loss). Apply minimal, targeted fixes and validate with tests and CI.

- **Central improvements / infra:** After critical fixes, implement central improvements that prevent recurrence (settings consolidation, shared client contracts, infra refactors).

- **Secondary improvements / docs:** Low-risk work such as documentation, minor refactors, and ergonomics improvements — schedule opportunistically.

**قواعد الحوكمة (Governance Rules)**

بما أننا حدّدنا أن المشكلة الرئيسية هي في **بنية المشروع وتحديد المسارات (Paths)**، فهذه مجموعة قواعد عمل لتجنيب التكرار والالتباس وتوجيه عملية التصحيح نحو الخطأ المركزي أولاً.

**1. قواعد هيكلة المشروع وتوحيد الأسماء**

- **إزالة الغموض في المسارات:** إعادة تسمية المجلدات المتسببة في التضارب لتوضيح الغرض منها.

  - الإجراء: استخدم أمر `find` لتحديد ملف التشغيل الحقيقي، ثم أعد تسمية المجلد الذي يحتويه (مثلاً إذا كان `new-project/i-sys` هو الكود الأساسي، فقم بتسميته `core_system`).

- **ملفات الدعم/المكتبات الفرعية:** يجب تمييزها بوضوح.

  - الإجراء: استخدم `snake_case` للأسماء (مثال: `i_system` بدلاً من `i-sys`) لتفادي الالتباس مع أدوات CI أو أسماء الحزم.

- **قاعدة التجاهل (Exclusion):** تأكد من أن `pyproject.toml` يتضمن `exclude = ["data/archive/**"]` ضمن إعدادات التحليل، وتحقق من أن `ruff` يقرأها فعليًا قبل عمليات الفحص.

**2. قواعد تدفق التصحيح (Debugging Flow)**

- **تحديد نقطة الدخول أولاً (أولوية قصوى):** قبل تشغيل أي شيء، حدد الملف الذي يحتوي نقطة الدخول (`main.py`, `run.py`, أو أي ملف يُستدعى مباشرة) ثم حدّث أمر التشغيل لاستخدام المسار الكامل.

  - الإجراء: استخدم `find` أو البحث عن `if __name__ == "__main__"` لتحديد وحدة التشغيل، ثم وثّق المسار في README أو في `scripts/` تشغيلية.

- **التصحيح المتسلسل (Fix-One-Thing-at-a-Time):** أصلح خطأ واحد فقط في كل دورة وبأصغر تعديل ممكن. أمثلة: عند مواجهة `NameError` أضف استيرادًا واحدًا فقط ثم أعد التشغيل.

- **الـ `ruff` هو حارس البوابة (Linting Gate):** قبل محاولة التشغيل، تشغيل `ruff check` على الكود النشط يجب أن يعيد صفر أخطاء. إذا لم يكن كذلك، أصلح التحويلات البسيطة أو عزل المسارات المشبوهة عن الفحص.

**3. قواعد الإبلاغ ومراقبة الـ CI**

- **التقرير الموحد للأخطاء:** عند الإبلاغ عن خطأ تشغيل احرص على لصق الـ `Traceback` الكامل أو على الأقل أول 10 أسطر منه.

- **الـ CI هو المرجع النهائي:** بعد كل إصلاح، ادفع التغيير إلى الفرع واضغط CI (GitHub Actions). نجاح CI هو مؤشر أن الإصلاح لم يكسر البيئة.

**إجراءات تشغيلية مقترحة (نماذج أوامر مفيدة)**

```
# تحديد ملفات الدخول الشائعة
find . -name "main.py" -o -name "run.py" -o -name "app.py" -o -name "server.py"

# البحث عن وحدات قابلة للتشغيل
grep -R --line-number "if __name__ == \"__main__\"" src new-project i-sys || true

# التحقق من قواعد التجاهل في pyproject.toml ثم تشغيل ruff على المسارات المحددة
python -c "import tomllib,sys;print('pyproject found' if tomllib.loads(open('pyproject.toml','rb').read()) else 'no')" || true
ruff check src new-project || true
```

اتّباع هذه القواعد سيساعد على تركيز جهود التصحيح على الخطأ المركزي وتجنّب تغييرات واسعة غير ضرورية أثناء الدورة الأولى من الإصلاح.

---


**قاعدة وصول الملفات (File Access Rules)**

لتقليل مخاطر التغيير غير المقصود وضمان سلامة الأرشيف والمعرفة، اعتمدنا القواعد التالية لجميع المسارات في المستودع.

1) ملفات المشاريع القديمة والملفات الحساسة — قراءة فقط (Read-Only) ما لم يُصرِّح المستخدم صراحةً بالكتابة
- النطاق: `data/archive/**`, أي أرشيفات قديمة، نسخ احتياطية، وملفات حساسة تعريفية (مفاتيح، إعدادات بيئية مسماة كمحفوظات).
- القاعدة: لا تُجرى عليها تعديلات أو حذف مباشرة عبر commits إلا بعد طلب صريح ومفصّل في issue/PR، والحصول على موافقة مالك/مراجع مختص.
- التنفيذ العملي: ضع علامة على المسارات الحساسة في `docs/STANDARDS.md`، واستخدم pre-commit / CI checks لرفض التغييرات المباشرة (فشل CI إذا تغيّر ملف موسوم كـ read-only دون استثناء مذكور في PR).

2) ملفات التجارب والمعرفة — إلحاقي فقط (Append-Only), لا تُقلَّص أو تُحذف محتوياتها
- النطاق: دلائل التجارب، سجلات التجارب، مجموعات البيانات التجريبية غير المتتبعة كالـ `knowledge/` أو `data/experiments/` (حدد المسارات الفعلية لبيئتك).
- القاعدة: يسمح بإضافة أسطر/ملفات جديدة لتوسيع المعرفة، لكن لا يسمح بحذف أو تعديل السجلات التاريخية؛ أي تصحيح يجب أن يتم بواسطة سجل تتابعي (new entry) يشرح سبب التصحيح.
- التنفيذ العملي: تفعيل hook أو CI rule يكتشف تغييرات حذفية/تعديلاً على ملفات في هذه المسارات ويرفضها (يطلب إنشاء ملف متابعة بدل التعديل). توثيق صيغة الإدخال (timestamp, author, reason).

3) ملفات القواعد، ملفات التعليمات، اختيارات المستخدم، بطاقات المشاريع، وملفات الأوامر — ثابتة وغير قابلة للتعديل/الحذف (Immutable)
- النطاق: `docs/*.md`, `rules/*.md`, `configs/default_choices.*`, `projects/cards/*.md`, `scripts/run_*`, `scripts/commands/*` (اضبط المسارات حسب المشروع).
- القاعدة: لا تُعدل هذه الملفات مباشرة؛ تغييراتها تتطلب PR مبرر مع مراجعة مزدوجة وموافقة من صاحب الوثائق/مالك المنتج.
- التنفيذ العملي: استخدم branch protection، ومنع الدمج إذا لم يمرّ PR بفحوص المراجعة المطلوبة، وتطبيق CI check يرفض تغييرات غير مبررة.

4) عملية طلب الاستثناء (How to request write/change)
- افتح issue يشرح السبب، أثر التغيير، وخطة الاختبار/الرجوع.
- أضف في PR عنوان `EXCEPTION: <paths>` ووسم reviewer المختص.
- بعد موافقة، سيكون مسموحًا بتعديل الملفات المذكورة مع توثيق واضح في وصف PR.

5) مراقبة وتنفيذ فني
- أضف قواعد pre-commit أو CI للتحقق من نوع التغيير (حذف/تعديل/إضافة) لمسارات محددة.
- سجل نتائج الفحوص في تقرير CI (فشل/قبول) واذكر إرشادات الاستثناء في وثائق المشروع.

Generated by repo maintenance scripts — راجع الخريطة قبل الدمج.

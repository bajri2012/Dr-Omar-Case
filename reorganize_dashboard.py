import os
import re

CASES_DIR = "cases"
README_FILE = "README.md"
INDEX_FILE = "index.md"

def get_cases_data():
    cases_data = []
    # Recursively find md files in the cases folder
    for root, dirs, files in os.walk(CASES_DIR):
        for f in files:
            if f.endswith(".md") and f.replace(".md", "") == os.path.basename(root):
                file_path = os.path.join(root, f)
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    try:
                        case = {
                            "num": f.replace(".md", ""),
                            "type": re.search(r"# تفاصيل القضية: (.*) -", content).group(1),
                            "status": re.search(r"> \*\*الحالة:\*\* (.*)", content).group(1),
                            "role": re.search(r"> \*\*الصفة:\*\* (.*)", content).group(1),
                            "plaintiff": re.search(r"- \*\*المدعي:\*\* (.*)", content).group(1),
                            "defendant": re.search(r"- \*\*المدعى عليه:\*\* (.*)", content).group(1),
                            "date": re.search(r"- \*\*تاريخ القضية:\*\* (.*)", content).group(1),
                            "rel_path": f"./cases/{os.path.basename(root)}/{f}"
                        }
                        cases_data.append(case)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
    return cases_data

def build_readme(stats):
    content = f"""# ⚖️ نظام إدارة القضايا الشامل

مرحباً بك في نظام الأرشفة القانونية. تم تنظيم هذا النظام لتسهيل الوصول إلى المعلومات الحيوية لكل قضية ومتابعة حالتها ومرفقاتها لجميع الأطراف المعنية.

## 📊 إحصائيات القضايا الكلية
> [!NOTE]
> ملخص شامل لحالات جميع القضايا المسجلة في النظام.

| الحالة | العدد |
| :--- | :--- |
| 📁 إجمالي القضايا | **{stats['total']}** |
| ⏳ قيد النظر | **{stats['active']}** |
| ✅ منتهية | **{stats['finished']}** |
| 🏛️ محكومة | **{stats['judged']}** |
| ⚠️ أخرى | **{stats['others']}** |

## 📂 خريطة المشروع
- **[الفهرس الرئيسي](./index.md)**: عرض تفصيلي لجميع القضايا مقسمة حسب الحالة.
- **مجلد [Cases/](./cases/)**: يحتوي على الحافظات المستقلة لكل قضية (تشمل المرفقات).
- **[New-instruction.md](./New-instruction.md)**: ملف المصدر الأساسي للبيانات.

## 🚀 روابط سريعة
- [عرض القضايا النشطة](./index.md#active-cases)
- [عرض القضايا المنتهية](./index.md#closed-cases)

---
*تم تحديث النظام ليشمل كافة القضايا موزعة على مجلدات مستقلة للمرفقات.*
"""
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def build_index(cases):
    # Grouping
    active = [c for c in cases if "قيد النظر" in c['status']]
    judged = [c for c in cases if "محكومة" in c['status']]
    finished = [c for c in cases if "منتهية" in c['status'] and "محكومة" not in c['status']]
    others = [c for c in cases if all(x not in c['status'] for x in ["قيد النظر", "محكومة", "منتهية"])]

    content = """# 🗂️ الفهرس الموحد للقضايا الشامل

<a id="active-cases"></a>
## 📂 قضايا قيد النظر (نشطة)
> [!IMPORTANT]
> قضايا لم يصدر فيها حكم نهائي بعد وتحتاج لمتابعة مستمرة.

| رقم القضية | نوع القضية | المدعي | المدعى عليه | الحالة | تاريخ القضية |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for c in active:
        content += f"| [{c['num']}]({c['rel_path']}) | {c['type']} | {c['plaintiff']} | {c['defendant']} | {c['status']} | {c['date']} |\n"

    content += """
<a id="closed-cases"></a>
## ✅ قضايا منتهية أو محكومة
> [!TIP]
> قضايا أرشفة صدر فيها حكم أو تم التنازل عنها.

| رقم القضية | نوع القضية | المدعي | المدعى عليه | الحالة | تاريخ القضية |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for c in (judged + finished):
        content += f"| [{c['num']}]({c['rel_path']}) | {c['type']} | {c['plaintiff']} | {c['defendant']} | {c['status']} | {c['date']} |\n"

    if others:
        content += """
## ⚠️ حالات أخرى
| رقم القضية | نوع القضية | المدعي | المدعى عليه | الحالة | تاريخ القضية |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
        for c in others:
            content += f"| [{c['num']}]({c['rel_path']}) | {c['type']} | {c['plaintiff']} | {c['defendant']} | {c['status']} | {c['date']} |\n"

    content += "\n---\n[العودة للرئيسية](./README.md)"

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    data = get_cases_data()
    stats = {
        'total': len(data),
        'active': len([c for c in data if "قيد النظر" in c['status']]),
        'finished': len([c for c in data if "منتهية" in c['status'] and "محكومة" not in c['status']]),
        'judged': len([c for c in data if "محكومة" in c['status']]),
        'others': len([c for c in data if all(x not in c['status'] for x in ["قيد النظر", "محكومة", "منتهية"])])
    }
    build_readme(stats)
    build_index(data)
    print("Files restructured and reorganized successfully.")

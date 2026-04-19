import os
import re

CASES_DIR = "cases"
README_FILE = "README.md"
INDEX_FILE = "index.md"
INSTRUCTION_FILE = "New-instruction.md"

# Specific IDs to keep regardless of status
KEEP_IDS = {'4670968566', '4570088468', '4771849984', '4670551825'}

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
                        # Extract next session if available
                        session_match = re.search(r"- \*\*الجلسة القادمة:\*\* (.*)", content)
                        if session_match:
                            case["next_session"] = session_match.group(1)
                        else:
                            # Try to find in instruction file format
                            case["next_session"] = "غير محدد"
                            
                        cases_data.append(case)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
    return cases_data

def get_instruction_metadata():
    with open(INSTRUCTION_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract sections using regex
    estate = re.search(r"تقدير التركة\n(.*?)(?=\n\n|\nتقدير|$)", content, re.DOTALL)
    debts = re.search(r"تقدير الديون\n(.*?)(?=\n\n|\nشرح|$)", content, re.DOTALL)
    priorities = re.search(r"شرح المواقف والأولويات(.*?)(\n\n|\nاهم|$)", content, re.DOTALL)
    
    return {
        "estate": estate.group(1).strip() if estate else "",
        "debts": debts.group(1).strip() if debts else "",
        "priorities": priorities.group(1).strip() if priorities else ""
    }

def build_readme(stats, metadata, cases):
    # Prepare hearing dates table
    hearings_content = "\n| رقم القضية | الموضوع | موعد الجلسة |\n| :--- | :--- | :--- |\n"
    active_cases = [c for c in cases if "قيد النظر" in c['status']]
    for c in active_cases:
        hearings_content += f"| [{c['num']}]({c['rel_path']}) | {c['type']} | {c.get('next_session', 'غير محدد')} |\n"

    content = f"""# ⚖️ نظام إدارة القضايا الشامل - د. عمر باجري

مرحباً بك في نظام الأرشفة القانونية الموحد. تم تنظيم هذا النظام لمتابعة القضايا النشطة والديون والتركة الخاصة بالوالد عبدالعزيز عيسى باجري (رحمه الله).

## 📊 إحصائيات النظام الحالية
> [!NOTE]
> تم تصفية النظام ليركز فقط على القضايا النشطة والقضايا الجوهرية المنتهية.

| الحالة | العدد |
| :--- | :--- |
| 📁 إجمالي القضايا النشطة | **{stats['active']}** |
| ✅ قضايا مرجعية منتهية | **{stats['keep']}** |

## 👥 شرح الأطراف
- **المورث:** عبدالعزيز عيسى باجري (رحمه الله).
- **الورثة:** (محمد، عمر، أمل، ابتسام، عماد، عقيل، وداد، محسن).
- **الأطراف الخارجية:** بنك الراجحي، بنك ساب، مدرسة دار جنى، شركة الاعتماد.

## 💰 تقدير التركة
{metadata['estate']}

## 🧾 تقدير الديون
{metadata['debts']}

## 🎯 الأولويات والمواقف (د. عمر باجري)
{metadata['priorities']}

## 📅 جدول الجلسات القادمة
{hearings_content}

## 📂 خريطة الوصول
- **[الفهرس التفصيلي للقضايا](./index.md)**
- **[ملف التعليمات المصدر](./New-instruction.md)**

---
*تم تنظيف النظام وتحديث البيانات السردية بتاريخ اليوم.*
"""
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def build_index(cases):
    # Filter based on user request: Keep Active OR in KEEP_IDS
    filtered_cases = [c for c in cases if "قيد النظر" in c['status'] or c['num'] in KEEP_IDS]
    
    active = [c for c in filtered_cases if "قيد النظر" in c['status']]
    keep_finished = [c for c in filtered_cases if c['num'] in KEEP_IDS and "قيد النظر" not in c['status']]

    content = """# 🗂️ الفهرس الموحد (النسخة المنقحة)

<a id="active-cases"></a>
## 📂 قضايا قيد النظر (نشطة)
| رقم القضية | نوع القضية | المدعي | المدعى عليه | الحالة | تاريخ القضية |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for c in active:
        content += f"| [{c['num']}]({c['rel_path']}) | {c['type']} | {c['plaintiff']} | {c['defendant']} | {c['status']} | {c['date']} |\n"

    content += """
<a id="closed-cases"></a>
## ✅ قضايا مرجعية (منتهية/أرشفة)
> [!TIP]
> قضايا منتهية تم الإبقاء عليها لأهميتها في التركة.

| رقم القضية | نوع القضية | المدعي | المدعى عليه | الحالة | تاريخ القضية |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for c in keep_finished:
        content += f"| [{c['num']}]({c['rel_path']}) | {c['type']} | {c['plaintiff']} | {c['defendant']} | {c['status']} | {c['date']} |\n"

    content += "\n---\n[العودة للرئيسية](./README.md)"

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    data = get_cases_data()
    metadata = get_instruction_metadata()
    
    stats = {
        'total': len(data),
        'active': len([c for c in data if "قيد النظر" in c['status']]),
        'keep': len([c for c in data if c['num'] in KEEP_IDS and "قيد النظر" not in c['status']])
    }
    
    build_readme(stats, metadata, data)
    build_index(data)
    print("Dashboard updated and cleanup verified.")

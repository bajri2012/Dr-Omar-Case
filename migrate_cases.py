import os
import re

# Paths
INPUT_FILE = "New-instruction.md"
OUTPUT_DIR = "cases"
INDEX_FILE = "index.md"

def parse_cases(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    
    cases = []
    current_case = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if "رقم القضية" in line:
            if current_case:
                cases.append(current_case)
            current_case = {"رقم القضية": lines[i+1] if i+1 < len(lines) else ""}
            i += 2
        elif "تاريخ القضية" in line:
            current_case["تاريخ القضية"] = lines[i+1] if i+1 < len(lines) else ""
            i += 2
        elif "نوع القضية" in line:
            current_case["نوع القضية"] = lines[i+1] if i+1 < len(lines) else ""
            i += 2
        elif "الصفة" in line:
            current_case["الصفة"] = lines[i+1] if i+1 < len(lines) else ""
            i += 2
        elif "المدعي" in line:
            current_case["المدعي"] = lines[i+1] if i+1 < len(lines) else ""
            i += 2
        elif "المدعى عليه" in line:
            current_case["المدعى عليه"] = lines[i+1] if i+1 < len(lines) else ""
            i += 2
        elif "الحالة" in line:
            current_case["الحالة"] = lines[i+1] if i+1 < len(lines) else ""
            i += 2
        else:
            i += 1
            
    if current_case:
        cases.append(current_case)
        
    return cases

def generate_case_md(case):
    case_num = case.get("رقم القضية", "بدون_رقم")
    case_type = case.get("نوع القضية", "غير محدد")
    
    content = f"""# تفاصيل القضية: {case_type} - {case_num}

> [!IMPORTANT]
> **رقم القضية:** {case_num}
> **الحالة:** {case.get("الحالة", "غير محدد")}
> **الصفة:** {case.get("الصفة", "غير محدد")}

## 📑 معلومات الأطراف
- **المدعي:** {case.get("المدعي", "غير محدد")}
- **المدعى عليه:** {case.get("المدعى عليه", "غير محدد")}

## 📅 بيانات القضية
- **تاريخ القضية:** {case.get("تاريخ القضية", "غير محدد")}
- **نوع القضية:** {case_type}

## 🔍 شرح القضية (ملخص)
*(يمكنك إضافة تفاصيل سير القضية هنا)*
- 

---
## 📎 مرفقات القضية
*(أضف روابط المستندات والمرفقات هنا)*
- [ ] لائحة الدعوى
- [ ] الوكالات
- [ ] أحكام سابقة (إن وجد)

---
[العودة للفهرس الرئيسي](../index.md)
"""
    return content

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    all_cases = parse_cases(INPUT_FILE)
    
    # Process ALL cases
    cases_to_process = all_cases
    
    processed_list = []
    
    for case in cases_to_process:
        case_num = case.get("رقم القضية", "بدون_رقم")
        if not case_num: continue
        
        content = generate_case_md(case)
        
        file_name = f"{case_num}.md"
        with open(os.path.join(OUTPUT_DIR, file_name), "w", encoding="utf-8") as f:
            f.write(content)
            
        processed_list.append({
            "num": case_num,
            "type": case.get("نوع القضية", "غير محدد"),
            "plaintiff": case.get("المدعي", "غير محدد"),
            "defendant": case.get("المدعى عليه", "غير محدد"),
            "status": case.get("الحالة", "غير محدد"),
            "date": case.get("تاريخ القضية", "غير محدد")
        })

    # Note: reorganize_dashboard.py will handle the index and README generation properly 
    # to maintain consistency and grouping.
    print(f"Completed! Generated {len(processed_list)} case files total.")

if __name__ == "__main__":
    main()

import os
import re

# Paths
INPUT_FILE = "New-instruction.md"
OUTPUT_DIR = "cases"

def parse_cases(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Handle the classic block format (the 44 cases)
    classic_cases = []
    lines = [line.strip() for line in content.split("\n")]
    i = 0
    while i < len(lines):
        line = lines[i]
        if "رقم القضية" in line and i+1 < len(lines) and re.match(r"^\d+$", lines[i+1]):
            case = {"رقم القضية": lines[i+1]}
            i += 2
            # Look for other fields until next case
            while i < len(lines) and "رقم القضية" not in lines[i]:
                if "تاريخ القضية" in lines[i] and i+1 < len(lines):
                    case["تاريخ القضية"] = lines[i+1]
                    i += 2
                elif "نوع القضية" in lines[i] and i+1 < len(lines):
                    case["نوع القضية"] = lines[i+1]
                    i += 2
                elif "الصفة" in lines[i] and i+1 < len(lines):
                    case["الصفة"] = lines[i+1]
                    i += 2
                elif "المدعي" in lines[i] and i+1 < len(lines):
                    case["المدعي"] = lines[i+1]
                    i += 2
                elif "المدعى عليه" in lines[i] and i+1 < len(lines):
                    case["المدعى عليه"] = lines[i+1]
                    i += 2
                elif "الحالة" in lines[i] and i+1 < len(lines):
                    case["الحالة"] = lines[i+1]
                    i += 2
                else:
                    i += 1
            classic_cases.append(case)
        else:
            i += 1

    # Handle the NEW detailed format (e.g. #4772114909 with value and attachments)
    detailed_cases = {}
    detailed_blocks = re.findall(r"(رقم القضية #?(\d+).*?)(?=\nرقم القضية #?|\Z)", content, re.DOTALL)
    for block_full, case_num in detailed_blocks:
        case = {"رقم القضية": case_num}
        # Extract fields
        value_match = re.search(r"قيمة القضية ([\d,]+) ريال", block_full)
        if value_match: case["قيمة القضية"] = value_match.group(1)
        
        hearing_match = re.search(r"الجلسة القادمة حددت بتاريخ ([\d/]+)هـ", block_full)
        if hearing_match: case["الجلسة القادمة"] = hearing_match.group(1)
        
        status_line = re.search(r"الحالة : (.*)", block_full)
        if status_line: case["الحالة"] = status_line.group(1).strip()
        
        # Merge with classic if exists
        detailed_cases[case_num] = case

    # Merging logic: classic + detailed updates
    final_cases = {}
    for c in classic_cases:
        num = c["رقم القضية"]
        final_cases[num] = c
    
    # Update with details
    for num, det in detailed_cases.items():
        if num in final_cases:
            final_cases[num].update(det)
        else:
            final_cases[num] = det
            
    return list(final_cases.values())

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
"""
    if "قيمة القضية" in case:
        content += f"- **قيمة القضية:** {case['قيمة القضية']} ريال\n"
    if "الجلسة القادمة" in case:
        content += f"- **الجلسة القادمة:** {case['الجلسة القادمة']}هـ\n"

    content += f"""
## 🔍 شرح القضية (ملخص)
*(يمكنك إضافة تفاصيل سير القضية هنا)*
- 

---
## 📎 مرفقات القضية (Morfqat)
*(المرفقات موجودة في مجلد attachments داخل حافظة القضية)*
- [ ] لائحة الدعوى
- [ ] الوكالات
- [ ] أحكام سابقة (إن وجد)

---
[العودة للفهرس الرئيسي](../../index.md)
"""
    return content

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    all_cases = parse_cases(INPUT_FILE)
    
    for case in all_cases:
        case_num = case.get("رقم القضية")
        if not case_num: continue
        
        # New Structural Logic: Create Folder
        case_folder = os.path.join(OUTPUT_DIR, case_num)
        os.makedirs(case_folder, exist_ok=True)
        os.makedirs(os.path.join(case_folder, "attachments"), exist_ok=True)
        
        content = generate_case_md(case)
        
        file_path = os.path.join(case_folder, f"{case_num}.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"Update complete! Processed {len(all_cases)} cases into per-case folders.")

if __name__ == "__main__":
    main()

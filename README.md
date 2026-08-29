# Friends Forever Change Request System
## Exit Exam MVC 1/2569

ระบบจัดการคำขอเปลี่ยนบทบาทสมาชิก พัฒนาด้วย Python 3 + Flask (MVC pattern)

---

## วิธีรันโปรแกรม

```bash
# 1. ติดตั้ง dependency
pip install flask

# 2. รันโปรแกรม
python main.py

# 3. เปิดเบราว์เซอร์
# http://127.0.0.1:8080
```

**การใช้งาน:**
1. เลือก "ตัวตน (Actor)" จาก dropdown หน้าแรก
2. สร้างคำขอเปลี่ยนบทบาทให้สมาชิกอื่น
3. ลงความเห็น APPROVE/REJECT ในคำขอที่มีสิทธิ์
4. ดูสรุปคำขอแยกตามสถานะในหน้า "คำขอ"

---

## วิธีรันเทสต์ T1–T6

```bash
# รัน T1–T6 ต่อเนื่องบน state เดียวกัน
python tests/test_scenarios.py

# หรือผ่าน pytest
pip install pytest
python -m pytest tests/test_scenarios.py -v
```

### ผลที่คาดหวัง

| Test | Action | Expected |
|---|---|---|
| T1 | M05 สร้างคำขอให้ M01 → EDITOR | สร้างสำเร็จ (C05) PENDING |
| T2 | M03 สร้างให้ M01 → CREATOR | ปฏิเสธ (M01 มี C05 PENDING อยู่) |
| T3 | M04 APPROVE C01 | APPROVED, M02: FINANCE→EDITOR |
| T4 | M05 REJECT C02 | REJECTED, M03 ยัง EDITOR |
| T5 | M03 ยกเลิก C03 | CANCELLED |
| T6 | M05 APPROVE C04 | ปฏิเสธ (M05 = target ของ C04) |


---

## MVC Architecture

| Layer | ไฟล์ | หน้าที่ |
|---|---|---|
| **Model** | `app/models/` | ถือ business rules ทั้งหมด (eligibility, threshold, cancel conditions) |
| **View** | `app/templates/*.html` | แสดงผลเท่านั้น ไม่มี logic |
| **Controller** | `app/controllers/*.py` | รับ HTTP request, เรียก Store/Model, ส่งข้อมูลให้ View |
| **Service** | `app/services/store.py` | In-memory store, cross-entity validation (pending duplicate check) |

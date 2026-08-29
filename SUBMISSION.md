# SUBMISSION - Exit Exam MVC 1/2569

## 1. วิธีเปิดโปรแกรม
- ภาษา/เฟรมเวิร์ก: Python 3 + Flask 3.x (web app, Jinja2 templates)
- Entry point / คำสั่งเปิดโปรแกรม:
  ```bash
  pip install flask
  python main.py
  # เปิดเบราว์เซอร์ที่ http://localhost:5000
  ```
- หมายเหตุที่จำเป็น: ต้องรัน `python tests/test_scenarios.py` เพื่อทดสอบ T1–T6

## 2. ตารางเชื่อมโยง Requirements

| Requirement | Model / Domain | Controller / Action | View / Screen |
|---|---|---|---|
| R1 MVC structure | `app/models/` (Member, RoleChangeRequest, Decision, enums) + `app/services/store.py` | `app/controllers/member_controller.py`, `app/controllers/request_controller.py` (Flask Blueprints) | `app/templates/*.html` (Jinja2, แสดงผลเท่านั้น) |
| R2 ดูสมาชิก + สร้างคำขอ | `Member`, `RoleChangeRequest`; `Store.create_request()` ตรวจ requester≠target และไม่มี PENDING ซ้อน | `MemberController.list_members()`, `RequestController.create_request()` | `members.html`, `create_request.html` |
| R3 ลงความเห็น | `RoleChangeRequest.check_voter_eligible()` ตรวจ active/requester/target/voted; `RoleChangeRequest.add_decision()` | `RequestController.vote()` | `request_detail.html` (แสดงฟอร์ม APPROVE/REJECT หรือข้อความไม่มีสิทธิ์) |
| R4 สรุปผล + เปลี่ยน role | `RoleChangeRequest.add_decision()` นับ approve_count/reject_count; ถ้า ≥ 2 เปลี่ยน status และ `target.role` | `RequestController.vote()` (orchestrate) | `request_detail.html` แสดงสถานะหลังอัปเดต |
| R5 ยกเลิก + สรุป + error | `RoleChangeRequest.cancel()` ตรวจ requester/PENDING/ไม่มี decisions; ทุก method คืน `(bool, str)` ไม่ crash | `RequestController.cancel_request()`, `list_requests()` (grouped by status) | `requests.html` แยกหมวด PENDING/APPROVED/REJECTED/CANCELLED; flash messages แสดง error |

## 3. ผลการทดสอบ

| กรณี | ผ่าน/ไม่ผ่าน | หมายเหตุ |
|---|---|---|
| T1 | ✅ ผ่าน | M05 สร้าง C05 สำเร็จ (M01 ไม่มี PENDING ก่อน T1) → C05 สถานะ PENDING |
| T2 | ✅ ผ่าน | ปฏิเสธด้วยเหตุผล "คุยกันได้ มีคำขอ PENDING อยู่แล้ว (คำขอ C05)" — M01 ติด C05 จาก T1 |
| T3 | ✅ ผ่าน | M04 APPROVE C01: approve_count 1→2 → C01=APPROVED, M02 role: FINANCE→EDITOR |
| T4 | ✅ ผ่าน | M05 REJECT C02: reject_count 1→2 → C02=REJECTED, M03 role ยัง EDITOR |
| T5 | ✅ ผ่าน | M03 cancel C03: ไม่มี decisions → C03=CANCELLED |
| T6 | ✅ ผ่าน | ปฏิเสธ "เป้าหมายของคำขอไม่สามารถลงความเห็นได้" — M05 เป็น target_id ของ C04 |

## 4. ความแตกต่างระหว่างแบบที่ออกกับโปรแกรมจริง (ถ้ามี)

1. ข้อความ flash message ใน T3 ยังแสดง `Role.EDITOR` แบบ enum repr ก่อนแก้ → แก้แล้วเป็น `EDITOR`
2. ไม่มี

## 5. บันทึกการใช้ AI

| เวลาโดยประมาณ | เครื่องมือ | ใช้เพื่ออะไร | นำคำแนะนำไปใช้อย่างไร |
|---|---|---|---|
| 14.30 | GPT | ช่วยตรวจสอบโดยการส่งโค้ด test ในส่วนที่เป็น Role.EDITOR พอรันแล้วมีปัญหาไม่ตรงกับโจทย์ |  |

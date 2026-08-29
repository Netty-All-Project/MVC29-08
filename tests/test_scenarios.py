"""
T1–T6 ต่อเนื่องบน state เดียวกัน (ไม่ reset ระหว่าง test)
รัน: python -m pytest tests/test_scenarios.py -v
หรือ: python tests/test_scenarios.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import Store
from app.models import DecisionResult, RequestStatus, Role

SEED = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seed_data.json")

# --- shared state (loaded once, mutated across all tests) ---
store = Store()
store.load_seed(SEED)

PASS = "PASS"
FAIL = "FAIL"
results = []


def check(label: str, cond: bool, note: str = ""):
    tag = PASS if cond else FAIL
    results.append((label, tag, note))
    icon = "✅" if cond else "❌"
    print(f"{icon} [{tag}] {label}" + (f" — {note}" if note else ""))
    return cond


# ─── Verify seed state ────────────────────────────────────────────────
print("\n=== ตรวจสอบ state หลัง load seed ===")
c01 = store.get_request("C01")
c02 = store.get_request("C02")
c03 = store.get_request("C03")
c04 = store.get_request("C04")

check("seed: C01 PENDING", c01.status == RequestStatus.PENDING)
check("seed: C01 มี 1 APPROVE (M03)", c01.approve_count == 1)
check("seed: C02 PENDING", c02.status == RequestStatus.PENDING)
check("seed: C02 มี 1 REJECT (M04)", c02.reject_count == 1)
check("seed: C03 PENDING ไม่มี decisions", c03.status == RequestStatus.PENDING and not c03.decisions)
check("seed: C04 PENDING มี 1 APPROVE (M01)", c04.approve_count == 1)


# ─── T1: M05 สร้างคำขอให้ M01 → EDITOR ──────────────────────────────
print("\n=== T1: M05 สร้างคำขอให้ M01 เปลี่ยนเป็น EDITOR ===")
ok, msg, new_req = store.create_request("M05", "M01", Role.EDITOR)
print(f"   ผล: {msg}")
check("T1: สร้างสำเร็จ", ok, msg)
check("T1: คำขอใหม่สถานะ PENDING", ok and new_req.status == RequestStatus.PENDING)
T1_req_id = new_req.id if ok else None


# ─── T2: M03 พยายามสร้างให้ M01 อีกครั้ง → ต้องปฏิเสธ ──────────────
print("\n=== T2: M03 พยายามสร้างคำขอให้ M01 เปลี่ยนเป็น CREATOR ===")
ok2, msg2, _ = store.create_request("M03", "M01", Role.CREATOR)
print(f"   ผล: {msg2}")
check("T2: ปฏิเสธเพราะ M01 มี PENDING อยู่", not ok2, msg2)


# ─── T3: M04 APPROVE ต่อ C01 → ครบ 2 → APPROVED, M02 → EDITOR ───────
print("\n=== T3: M04 ลงความเห็น APPROVE ต่อ C01 ===")
m02_before = store.get_member("M02").role
ok3, msg3 = store.submit_vote("M04", "C01", DecisionResult.APPROVE)
print(f"   ผล: {msg3}")
m02_after = store.get_member("M02").role
c01_after = store.get_request("C01")
check("T3: บันทึกสำเร็จ", ok3, msg3)
check("T3: C01 → APPROVED", c01_after.status == RequestStatus.APPROVED)
check("T3: M02 role เปลี่ยนเป็น EDITOR", m02_after == Role.EDITOR,
      f"ก่อน={m02_before.value} หลัง={m02_after.value}")


# ─── T4: M05 REJECT ต่อ C02 → ครบ 2 → REJECTED, M03 ยัง EDITOR ──────
print("\n=== T4: M05 ลงความเห็น REJECT ต่อ C02 ===")
m03_before = store.get_member("M03").role
ok4, msg4 = store.submit_vote("M05", "C02", DecisionResult.REJECT)
print(f"   ผล: {msg4}")
m03_after = store.get_member("M03").role
c02_after = store.get_request("C02")
check("T4: บันทึกสำเร็จ", ok4, msg4)
check("T4: C02 → REJECTED", c02_after.status == RequestStatus.REJECTED)
check("T4: M03 role ยัง EDITOR", m03_after == Role.EDITOR,
      f"role={m03_after.value}")


# ─── T5: M03 ยกเลิก C03 (ไม่มีความเห็น) → CANCELLED ─────────────────
print("\n=== T5: M03 ยกเลิก C03 ===")
ok5, msg5 = store.cancel_request("M03", "C03")
print(f"   ผล: {msg5}")
c03_after = store.get_request("C03")
check("T5: ยกเลิกสำเร็จ", ok5, msg5)
check("T5: C03 → CANCELLED", c03_after.status == RequestStatus.CANCELLED)


# ─── T6: M05 APPROVE ต่อ C04 → ปฏิเสธ (M05 = target) ────────────────
print("\n=== T6: M05 ลงความเห็น APPROVE ต่อ C04 ===")
ok6, msg6 = store.submit_vote("M05", "C04", DecisionResult.APPROVE)
print(f"   ผล: {msg6}")
check("T6: ปฏิเสธเพราะ M05 เป็น target ของ C04", not ok6, msg6)


# ─── สรุปผล ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("สรุปผลการทดสอบ")
print("="*60)
passed = sum(1 for _, t, _ in results if t == PASS)
total = len(results)
for label, tag, note in results:
    icon = "✅" if tag == PASS else "❌"
    print(f"  {icon} {label}" + (f"\n       → {note}" if note else ""))
print(f"\nผ่าน {passed}/{total}")

if passed < total:
    sys.exit(1)

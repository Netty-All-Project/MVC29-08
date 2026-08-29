from dataclasses import dataclass, field
from typing import List, Tuple, TYPE_CHECKING
from .enums import RequestStatus, DecisionResult
from .decision import Decision

if TYPE_CHECKING:
    from .member import Member


@dataclass
class RoleChangeRequest:
    id: str
    requester_id: str
    target_id: str
    new_role: str          # Role enum value
    status: RequestStatus = RequestStatus.PENDING
    decisions: List[Decision] = field(default_factory=list)

    # --- computed properties (pure domain logic) ---

    @property
    def approve_count(self) -> int:
        return sum(1 for d in self.decisions if d.result == DecisionResult.APPROVE)

    @property
    def reject_count(self) -> int:
        return sum(1 for d in self.decisions if d.result == DecisionResult.REJECT)

    @property
    def is_terminal(self) -> bool:
        return self.status != RequestStatus.PENDING

    # --- business rules ---

    def check_voter_eligible(self, voter_id: str) -> Tuple[bool, str]:
        """Return (ok, reason). Caller must also check voter.active."""
        if self.is_terminal:
            return False, f"คำขอนี้ปิดแล้ว (สถานะ: {self.status.value})"
        if voter_id == self.requester_id:
            return False, "ผู้เสนอไม่สามารถลงความเห็นได้"
        if voter_id == self.target_id:
            return False, "เป้าหมายของคำขอไม่สามารถลงความเห็นได้"
        if any(d.member_id == voter_id for d in self.decisions):
            return False, "คุณได้ลงความเห็นในคำขอนี้ไปแล้ว"
        return True, ""

    def add_decision(self, decision: Decision, target_member: "Member") -> Tuple[bool, str]:
        """Record vote and resolve outcome if threshold reached. Returns (success, message)."""
        ok, reason = self.check_voter_eligible(decision.member_id)
        if not ok:
            return False, reason

        self.decisions.append(decision)

        if self.approve_count >= 2:
            self.status = RequestStatus.APPROVED
            target_member.role = self.new_role
            return True, f"ครบ 2 เสียง APPROVE → คำขออนุมัติแล้ว บทบาทของ {target_member.name} เปลี่ยนเป็น {self.new_role.value}"
        if self.reject_count >= 2:
            self.status = RequestStatus.REJECTED
            return True, f"ครบ 2 เสียง REJECT → คำขอถูกปฏิเสธ บทบาทของ {target_member.name} ไม่เปลี่ยน"

        return True, "บันทึกความเห็นสำเร็จ"

    def cancel(self, actor_id: str) -> Tuple[bool, str]:
        """Cancel by requester only when PENDING and no votes yet."""
        if actor_id != self.requester_id:
            return False, "เฉพาะผู้เสนอเท่านั้นที่สามารถยกเลิกคำขอได้"
        if self.status != RequestStatus.PENDING:
            return False, f"ยกเลิกไม่ได้ คำขออยู่ในสถานะ {self.status.value}"
        if self.decisions:
            return False, "มีผู้ลงความเห็นแล้ว ไม่สามารถยกเลิกได้"
        self.status = RequestStatus.CANCELLED
        return True, "ยกเลิกคำขอสำเร็จ"

"""In-memory store and seed loader. Single source of state for the app."""
import json
import os
from typing import Dict, List, Optional, Tuple

from app.models import Member, Decision, RoleChangeRequest, Role, RequestStatus, DecisionResult


class Store:
    def __init__(self):
        self.members: Dict[str, Member] = {}
        self.requests: Dict[str, RoleChangeRequest] = {}
        self._next_request_seq = 1

    # --- seed ---

    def load_seed(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        for m in data["members"]:
            self.members[m["id"]] = Member(
                id=m["id"],
                name=m["name"],
                role=Role(m["role"]),
                active=m["active"],
            )

        for r in data["role_change_requests"]:
            self.requests[r["id"]] = RoleChangeRequest(
                id=r["id"],
                requester_id=r["requester_id"],
                target_id=r["target_id"],
                new_role=Role(r["new_role"]),
                status=RequestStatus(r["status"]),
            )
            # track sequence so new IDs don't clash
            seq = int(r["id"][1:]) if r["id"][0] == "C" and r["id"][1:].isdigit() else 0
            self._next_request_seq = max(self._next_request_seq, seq + 1)

        for d in data["decisions"]:
            req = self.requests.get(d["request_id"])
            if req:
                req.decisions.append(Decision(
                    request_id=d["request_id"],
                    member_id=d["member_id"],
                    result=DecisionResult(d["result"]),
                ))

    # --- queries ---

    def get_member(self, member_id: str) -> Optional[Member]:
        return self.members.get(member_id)

    def list_members(self) -> List[Member]:
        return list(self.members.values())

    def get_request(self, request_id: str) -> Optional[RoleChangeRequest]:
        return self.requests.get(request_id)

    def list_requests(self) -> List[RoleChangeRequest]:
        return list(self.requests.values())

    def pending_request_for_target(self, target_id: str) -> Optional[RoleChangeRequest]:
        for r in self.requests.values():
            if r.target_id == target_id and r.status == RequestStatus.PENDING:
                return r
        return None

    # --- mutations ---

    def create_request(
        self, requester_id: str, target_id: str, new_role: Role
    ) -> Tuple[bool, str, Optional[RoleChangeRequest]]:
        requester = self.get_member(requester_id)
        target = self.get_member(target_id)

        if not requester or not target:
            return False, "ไม่พบสมาชิก", None
        if requester_id == target_id:
            return False, "ผู้เสนอและเป้าหมายต้องไม่ใช่คนเดียวกัน", None

        existing = self.pending_request_for_target(target_id)
        if existing:
            return False, f"{target.name} มีคำขอ PENDING อยู่แล้ว (คำขอ {existing.id})", None

        req_id = f"C{self._next_request_seq:02d}"
        self._next_request_seq += 1
        req = RoleChangeRequest(
            id=req_id,
            requester_id=requester_id,
            target_id=target_id,
            new_role=new_role,
        )
        self.requests[req_id] = req
        return True, f"สร้างคำขอ {req_id} สำเร็จ", req

    def submit_vote(
        self, actor_id: str, request_id: str, result: DecisionResult
    ) -> Tuple[bool, str]:
        actor = self.get_member(actor_id)
        req = self.get_request(request_id)

        if not actor:
            return False, "ไม่พบสมาชิก"
        if not req:
            return False, "ไม่พบคำขอ"
        if not actor.active:
            return False, "สมาชิกที่ไม่ active ไม่มีสิทธิ์ลงความเห็น"

        target = self.get_member(req.target_id)
        decision = Decision(request_id=request_id, member_id=actor_id, result=result)
        ok, msg = req.add_decision(decision, target)
        return ok, msg

    def cancel_request(self, actor_id: str, request_id: str) -> Tuple[bool, str]:
        req = self.get_request(request_id)
        if not req:
            return False, "ไม่พบคำขอ"
        return req.cancel(actor_id)

    def eligible_voters(self, request_id: str) -> List[Member]:
        req = self.get_request(request_id)
        if not req:
            return []
        voted_ids = {d.member_id for d in req.decisions}
        return [
            m for m in self.members.values()
            if m.active
            and m.id != req.requester_id
            and m.id != req.target_id
            and m.id not in voted_ids
        ]

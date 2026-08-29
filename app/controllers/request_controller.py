"""RoleChangeRequestController — handles create/vote/cancel and summary view."""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app

from app.models import Role, DecisionResult, RequestStatus

request_bp = Blueprint("req", __name__)


def get_store():
    return current_app.store


def require_actor():
    """Return (actor, None) or (None, redirect_response)."""
    store = get_store()
    actor_id = session.get("actor_id")
    actor = store.get_member(actor_id) if actor_id else None
    if not actor:
        flash("กรุณาเลือกสมาชิกก่อน", "error")
        return None, redirect(url_for("member.index"))
    return actor, None


@request_bp.route("/requests")
def list_requests():
    store = get_store()
    actor_id = session.get("actor_id")
    actor = store.get_member(actor_id) if actor_id else None

    all_reqs = store.list_requests()
    grouped = {
        "PENDING": [],
        "APPROVED": [],
        "REJECTED": [],
        "CANCELLED": [],
    }
    for r in all_reqs:
        grouped[r.status.value].append(r)

    members = {m.id: m for m in store.list_members()}
    return render_template("requests.html", grouped=grouped, members=members, actor=actor)


@request_bp.route("/requests/create", methods=["GET", "POST"])
def create_request():
    actor, redir = require_actor()
    if redir:
        return redir

    store = get_store()
    members = store.list_members()
    roles = list(Role)

    if request.method == "POST":
        target_id = request.form.get("target_id")
        new_role = request.form.get("new_role")

        try:
            role_enum = Role(new_role)
        except ValueError:
            flash("บทบาทไม่ถูกต้อง", "error")
            return render_template("create_request.html", actor=actor, members=members, roles=roles)

        ok, msg, req = store.create_request(actor.id, target_id, role_enum)
        if ok:
            flash(msg, "success")
            return redirect(url_for("req.list_requests"))
        else:
            flash(msg, "error")

    return render_template("create_request.html", actor=actor, members=members, roles=roles)


@request_bp.route("/requests/<request_id>")
def request_detail(request_id):
    store = get_store()
    actor_id = session.get("actor_id")
    actor = store.get_member(actor_id) if actor_id else None

    req = store.get_request(request_id)
    if not req:
        flash("ไม่พบคำขอ", "error")
        return redirect(url_for("req.list_requests"))

    members = {m.id: m for m in store.list_members()}
    eligible = store.eligible_voters(request_id) if req.status == RequestStatus.PENDING else []
    can_vote = actor and actor in eligible
    can_cancel = (
        actor
        and req.status == RequestStatus.PENDING
        and req.requester_id == actor.id
        and not req.decisions
    )

    return render_template(
        "request_detail.html",
        req=req,
        members=members,
        actor=actor,
        eligible=eligible,
        can_vote=can_vote,
        can_cancel=can_cancel,
    )


@request_bp.route("/requests/<request_id>/vote", methods=["POST"])
def vote(request_id):
    actor, redir = require_actor()
    if redir:
        return redir

    result_str = request.form.get("result")
    try:
        result = DecisionResult(result_str)
    except ValueError:
        flash("ผลลงความเห็นไม่ถูกต้อง", "error")
        return redirect(url_for("req.request_detail", request_id=request_id))

    store = get_store()
    ok, msg = store.submit_vote(actor.id, request_id, result)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("req.request_detail", request_id=request_id))


@request_bp.route("/requests/<request_id>/cancel", methods=["POST"])
def cancel_request(request_id):
    actor, redir = require_actor()
    if redir:
        return redir

    store = get_store()
    ok, msg = store.cancel_request(actor.id, request_id)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("req.request_detail", request_id=request_id))

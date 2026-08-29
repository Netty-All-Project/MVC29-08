"""MemberController — handles actor selection and member listing."""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app

member_bp = Blueprint("member", __name__)


def get_store():
    return current_app.store


@member_bp.route("/")
def index():
    store = get_store()
    members = store.list_members()
    actor_id = session.get("actor_id")
    actor = store.get_member(actor_id) if actor_id else None
    return render_template("index.html", members=members, actor=actor)


@member_bp.route("/select-actor", methods=["POST"])
def select_actor():
    actor_id = request.form.get("actor_id")
    store = get_store()
    if store.get_member(actor_id):
        session["actor_id"] = actor_id
    else:
        flash("เลือกสมาชิกไม่ถูกต้อง", "error")
    return redirect(url_for("member.index"))


@member_bp.route("/members")
def list_members():
    store = get_store()
    members = store.list_members()
    actor_id = session.get("actor_id")
    actor = store.get_member(actor_id) if actor_id else None
    return render_template("members.html", members=members, actor=actor)

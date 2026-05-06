from flask import Blueprint, jsonify

from app.repositories import sites as repo

bp = Blueprint("sites", __name__, url_prefix="/api")


@bp.get("/sites")
def list_sites():
    return jsonify({"sites": repo.list_active()})

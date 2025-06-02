from flask import Blueprint, jsonify
from models.category_model import Category

category_bp = Blueprint("category", __name__)

@category_bp.route("/categories", methods=["GET"])
def list_categories():
    categories = Category.all()
    return jsonify([
        {"id": c.id, "name": c.name} for c in categories
    ])

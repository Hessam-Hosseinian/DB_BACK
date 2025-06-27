from flask import Blueprint, jsonify, request
from models.category_model import Category
from utils.auth import admin_required

category_bp = Blueprint("category", __name__)

@category_bp.route("/categories", methods=["GET"])
def list_categories():
    categories = Category.all()
    return jsonify([
        {"id": c.id, "name": c.name, "question_count": c.question_count} 
        for c in categories
    ])

@category_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = Category.find_by_id(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify({
        "id": category.id,
        "name": category.name,
        "question_count": category.question_count
    })

@category_bp.route("/categories", methods=["POST"])
@admin_required
def create_category():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    
    existing = Category.find_by_name(data["name"])
    if existing:
        return jsonify({"error": "Category already exists"}), 409
    
    category = Category(name=data["name"]).save()
    return jsonify({
        "id": category.id,
        "name": category.name,
        "question_count": category.question_count
    }), 201

@category_bp.route("/categories/<int:category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):
    category = Category.find_by_id(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    
    existing = Category.find_by_name(data["name"])
    if existing and existing.id != category_id:
        return jsonify({"error": "Category name already exists"}), 409
    
    if category.update(data["name"]):
        return jsonify({
            "id": category.id,
            "name": category.name,
            "question_count": category.question_count
        })
    return jsonify({"error": "Failed to update category"}), 500

@category_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    category = Category.find_by_id(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    if category.question_count > 0:
        return jsonify({
            "error": "Cannot delete category with existing questions"
        }), 400
    
    if category.delete():
        return "", 204
    return jsonify({"error": "Failed to delete category"}), 500

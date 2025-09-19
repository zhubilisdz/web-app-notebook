from flask import Blueprint, request, jsonify
from datetime import datetime

# 创建蓝图
categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    try:
        from app import db, Category
        categories = Category.query.order_by(Category.created_at.desc()).all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    """创建新分类"""
    try:
        from app import db, Category
        data = request.get_json()
        
        # 检查分类名称是否已存在
        existing_category = Category.query.filter_by(name=data.get('name')).first()
        if existing_category:
            return jsonify({'error': '分类名称已存在'}), 400
        
        category = Category(
            name=data.get('name'),
            description=data.get('description', ''),
            color=data.get('color', '#667eea'),
            icon=data.get('icon', '📁')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify(category.to_dict()), 201
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """更新分类"""
    try:
        from app import db, Category
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        # 检查分类名称是否已被其他分类使用
        if 'name' in data and data['name'] != category.name:
            existing_category = Category.query.filter_by(name=data['name']).first()
            if existing_category:
                return jsonify({'error': '分类名称已存在'}), 400
        
        # 更新分类信息
        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'color' in data:
            category.color = data['color']
        if 'icon' in data:
            category.icon = data['icon']
        
        category.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(category.to_dict())
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除分类"""
    try:
        from app import db, Category
        category = Category.query.get_or_404(category_id)
        
        # 删除分类（会自动解除与笔记的关联）
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': '分类删除成功'})
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>/notes', methods=['GET'])
def get_category_notes(category_id):
    """获取分类下的所有笔记"""
    try:
        from app import db, Category
        category = Category.query.get_or_404(category_id)
        notes = category.notes
        return jsonify([note.to_summary_dict() for note in notes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/notes/<int:note_id>/categories', methods=['POST'])
def add_note_to_category(note_id):
    """将笔记添加到分类"""
    try:
        from app import db, Note, Category
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        category_ids = data.get('category_ids', [])
        
        # 清除现有分类关联
        note.categories.clear()
        
        # 添加新的分类关联
        for category_id in category_ids:
            category = Category.query.get(category_id)
            if category:
                note.categories.append(category)
        
        note.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(note.to_dict())
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建蓝图
notes_bp = Blueprint('notes', __name__)

# 注意：这里我们需要从主应用导入db和模型
# 为了避免循环导入，我们将在需要时导入

@notes_bp.route('/notes', methods=['GET'])
def get_notes():
    """获取所有笔记列表"""
    try:
        from app import db, Note
        notes = Note.query.order_by(Note.updated_at.desc()).all()
        return jsonify([note.to_dict() for note in notes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """获取单个笔记详情"""
    try:
        from app import db, Note
        note = Note.query.get_or_404(note_id)
        return jsonify(note.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/notes', methods=['POST'])
def create_note():
    """创建新笔记"""
    try:
        from app import db, Note
        data = request.get_json()
        
        note = Note(
            title=data.get('title', '无标题笔记'),
            content=data.get('content', '')
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify(note.to_dict()), 201
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """更新笔记"""
    try:
        from app import db, Note
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        note.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(note.to_dict())
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """删除笔记"""
    try:
        from app import db, Note
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'message': '笔记已删除'})
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from routes.ai import ai_bp
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
CORS(app, origins=['http://localhost:5173'], supports_credentials=True)

# 数据模型
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default='无标题笔记')
    content = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联标签和分类
    tags = db.relationship('Tag', secondary='note_tag', back_populates='notes')
    categories = db.relationship('Category', secondary='note_category', back_populates='notes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': [tag.name for tag in self.tags],
            'categories': [category.to_dict() for category in self.categories]
        }
    
    def to_summary_dict(self):
        # 生成摘要（前100个字符）
        snippet = self.content[:100] + '...' if len(self.content) > 100 else self.content
        return {
            'id': self.id,
            'title': self.title,
            'snippet': snippet,
            'created_at': self.created_at.isoformat(),
            'tags': [tag.name for tag in self.tags],
            'categories': [category.to_dict() for category in self.categories]
        }

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    # 关联笔记
    notes = db.relationship('Note', secondary='note_tag', back_populates='tags')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), nullable=False, default='#667eea')  # 十六进制颜色值
    icon = db.Column(db.String(10), nullable=False, default='📁')  # emoji图标
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联笔记
    notes = db.relationship('Note', secondary='note_category', back_populates='categories')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'note_count': len(self.notes)
        }

# 多对多关系表
note_tag = db.Table('note_tag',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

note_category = db.Table('note_category',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# API 路由
@app.route('/api/notes', methods=['GET'])
def get_notes():
    """获取所有笔记列表"""
    try:
        notes = Note.query.order_by(Note.updated_at.desc()).all()
        return jsonify([note.to_dict() for note in notes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """获取单个笔记详情"""
    try:
        note = Note.query.get_or_404(note_id)
        return jsonify(note.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes', methods=['POST'])
def create_note():
    """创建新笔记"""
    try:
        data = request.get_json()
        
        note = Note(
            title=data.get('title', '无标题笔记'),
            content=data.get('content', '')
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify(note.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """更新笔记"""
    try:
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        note.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(note.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """删除笔记"""
    try:
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'message': '笔记已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 分类管理API
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    try:
        categories = Category.query.order_by(Category.created_at.desc()).all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def create_category():
    """创建新分类"""
    try:
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
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 注册蓝图
app.register_blueprint(ai_bp, url_prefix='/api/ai')

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Native 记事本后端服务运行正常',
        'timestamp': datetime.utcnow().isoformat()
    })

# 初始化数据库
def init_db():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        print("数据库初始化完成")

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 启动应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    )
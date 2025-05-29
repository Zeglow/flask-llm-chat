from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
print(f"🔍 正在加载环境变量文件: {env_path}")
load_dotenv(dotenv_path=env_path)

# 立即验证环境变量是否加载
print("🔍 环境变量加载状态:")
print(f"OPENAI_API_KEY: {'已设置' if os.getenv('OPENAI_API_KEY') else '未设置'}")
print(f"OPENAI_ORG_ID: {'已设置' if os.getenv('OPENAI_ORG_ID') else '未设置'}")
print(f"OPENAI_PROJECT_ID: {'已设置' if os.getenv('OPENAI_PROJECT_ID') else '未设置'}")

app = Flask(__name__)

# 修复CORS配置 - 方法1：简化配置
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# 或者使用更详细的配置 - 方法2：
# CORS(app, 
#      origins=["http://localhost:5173"],
#      methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#      allow_headers=["Content-Type", "Authorization"],
#      supports_credentials=True)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/qiuweiyu/LLM-assistant/instance/db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 确保instance目录存在
os.makedirs('/Users/qiuweiyu/LLM-assistant/instance', exist_ok=True)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# ChatHistory表，存储用户对话记录
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text, db.ForeignKey('user.id'))
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('chat_history', lazy=True))

# 登录加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 添加OPTIONS请求处理
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

@app.route('/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return jsonify(routes)

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return jsonify({'message': 'Login successful'})
        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/signup', methods=['POST'])
def api_signup():
    try:
        data = request.json

        # 数据验证
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # 获取原始邮箱+密码
        email = data.get('email')
        password = data.get('password')

        # 验证必填字段
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        if not password:
            return jsonify({'message': 'Password is required'}), 400
        
        # 验证邮箱格式
        if '@' not in email or '.' not in email:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # 验证密码长度
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        # 验证用户是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'User already exists'}), 400
        
        # 验证后再hash密码，创建新用户
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        print("🟢 收到注册请求")
        return jsonify({'message': 'User created successfully'})
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    try:
        data = request.json
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({'message': 'Prompt is required'}), 400

        gpt_response = run_openai_chat(prompt)

        new_chat = ChatHistory(
            user_id=current_user.id,
            prompt=prompt,
            response=gpt_response
        )
        db.session.add(new_chat)
        db.session.commit()

        return jsonify({'response': gpt_response})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    try:
        history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).all()
        result = [{
            'prompt': h.prompt,
            'response': h.response,
            'timestamp': h.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for h in history]
        return jsonify(result)
    except Exception as e:
        print(f"History error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    try:
        logout_user()
        return jsonify({'message': 'Logged out successfully'})
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/')
def index():
    return jsonify({'message': 'API is running'})

# OpenAI 客户端配置
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID"),
    project=os.getenv("OPENAI_PROJECT_ID")
)

def run_openai_chat(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Sorry, I encountered an error processing your request."

if __name__ == '__main__':
    print("🔑 API:", os.getenv("OPENAI_API_KEY"))
    print("🏢 ORG:", os.getenv("OPENAI_ORG_ID"))
    print("📁 PROJ:", os.getenv("OPENAI_PROJECT_ID"))

    with app.app_context():
        db.create_all()
        print("✅ Database and tables created!")
        print("Tables:", list(db.metadata.tables.keys()))
        
        # 验证数据库文件
        db_path = '/Users/qiuweiyu/LLM-assistant/instance/db.sqlite'
        if os.path.exists(db_path):
            print(f"✅ 数据库文件存在: {db_path}")
            print(f"文件大小: {os.path.getsize(db_path)} 字节")
        else:
            print("❌ 数据库文件不存在")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
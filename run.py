from flask import Flask
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
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/qiuweiyu/LLM-assistant/instance/db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭警告

# 确保instance目录存在
os.makedirs('/Users/qiuweiyu/LLM-assistant/instance', exist_ok=True)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)  # 添加nullable=False
    password = db.Column(db.String(100), nullable=False)  # 添加nullable=False

#ChatHistory表，存储用户对话记录
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Text, db.ForeignKey('user.id'))
    prompt = db.Column(db.Text, nullable = False)
    response = db.Column(db.Text, nullable = False)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)

    user = db.relationship('User', backref = db.backref('chat_history', lazy = True))

# 登录加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        # 检查用户是否已存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return 'User already exists'
        
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    if request.method == "POST":
        user_input = request.form['prompt']

        gpt_response = run_openai_chat(user_input)

        #store into db
        new_chat = ChatHistory(
            user_id = current_user.id,
            prompt = user_input,
            response = gpt_response
        )
        db.session.add(new_chat)
        db.session.commit()

        return redirect(url_for('dashboard')) #避免刷新重复提交
    
    # GET，显示所有历史记录
    history = ChatHistory.query.filter_by(user_id = current_user.id).order_by(ChatHistory.timestamp.desc()).all()
    return render_template('dashboard.html', history = history)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),         # 你的 sk-proj- 开头的 token
    organization=os.getenv("OPENAI_ORG_ID"),     # 从控制台复制 organization ID
    project=os.getenv("OPENAI_PROJECT_ID")        # 从控制台复制 project ID
)

def run_openai_chat(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    print("🔑 API:", os.getenv("OPENAI_API_KEY"))
    print("🏢 ORG:", os.getenv("OPENAI_ORG_ID"))
    print("📁 PROJ:", os.getenv("OPENAI_PROJECT_ID"))

    with app.app_context():
        # 删除重复的db.create_all()调用
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
    
    app.run(debug=True)
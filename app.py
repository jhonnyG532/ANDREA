from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cumple-andrea-2024-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cumple.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order_num = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200))
    order_num = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)

with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='winny').first():
        admin = Admin(username='winny', password_hash='scrypt:32768:8:1$qXKMaLWCsrjBR8xC$6ef287237174e83d5794695ed86313ecc50a423fb95545f7030de74b179d8fdc8f90f5d364006afbb2491326b5fca480de3cb93828ef89db63918c52610b6124')
        db.session.add(admin)
        
        if Message.query.count() == 0:
            messages = [
                Message(title="Para ti, Andrea...", content="Hoy es tu día, y quiero que sepas lo especial que eres para mí.", order_num=1),
                Message(title="Eres única", content="Tu risa es contagiosa, tu bondad infinita, y tu corazón超大.", order_num=2),
                Message(title="Mis deseos", content="🌟 Momentos llenos de alegría\n💪 Fuerza para tus sueños\n❤️ Amor en cada paso\n🎭 Aventuras que te hagan feliz", order_num=3),
                Message(title="Con cariño", content="Gracias por ser mi hermana, mi amiga, mi confidente. ¡Te quiero mucho!", order_num=4),
            ]
            for msg in messages:
                db.session.add(msg)
        
        if Config.query.count() == 0:
            configs = [
                Config(key='nombre', value='Andrea'),
                Config(key='titulo', value='¡Feliz Cumpleaños!'),
                Config(key='subtitulo', value='Para ti, con todo mi cariño ✨'),
                Config(key='color_primary', value='#ff6b9d'),
                Config(key='color_secondary', value='#c44569'),
                Config(key='color_gold', value='#ffd700'),
            ]
            for cfg in configs:
                db.session.add(cfg)
        
        db.session.commit()

@app.route('/')
def home():
    nombre = Config.query.filter_by(key='nombre').first()
    titulo = Config.query.filter_by(key='titulo').first()
    subtitulo = Config.query.filter_by(key='subtitulo').first()
    messages = Message.query.order_by(Message.order_num).all()
    photos = Photo.query.order_by(Photo.order_num).all()
    
    return render_template('index.html',
                         nombre=nombre.value if nombre else 'Andrea',
                         titulo=titulo.value if titulo else '¡Feliz Cumpleaños!',
                         subtitulo=subtitulo.value if subtitulo else '',
                         messages=messages,
                         photos=photos)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/panel')
@login_required
def admin_panel():
    nombre = Config.query.filter_by(key='nombre').first()
    titulo = Config.query.filter_by(key='titulo').first()
    subtitulo = Config.query.filter_by(key='subtitulo').first()
    messages = Message.query.order_by(Message.order_num).all()
    photos = Photo.query.order_by(Photo.order_num).all()
    
    return render_template('admin/panel.html',
                         nombre=nombre.value if nombre else '',
                         titulo=titulo.value if titulo else '',
                         subtitulo=subtitulo.value if subtitulo else '',
                         messages=messages,
                         photos=photos)

@app.route('/admin/config', methods=['POST'])
@login_required
def admin_config():
    for key in ['nombre', 'titulo', 'subtitulo']:
        value = request.form.get(key)
        config = Config.query.filter_by(key=key).first()
        if config:
            config.value = value
        else:
            config = Config(key=key, value=value)
            db.session.add(config)
    
    db.session.commit()
    flash('Configuración guardada', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/upload', methods=['POST'])
@login_required
def admin_upload():
    if 'file' not in request.files:
        flash('No se encontró archivo', 'error')
        return redirect(url_for('admin_panel'))
    
    file = request.files['file']
    caption = request.form.get('caption', '')
    
    if file.filename == '':
        flash('No seleccionaste ningún archivo', 'error')
        return redirect(url_for('admin_panel'))
    
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        max_order = db.session.query(db.func.max(Photo.order_num)).scalar() or 0
        photo = Photo(filename=filename, caption=caption, order_num=max_order + 1)
        db.session.add(photo)
        db.session.commit()
        
        flash('Foto subida correctamente', 'success')
    else:
        flash('Formato no permitido', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/photo/<int:id>')
@login_required
def admin_delete_photo(id):
    photo = Photo.query.get_or_404(id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
    except:
        pass
    db.session.delete(photo)
    db.session.commit()
    flash('Foto eliminada', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/message/add', methods=['POST'])
@login_required
def admin_add_message():
    title = request.form.get('title')
    content = request.form.get('content')
    max_order = db.session.query(db.func.max(Message.order_num)).scalar() or 0
    msg = Message(title=title, content=content, order_num=max_order + 1)
    db.session.add(msg)
    db.session.commit()
    flash('Mensaje agregado', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/message/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_message(id):
    msg = Message.query.get_or_404(id)
    msg.title = request.form.get('title')
    msg.content = request.form.get('content')
    msg.order_num = request.form.get('order_num', 0, type=int)
    db.session.commit()
    flash('Mensaje actualizado', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/message/delete/<int:id>')
@login_required
def admin_delete_message(id):
    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Mensaje eliminado', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/message/reorder', methods=['POST'])
@login_required
def admin_reorder_messages():
    order_list = request.form.getlist('order[]')
    for i, msg_id in enumerate(order_list):
        msg = Message.query.get(msg_id)
        if msg:
            msg.order_num = i
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/photo/reorder', methods=['POST'])
@login_required
def admin_reorder_photos():
    order_list = request.form.getlist('order[]')
    for i, photo_id in enumerate(order_list):
        photo = Photo.query.get(photo_id)
        if photo:
            photo.order_num = i
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/change-password', methods=['POST'])
@login_required
def admin_change_password():
    current = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    confirm = request.form.get('confirm_password')
    
    admin = Admin.query.filter_by(username='admin').first()
    
    if not check_password_hash(admin.password_hash, current):
        flash('Contraseña actual incorrecta', 'error')
        return redirect(url_for('admin_panel'))
    
    if new_pass != confirm:
        flash('Las contraseñas no coinciden', 'error')
        return redirect(url_for('admin_panel'))
    
    admin.password_hash = generate_password_hash(new_pass)
    db.session.commit()
    flash('Contraseña actualizada', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
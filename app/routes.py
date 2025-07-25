from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.forms import RegistrationForm, LoginForm, UploadForm
from app.models import User, Image
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.tasks import process_image

# Конфигурация загрузки файлов
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('gallery'))
        flash('Неправильное имя пользователя или пароль', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            img = Image(
                filename=filename,
                original_url=f'static/uploads/{filename}',
                user_id=current_user.id
            )
            db.session.add(img)
            db.session.commit()

            flash('Изображение успешно загружено!', 'success')
            return redirect(url_for('gallery'))
        else:
            flash('Допустимые форматы: png, jpg, jpeg, gif', 'danger')
    return render_template('upload.html', form=form)


@app.route('/gallery')
@login_required
def gallery():
    images = current_user.images.order_by(Image.timestamp.desc()).all()
    return render_template('gallery.html', images=images)


@app.route('/process/<int:image_id>')
@login_required
def process(image_id):
    img = Image.query.get_or_404(image_id)
    if img.user_id != current_user.id:
        abort(403)
    process_image.delay(image_id)
    flash('Изображение отправлено на обработку. Обновите страницу через некоторое время.', 'info')
    return redirect(url_for('gallery'))
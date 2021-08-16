import json
from datetime import datetime
from urllib.parse import urlparse
import os
import requests
import vk


from flask import Flask, render_template, redirect, request, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.ticket import Ticket
from data.form import Form
from data.user import User

UPLOAD_FOLDER = 'content'

try:
    os.mkdir(UPLOAD_FOLDER)
except FileExistsError:
    pass

try:
    os.mkdir('db')
except FileExistsError:
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ticket-webapp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)
# run_with_ngrok(app)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    schools = db_sess.query(User).filter(User.status == 'ok')
    ticket = Ticket()
    if request.method == 'POST':
        ticket.school = request.form.get('school')
        ticket.form = request.form.get('form')
        ticket.milk = request.form.get('milk')
        ticket.dinner = request.form.get('dinner')
        ticket.mal_ob = request.form.get('mal_ob')
        ticket.af_dinner = request.form.get('af_dinner')
        db_sess.add(ticket)
        db_sess.commit()
        return redirect('/')
    return render_template('index.html', title='Подача талона',
                           schools=schools)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_sess = db_session.create_session()
    schools = db_sess.query(User).filter(User.status == 'ok')
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.school == request.form.get('school'), User.status == 'ok').first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect("/school_panel")
        return render_template('login.html', message="Неправильный логин или пароль")
    return render_template('login.html', schools=schools)


@app.route('/register_school', methods=['GET', 'POST'])
def register_school():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.school == request.form.get('school')).first():
            return render_template('registration.html', message="Ты уже зареган")
        elif request.form.get('password') != request.form.get('check_password'):
            return render_template('registration.html', message="Не совпадают")
        else:
            user = User(school=request.form.get('school'), status='bad')
            user.set_password(request.form.get('password'))
            db_sess.add(user)
            db_sess.commit()
            return redirect('/')
    return render_template('register_school.html')


@app.route('/sumbit_status/<schoolname>', methods=['GET', 'POST'])
def sumbit_status(schoolname):
    db_sess = db_session.create_session()
    school = db_sess.query(User).filter(User.school == schoolname).first()
    school.status = 'ok'
    db_sess.commit()
    return redirect('/admin')


@app.route('/delete_school/<schoolname>', methods=['GET', 'POST'])
def delete_school(schoolname):
    db_sess = db_session.create_session()
    school = db_sess.query(User).filter(User.school == schoolname).first()
    db_sess.delete(school)
    db_sess.commit()
    return redirect('/admin')


@app.route('/get_len', methods=['GET', 'POST'])
def get_len():
    db_sess = db_session.create_session()
    result = {}
    for i in db_sess.query(Form).filter(request.form.get('school') == Form.school):
        result[i.form] = i.form
    return json.dumps(result)


@app.route('/see_menu', methods=["POST", "GET"])
def see_menu():
    url = urlparse(request.url)
    req = f'https://oauth.vk.com/access_token?client_id=7921944&client_secret=YGiSOZTjRyp0vIHA61Uy&redirect_uri=https://for-school-rus.herokuapp.com/see_menu&{url.query}'
    access_token = requests.get(req).json()['access_token']

    session = vk.Session(access_token=access_token)
    api = vk.API(session, timeout=60)
    wall_content = api.wall.get(domain='fabrika_s_p', count=1, offset=1, v=5.131)
    post_text = wall_content['items'][0]['text']
    time = int(wall_content['items'][0]['date'])
    time = datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    images_urls = []

    for photo in wall_content['items'][0]['attachments']:
        for sizes in photo['photo']['sizes']:
            if sizes['type'] == 'w':
                images_urls.append(sizes['url'])

    i = 0
    for img in images_urls:
        with open(f"{UPLOAD_FOLDER}/qwerty{i}.jpg", 'wb') as file:
            file.write(requests.get(img).content)
        i += 1
    images = os.listdir(UPLOAD_FOLDER)
    return render_template('see_menu.html', title='Посмотреть меню', images=images, UPLOAD_FOLDER=UPLOAD_FOLDER,
                           post_text=post_text, time=time)


@app.route('/content/<name>', methods=["POST", "GET"])
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/school_panel', methods=["POST", "GET"])
def school_panel():
    db_sess = db_session.create_session()
    all_tickets = db_sess.query(Ticket).filter(current_user.school == Ticket.school)
    return render_template('school_panel.html', title='Общие данные', all_tickets=all_tickets)


@app.route('/admin', methods=["POST", "GET"])
def admin():
    db_sess = db_session.create_session()
    all_school = db_sess.query(User).all()
    return render_template('admin.html', all_school=all_school)


@app.route('/add_form', methods=["POST", "GET"])
def add_form():
    db_sess = db_session.create_session()
    form = Form()
    if request.method == 'POST':
        form.form = request.form.get('form')
        form.school = current_user.school
        db_sess.add(form)
        db_sess.commit()
        return redirect('/add_form')
    all_forms = db_sess.query(Form).filter(Form.school == current_user.school)
    return render_template('add_form.html', title='Общие данные', all_forms=all_forms)


@app.route('/clear_talons', methods=['GET', 'POST'])
def clear_talons():
    db_sess = db_session.create_session()
    db_sess.query(Ticket).filter(Ticket.school == current_user.school).delete()
    db_sess.commit()
    return redirect('/school_panel')


@app.route('/clear_forms', methods=['GET', 'POST'])
def clear_forms():
    db_sess = db_session.create_session()
    db_sess.query(Form).filter(Form.school == current_user.school).delete()
    db_sess.commit()
    return redirect('/add_form')


if __name__ == '__main__':
    db_session.global_init('db/tickets.sqlite')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(debug=True)

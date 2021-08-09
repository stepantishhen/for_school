import os
import vk
import requests
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template, redirect, abort, request, flash, send_from_directory
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename

from data.talons import Talons, Forms
from data import db_session

UPLOAD_FOLDER = os.path.abspath('content')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'for-school-app-secret-key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# run_with_ngrok(app)


@app.route('/', methods=["POST", "GET"])
def index():
    db_sess = db_session.create_session()
    talon = Talons()
    if request.method == 'POST':
        talon.form = request.form.get('form')
        talon.milk = request.form.get('milk')
        talon.dinner = request.form.get('dinner')
        talon.mal_ob = request.form.get('mal_ob')
        talon.af_dinner = request.form.get('af_dinner')
        db_sess.add(talon)
        db_sess.commit()
        return redirect('/')

    all_talons = db_sess.query(Talons).order_by(Talons.created_date)
    all_forms = db_sess.query(Forms).order_by(Forms.form)

    return render_template('index.html', title='Подача талона', all_talons=all_talons,
                           all_forms=all_forms)


@app.route('/see_menu', methods=["POST", "GET"])
def see_menu():
    url = urlparse(request.url)
    req = f'https://oauth.vk.com/access_token?client_id=7921944&client_secret=YGiSOZTjRyp0vIHA61Uy&redirect_uri=https://for-school-rus.herokuapp.com/see_menu&{url.query}'
    access_token = requests.get(req).json()['access_token']
    text, ts = getting_menu(access_token)
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('see_menu.html', dir=UPLOAD_FOLDER, files=files,
                           text=text, ts=ts)


@app.route('/content/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/admin', methods=["POST", "GET"])
def admin():
    db_sess = db_session.create_session()
    all_talons = db_sess.query(Talons).order_by(Talons.created_date)
    return render_template('admin.html', title='Общие данные', all_talons=all_talons)


@app.route('/add_form', methods=["POST", "GET"])
def add_form():
    db_sess = db_session.create_session()
    form = Forms()
    if request.method == 'POST':
        form.form = request.form.get('form')
        db_sess.add(form)
        db_sess.commit()
        return redirect('/add_form')
    all_forms = db_sess.query(Forms).order_by(Forms.form)
    return render_template('add_form.html', title='Общие данные', all_forms=all_forms)


@app.route('/clear_talons', methods=['GET', 'POST'])
def clear_talons():
    db_sess = db_session.create_session()
    db_sess.query(Talons).delete()
    db_sess.commit()
    return redirect('/admin')


@app.route('/clear_forms', methods=['GET', 'POST'])
def clear_forms():
    db_sess = db_session.create_session()
    db_sess.query(Forms).delete()
    db_sess.commit()
    return redirect('/add_form')


def getting_menu(access_token):
    session = vk.Session(access_token=access_token)
    api = vk.API(session, timeout=60)
    wall_content = api.wall.get(domain='fabrika_s_p', count=1, offset=1, v=5.131)

    post_text = wall_content['items'][0]['text']
    ts = int(wall_content['items'][0]['date'])
    ts = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    images_urls = []
    for photo in wall_content['items'][0]['attachments']:
        for sizes in photo['photo']['sizes']:
            if sizes['type'] == 'w':
                images_urls.append(sizes['url'])
    i = 0
    for img in images_urls:
        with open(f"{UPLOAD_FOLDER}\qwerty{i}.jpg", 'wb') as file:
            file.write(requests.get(img).content)
        i += 1
    return post_text, ts


if __name__ == '__main__':
    db_session.global_init('db/talons.sqlite')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run()

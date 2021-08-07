from flask import Flask, render_template, redirect, abort, request
from flask_ngrok import run_with_ngrok
from data.talons import Talons, Forms
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'for-school-app-secret-key'
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


@app.route('/clear_forms', methods=['GET', 'POST'])
def clear_forms():
    db_sess = db_session.create_session()
    db_sess.query(Forms).delete()
    db_sess.commit()
    return redirect('/add_form')


@app.route('/clear_talons', methods=['GET', 'POST'])
def clear_talons():
    db_sess = db_session.create_session()
    db_sess.query(Talons).delete()
    db_sess.commit()
    return redirect('/admin')


if __name__ == '__main__':
    db_session.global_init('db/talons.sqlite')
    # app.run(port=8080, host='127.0.0.1', debug=True)
    app.run()

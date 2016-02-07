import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing


DATABASE = os.path.join(os.path.dirname(__file__), 'static', 'MyFlask.db')
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def check_user(username, password=''):
    """
    Looks in the database for a user with the specified attributes.
    Returns True if found.

    :param username: The main attribute to look for.
    :param password: Optional.
    :return: True if one or more users with the exact attributes are found
    """
    if not password == '':
        query = 'select count(*) from users where username = ? and password = ?'
        cur = g.db.execute(query, [username, password])
    else:
        query = 'select count(*) from users where username = ?'
        cur = g.db.execute(query, [username])
    data = int(cur.fetchone()[0])
    return data > 0


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select e.title, u.username, e.text from entries e, users u where u.id = e.owner order by u.id desc limit 10')
    entries = [dict(title=row[0], owner=row[1], text=row[2]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text, owner) values (?, ?, (	select id from users where username = ?));',
                 [request.form['title'], request.form['text'], session['username']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if not check_user(request.form['username'], request.form['password']):
            error = 'Invalid login credentials'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    init_db()
    app.run()

import mysql.connector
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash


DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    connection = mysql.connector.connect(user='admin', password='ilionxpython',
                                   host='mysql-python.tryfirst.svc.tutum.io',
                                   port='12345',
                                   database='db')
    connection.autocommit = True
    return connection


def check_user(username, password=''):
    """
    Looks in the database for a user with the specified attributes.
    Returns True if found.

    :param username: The main attribute to look for.
    :param password: Optional.
    :return: True if one or more users with the exact attributes are found
    """
    cur = g.db.cursor(buffered=True)
    if not password == '':
        cur.execute("select count(*) from users where user_username = %s and user_password = %s", (username, password))
    else:
        cur.execute("select count(*) from users where user_username = %s", (username,))
    for row in cur: data = row[0]
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
    cur = g.db.cursor(buffered=True)
    cur.execute('select e.entry_title, u.user_username, e.entry_text from entries e, users u where u.user_id = e.entry_owner order by u.user_id desc limit 10')
    entries = [dict(title=row[0], owner=row[1], text=row[2]) for row in cur]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.cursor()
    cur.execute('insert into entries (entry_title, entry_text, entry_owner) values (%s, %s, (	select user_id from users where user_username = %s));',
                (request.form['title'], request.form['text'], session['username']))
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if not request.form['password'] == request.form['password2']:
            error = 'Passwords do not match'
        elif check_user(request.form['username']):
            error = 'Account already exists'
        else:
            g.db.cursor().execute('insert into users (user_username, user_password) values (%s, %s)',
                        (request.form['username'], request.form['password']))
            if not check_user(request.form['username'], request.form['password']):
                error = 'An error occurred while creating your account'
            else:
                flash('New user created, you can now post messages')
                session['logged_in'] = True
                session['username'] = request.form['username']
                return redirect(url_for('show_entries'))
    return render_template('register.html', error=error)


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
    app.run()

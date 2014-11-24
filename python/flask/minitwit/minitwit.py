from _hashlib import openssl_md5
from contextlib import closing

import hashlib
from datetime import datetime
import time
from flask.app import Flask
import sqlite3
from flask import g, session, redirect, abort, request
from flask.helpers import url_for, flash
from flask.templating import render_template
from werkzeug.security import generate_password_hash, check_password_hash

__author__ = 'billy'
# -*- coding: utf-8 -*-
'''
    MiniTwit
    ~~~~~~~~

    A microblogging applicatoin written with Flask and sqlite3.
'''

# configuration
DATABASE = '../../minitwit.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

# create our little applicatoin 
app = Flask(__name__)
app.config.from_object(__name__)    # read configuration from this file
app.config.from_envvar('MINITWIT_SETTING', silent=True)

def connect_db():
    """
    :return: a new connection to the database
    """
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    """
    Creates the database tables.
    """
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    """
    Queries the database and returns a list of dictionaries.
    :param query:
    :param args:
    :param one:
    :return:
    """
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
                for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """
    Convenience method to look up the id for a username.
    :param username:
    :return:
    """
    rv = g.db.execute('select user_id from user where username=?', [username]).fetchone()
    return rv[0] if rv else None

def format_datetime(timestamp):
    """
    Format a timestamp for display.
    :param timestamp:
    :return:
    """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

def gravatar_url(email, size=80):
    """
    Return the gravatar image for the given email address.
    :param email:
    :param size:
    :return:
    """
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % (
        hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

@app.before_request
def before_request():
    """
    Make sure we are connected to the database each request and look up the current user so that we know he's there.
    :return:
    """
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id=?', [session['user_id']], one=True)

@app.teardown_request
def teardown_request(exception):
    """
    Closes the database again at the end of the request.
    :param exception:
    :return:
    """
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def timeline():
    """
    Show a users timeline of if no user is logged in it will redirect to the public timeline. This timeline shows
    the user's messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    query = '''
        select message.*, user.*
          from message, user
         where message.author_id = user.user_id
               and (
                user.user_id = ?
                or user.user_id in (select whom_id from follower where who_id =?)
               )
         order by message.pub_date desc limit ?'''
    return render_template('timeline.html',
                           messages=query_db(query, [session['user_id'], session['user_id'], PER_PAGE]))

@app.route('/public')
def public_timeline():
    """
    Displays the latest messages of all users.
    :return:
    """
    query = '''
        select message.*, user.*
          from message, user
         where message.author_id = user.user_id
         order by message.pub_date desc limit ?
    '''
    return render_template('timeline.html', messages=query_db(query, [PER_PAGE]))

@app.route('/<username>')
def user_timeline(username):
    '''
    Display's a users tweets.
    :param username:
    :return:
    '''
    profile_user = query_db('select * from user where username=?', [username], one=True)

    if profile_user is None:
        abort(404)

    followed = False
    if g.user:
        followed = query_db(''' select 1 from follower where follower.who_id =? and follower.whom_id=?''',
                            [session['user_id'], profile_user['user_id']], one=True) is not None

    query = '''
        select message.*, user.*
          from message, user
         where user.user_id = message.author_id
               and user.user_id = ?
         order by message.pub_date desc limit ? '''
    return render_template('timeline.html', messages=query_db(query, [profile_user['user_id'], PER_PAGE]),
                           followed=followed, profile_user=profile_user)

@app.route('/<username>/follow')
def follow_user(username):
    '''
    Adds the current user as follower of the given user.
    :param username:
    :return:
    '''
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    g.db.execute('insert into follower (who_id, whom_id) values (?, ?)',
                 [session['user_id'], whom_id])
    g.db.commit()
    flash('You are not following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))

@app.route('/<username>/unfollow')
def unfollow_user(username):
    '''
    Removes the current user as follower of the given user.
    :param username:
    :return:
    '''
    if not g.user:
        abort(404)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    g.db.execute('delete from follower where who_id=? and whom_id=?',
                 [session['user_id'], whom_id])
    g.db.commit()
    flash('You are no longer following "%s".' % username)
    return redirect(url_for('user_timeline', username=username))

@app.route('/add_message', methods=['POST'])
def add_message():
    '''
    Registers a new message for the user.
    :return:
    '''
    if 'user_id' not in session:
        abort(404)
    if request.form['text']:
        g.db.execute('''insert into message(author_id, text, pub_date) values(?, ?, ?)''',
            (session['user_id'], request.form['text'], int(time.time())))
        g.db.commit()
        flash('Your message was recorded.')
    return redirect(url_for('timeline'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Logs the user in.
    :return:
    '''
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where username = ?''',
                        [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in.')
            session['user_id'] = user['user_id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)

@app.route('/request', methods=['GET', 'POST'])
def register():
    '''
    Registers the user.
    :return:
    '''
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or '@' not in request.form['email']:
            error = 'You have to enter a valid email address.'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is alredy taken'
        else:
            g.db.execute('''insert into user (username, email, pw_hash) values (?, ?, ?)''',
                         [request.form['username'], request.form['email'],
                          generate_password_hash(request.form['password'])])
            g.db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    '''
    Logs the user out.
    :return:
    '''
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))

# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

if __name__ == '__main__':
    init_db()
    app.run()
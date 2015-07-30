# coding:utf-8

import os
# from sqlite3 import dbapi2 as sqlite3
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, make_response

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'mini_blog.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('MINI_BLOG_SETTINGS', silent=True)


def connect_db():
    ''' connects to the specific  database.  '''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


# FIXME,FIND OUT why

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    db = get_db()
    # with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    ''' http://www.pythondoc.com/flask/tutorial/dbinit.html?highlight=executescript
    from contextlib import closing
    closing() 助手函数允许我们在 with 块中保持数据库连接可用。
    应用对象的open_resource() 方法在其方框外也支持这个功能，因此可以在 with 块中直接使用。
    这个函数从资源位置（你的 flaskr 文 件夹）中打开一个文件，并且允许你读取它。
    '''


@app.teardown_appcontext
def close_db(error):
    ''' close the database again at the end of the request '''
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc ')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title,text) values (?,?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('new entry was successfully posted')
    return redirect(url_for('show_entries'))







from flask import Flask
from flask import request
from flask import g
from flask import jsonify
from flask import redirect
from datetime import datetime
import socket
import sqlite3

app = Flask(__name__)

DATABASE = 'tasks.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Close connection to database"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Query the database with given arguments"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def index():
    """Index Page"""
    return 'Index Page'


@app.route('/todolist', methods=['GET', 'POST'])
def todolist():
    """To-do list view based on given HTML method"""
    if request.method == 'POST':
        return todolist_post()
    else:
        return todolist_get()


def todolist_get():
    """To-do list view with 'GET' HTML method,
    counts done and not done tasks and returns
    HTML with <pre> tag and formatted list of 
    database entries"""
    done_counter = 0
    notdone_counter = 0
    todolist_return = "<pre>"
    for task in query_db('select * from Tasks'):
        if task[1] == 1:
            todolist_return += "[X] " + task[0] + "\n"
            done_counter += 1
        else:
            todolist_return += "[ ] " + task[0] + "\n"
            done_counter += 1
    todolist_return += "</pre>"
    task_sum = done_counter + notdone_counter
    header = ("To-do list (" +
             str(task_sum) +
             " tasks, " + str(done_counter) +
             " done, " + str(notdone_counter) +
             " to do)" + "\n")
    todolist_return = header + todolist_return
    return todolist_return


def todolist_post():
    """Gets JSON and inserts it into database
    when using HTML 'POST' method,
    returns json with last row id"""
    content = request.get_json()
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO
                      Tasks(Name, Status, IP, Created)
                      VALUES(?,?,?,?)""",
                      (content["title"],
                      bool(content["done"]),
                      socket.gethostbyname(socket.gethostname()),
                      datetime.now()))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify(task_id=cursor.lastrowid)


@app.route('/todolist/<int:post_id>', methods=['PATCH'])
def patch_todolist(post_id):
    """Patches database entry when using 'PATCH' HTML method
    and entry ID, takes json with title, status, or both on input,
    and replaces adequate entry"""
    content = request.get_json()
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("""SELECT Count(*) FROM Tasks""")
    count = cursor.fetchall()
    if count[0][0] < post_id:
        return ("", 404)
    if "title" in content and "done" in content:
        cursor.execute("""UPDATE Tasks
                          SET Name = ?, Status = ?
                          WHERE rowid = ?""",
                          (content["title"],
                          bool(content["done"]),
                          post_id))
        connection.commit()
        cursor.close()
        connection.close()
        return ('', 204)
    elif "title" in content:
        cursor.execute("""UPDATE Tasks
                          SET Name = ? WHERE rowid = ?""",
                          (content["title"], post_id))
        connection.commit()
        cursor.close()
        connection.close()
        return ('', 204)
    elif "done" in content:
        cursor.execute("""UPDATE Tasks
                          SET Status = ? WHERE rowid = ?""",
                          (bool(content["done"]), post_id))
        connection.commit()
        cursor.close()
        connection.close()
        return ('', 204)
    else:
        return ('', 404)


@app.route('/todolist/<int:post_id>', methods=['GET'])
def todolist_get_id(post_id):
    """Takes entry ID as argument, and returns JSON with
    title, status, ip address of author and creation date"""
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("""SELECT Count(*) FROM Tasks""")
    count = cursor.fetchall()
    if count[0][0] < post_id:
        return ("", 404)
    cursor.close()
    for task in query_db("""SELECT * FROM
                            Tasks
                            WHERE rowid = ?""",
                            str(post_id)):
        return jsonify(title=str(task[0]),
                       done=bool(task[1]),
                       author_ip=str(task[2]),
                       created_date=str(task[3]))


@app.route('/google')
def get_google_query():
    """Redirects to google search on given query string,
    eg. '/google?co=findit' redirects to google search page
    with query 'findit'"""
    co = request.args.get('co')
    url = "http://www.google.pl/search?q=" + co
    return redirect(url, code=302)

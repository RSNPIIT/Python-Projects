from flask import Flask as fl,request ,make_response ,send_from_directory, render_template, Response, session, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import uuid
import pandas as pd

# Static variables
TMP = 'templates'
STT = 'static'
VAL = 'RSNPIIT'
ITM = [20 , 30 , 35 , 40]

# Creating the Database
from extensions import db

# Creating a Flask Instance
app = fl(
    __name__,
    template_folder = TMP,
    static_folder = STT,
    static_url_path = '/'
)
# This is configuring the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./testdb.db'
app.secret_key = os.urandom(24)

# Initializing the database -> This is similar to git init and then migrate it 
db.init_app(app)
migrate = Migrate(app , db)

# Common data function used once
def common_data():
    return {
        'myname': VAL,
        'myvalue': 9.8,
        'myitem': ITM
    }

# The '/' means the root path of the file
@app.route('/')
def index():
    return render_template(
        template_name_or_list = 'index.html',
        message = "Session Data Set",
        **common_data()
    )

# Getting a stored session data for Flask to remember
@app.route('/set_data')
def set_data():
    session['name'] = "RS"
    session['data'] = "Hello World"

    return render_template(
        template_name_or_list = 'index.html',
        message = "Session Data Set",
        **common_data()
    )

# Returning the stored cached data
@app.route('/get_data')
def get_data():
    if 'name' in session.keys() and 'data' in session.keys():
        name = session['name']
        other = session['data']
        return render_template(
            template_name_or_list = 'index.html',
            message = f"Priviet Tovarisch Ich Heisse {name} und mein message ist {other}",
            **common_data()
        )
    else:
        return render_template(
            template_name_or_list = 'index.html',
            message = "No Session Found",
            **common_data()
        )

# Erasing the stored session data
@app.route('/clear_data')
def clear_session():
    session.clear()
    return render_template(
        template_name_or_list = 'index.html',
        message = "Session Data Erased",
        **common_data()
    )

# We set with the cookies here
@app.route('/set_cookie')
def set_cookie():
    res = make_response(
        render_template(
            template_name_or_list = 'index.html',
            message = "Cookie Set Successfully",
            **common_data()
        )
    )
    res.set_cookie(
        key = "Cookie_Name_CKK22",
        value = "Cookie_Val_key_JibJ"
    )
    return res

# Returning the cookie here
@app.route('/get_cookie')
def get_cookie():
    all_v = request.cookies['Cookie_Name_CKK22']
    return render_template(
        template_name_or_list = 'index.html',
        message = f"Got the Message it is :-> {all_v}",
        **common_data()
    )

# Erasing the Cookie here
@app.route('/erase_cookie')
def erase_cookie():
    res = make_response(
        render_template(
            template_name_or_list = 'index.html',
            message = "Cookie Erased",
            **common_data()
        )
    )
    res.set_cookie(
        key = "Cookie_Name_CKK22",
        value = "Cookie_Val_key_JibJ",
        expires = 0
    )
    return res

# Making the Login Route
@app.route(
    rule = '/login',
    methods = ['GET' , 'POST']
)
def login():
    if request.method == 'GET':
        return render_template(
            template_name_or_list = 'form.html'
        )
    elif request.method == 'POST':
        user = request.form.get('username')
        psw = request.form.get('password')

        if user == VAL and psw == '1Ramrup@S':
            flash(f"Hello {VAL} you have successfully authenticated")
        else:
            flash("Login Failed")
        return redirect(
            url_for('login')
        )

# The other Page route
@app.route(
    rule = '/other',
    methods = ['GET'],
)
def other():
    return render_template(
        template_name_or_list = 'other.html',
        some = VAL
    )
# This is the Route for File Upload ->
@app.route(
    rule = '/file_upload',
    methods = ['POST'],
)
def file_upload():
    file = request.files['file']
    
    if file.content_type == "text/plain":
        return file.read().decode()
    elif file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        df = pd.read_excel(file)
        return df.to_html()

# Essentially this creates a new directory to store the dowmloads
@app.route(
    rule = '/csv_two',
    methods = ['POST'],
)
def csv_two():
    file = request.files['file']
    df = pd.read_excel(file)

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    filename = f'{uuid.uuid4()}.csv'
    df.to_csv(
        os.path.join(
            'downloads' , filename
        )
    )
    return render_template(
        'download.html', 
        flname = filename
    )

# The Central Download Page is this one
@app.route(
    rule = '/download/<flname>',
    methods = ['GET'],
)
def download(flname):
    return send_from_directory(
        directory = 'downloads',
        path = flname,
        download_name = 'result.csv'
    )    

# This uses methods and request method which allows us to interact with the data in certain ways
@app.route(
    rule = '/hello',
    methods = ['GET', 'POST']
    )
def hello():
    if request.method == 'GET':
        return render_template(
            template_name_or_list = 'form.html'
        )
    elif request.method == 'POST':
        user = request.form.get('username')
        psw = request.form.get('password')

        if user == VAL and psw == '1Ramrup@S':
            return f"Hello {VAL} you have successfully authenticated"
        else:
            return "Login Failed"
    else:
        return "You will never see this message ever"

# This uses make response What this does is basically helps us control the HTTP headers
@app.route('/greet/<name>')
def greet(name):
    res = make_response(
        f'Hello {name}'
    )
    res.status_code = 202
    res.headers['content-type'] = 'text/plain'
    return f"<p>Hello {name}<br>Response Type is :-> {res if res != None else 'something'}<br>Body is :-> {res.data}<br>Status Code is :-> {res.status_code}<br></p>"

# These are not the Rotes but functions that we can use in Jinja2 HTML template
@app.template_filter('reverse_string')
def reverse_string(s):
    return s[ :: -1]

@app.template_filter('repeat')
def repeat(s , times = 2):
    return (s + ' ') * times

@app.template_filter('alternate')
def alternate(s):
    return ''.join(c.upper() if i % 2 != 0 else c.lower() for i,c in enumerate(s))

# Importing the Files here -> Basically extensions.py is used to avoid circular import error in run.py and models.py
from models import Person

# Now Here We add people to database in a Subscribe method
@app.route(
    rule = '/subscribe',
    methods = ['GET','POST']
    )
def subscribe():
    if request.method == 'GET':
        return render_template(
            template_name_or_list = 'subscribe.html'
        )
    elif request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        job = request.form.get('job')
        
        p1 = Person(
            name = name,
            age = age,
            job = job
        )
        db.session.add(p1)
        db.session.commit()
        flash("Person Added Successfully")

        return redirect(
            url_for(
                'subscribe'
            )
        )
# Then show all the prople who joined in a protected admin method
@app.route('/superuser')
def superuser():
    pupil = Person.query.all()
    return render_template(
        template_name_or_list = 'superuser.html',
        person = pupil
    )

# The Route to delete the Subscription Entries
@app.route(
    rule = '/delete/<int:pid>',
    methods = ['GET']
    )
def delete_person(pid):
    fellow = Person.query.get(pid)
    nam = fellow.name

    if fellow:
        db.session.delete(fellow)
        db.session.commit()
        flash(f'Record named {nam} has been erased')
    
    return redirect(
        url_for('superuser')
    )

# This uses the __name__ variable which is a dunder function to prevent other file from run (or mis-run this app)
if __name__ == '__main__':
    # The host means the current machine
    # The port means all devices connected to the network
    # Debug = True it helps to debug non crashing errors in an interactive manner
    app.run(
        host = '0.0.0.0',
        port = 5555,
        debug = True
    )
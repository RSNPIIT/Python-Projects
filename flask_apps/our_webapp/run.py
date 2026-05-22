from flask import Flask as fl,request ,make_response ,send_from_directory, render_template, Response
import os
import uuid
import pandas as pd

# Static variables
TMP = 'templates'
VAL = 'RSNPIIT'

# Creating a Flask Instance
app = fl(
    __name__,
    template_folder = TMP
    )

# The '/' means the root path of the file
@app.route('/')
def index():
    VAL = 'RSNPIIT'
    ITM = [20 , 30 , 35 , 40]
    return render_template(
        template_name_or_list = 'index.html',
        myname = VAL,
        myvalue = 9.8,
        myitem = ITM 
    )

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
            return f"Hello {VAL} you have successfully authenticated"
        else:
            return "Login Failed"

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
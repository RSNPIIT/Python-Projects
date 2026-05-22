from flask import Flask as fl,request ,make_response ,send_from_directory, render_template
import os

# Static variables
TMP = 'templates'

# Creating a Flask Instance
app = fl(
    __name__,
    template_folder = TMP
    )

# The '/' means the root aka the root path
@app.route('/')
def index():
    return "<h1>Hello World</h1>"

# This has been given as an optional Argument to Remove the 404 Favicon Error
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico', 
        mimetype='image/vnd.microsoft.icon'
        )

# This uses methods and request method which allows us to interact with the data in certain ways
@app.route(
    rule = '/hello',
    methods = ['GET', 'POST']
    )
def hello():
    if request.method == 'GET':
        return "Get Request made here"
    elif request.method == 'POST':
        return "Post Request made here"
    else:
        return "You will never see this message ever"

# This uses make response What this does is basically helps us control the HTTP heades
@app.route('/greet/<name>')
def greet(name):
    res = make_response(
        f'Hello {name}'
    )
    res.status_code = 202
    res.headers['content-type'] = 'text/plain'
    return f"<p>Hello {name}<br>Response Type is :-> {res if res != None else 'something'}<br>Body is :-> {res.data}<br>Status Code is :-> {res.status_code}<br></p>"

# This uses dynamic routing and exception handling in Python
@app.route('/add/<string:num1>/<string:num2>')
def adder(num1 , num2):
    try:
        num1 = float(num1)
        num2 = float(num2)
    except OverflowError as ov:
        return f"Error Occurred Here :-> \n{v}" , 404
    except ValueError as v:
        return f"Error Occurred Here :-> \n{v}" , 404
    else:
        sum = num1 + num2   
        if num1 >= 0 and num2 >= 0:
            return f"<h1>{num1} + {num2} = {sum :.2f}</h1>"
        elif num1 < 0:
            return f"<h1>{num1} + {num2} = {sum : .2f}</h1>"
        elif num2 < 0:
            return f"<h1>{num1} + ({num2}) = {sum : .2f}</h1>"
        else:
            return f"<h1>{num1} + ({num2}) = ({sum : .2f})</h1>"
    
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
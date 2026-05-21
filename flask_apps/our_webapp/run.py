from flask import Flask , send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Hello World</h1>"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico', 
        mimetype='image/vnd.microsoft.icon'
        )

@app.route('/hello')
def hello():
    return "Hello User"

@app.route('/greet/<name>')
def greet(name):
    return f"Hello {name}"

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
            return f"<h1>{num1} + {num2} = {sum}</h1>"
        elif num1 < 0:
            return f"<h1>{num1} + {num2} = {sum}</h1>"
        elif num2 < 0:
            return f"<h1>{num1} + ({num2}) = {sum}</h1>"
        else:
            return f"<h1>{num1} + ({num2}) = ({sum})</h1>"
    
if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 5555,
        debug = True
    )
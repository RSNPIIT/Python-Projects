from flask import Flask , request

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello User - This is my first Flask app'

@app.route('/contact')
def contact():
    return "Please Contact -> [[[ramrupsatpati@gmail.com]]]"

@app.route('/about')
def about():
    return "This is Abou Us Page"

@app.route('/submit' , methods = ['GET' , 'POST'])
def submit():
    if request.method == 'POST':
        return 'You are sending data'
    
    else:
        return 'You are only recieving the data not sending'

if __name__ == '__main__':
    app.run(debug = True)
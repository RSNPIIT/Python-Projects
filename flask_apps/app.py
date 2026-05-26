from flask import Flask, request, redirect, url_for, session, Response, render_template

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

@app.route('/')
def home():
    return render_template('starting.html')

@app.route('/login' , methods = ['GET' , 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username')
        password = request.form.get('password')
        type_ur = request.form.get('role')

        if uname == 'admin' and password == 'admin123' and type_ur == 'developer':
            session['user'] = uname
            return redirect(url_for('welcome'))
        
        else:
            flash('Invalid Credentials Please Try again')
            return Response('Invalid credentials , Please Try again Later' , mimetype = 'text/plain')
    
    else:
        return render_template('index.html')

@app.route('/welcome')
def welcome():
    if 'user' not in session:
        return redirect(url_for('home'))
    else:
        return render_template('welcome.html' , username = session['user'].title())

@app.route('/logout')
def logout():
    session.pop('user' , None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True)
import flask as fl

app = fl.Flask(__name__)

@app.route('/')
def run_it():
    return "<h1>Hello World</h1>"

if __name__ == '__main__':
    app.run(debug = True)
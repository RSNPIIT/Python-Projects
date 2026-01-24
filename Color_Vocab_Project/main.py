import flask as fl

app = fl.Flask(__name__ , template_folder='.' , static_folder='.' , static_url_path='')

FILENAME = 'index.html'

@app.route('/')
def render_it():
    return fl.render_template(FILENAME)

if __name__ == '__main__':
    app.run(debug = False)
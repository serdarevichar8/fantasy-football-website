from flask import Flask, render_template
import numpy as np

root = '/fantasy-football-website'

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')



@app.route('/champion')
def champion():
    return "champion"

@app.route('/season/<year>')
def season(year):
    if int(year) in np.arange(2019,2025):
        return render_template('base.html', year=year)
    else:
        return '<h1>404 Page not found<h1>'


if __name__ == '__main__':
    app.run(debug=True)

# If getting the error: Access denied to 127.0.0.1, go to this link:
# chrome://net-internals/#sockets
# and click on "Flush Socket Pools"
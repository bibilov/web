from flask import Flask
from flask import render_template
from flask import Response
import sqlite3
import random
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)


@app.route("/")
def cv_index():
    cvs = get_cv()
    res = ""
    for i, cv in enumerate(cvs):
        res += f"<h1>{i + 1})</h1>"
        res += f"<p>Желаемая зарплата: {cv['salary']}.</p>"
        res += f"<p>Образование: {cv['educationType']}.</p>"

    return res


@app.route("/dashboard")
def dashboard():
    con = sqlite3.connect('works.sqlite')
    res = con.execute('SELECT SUBSTR(dateModify, 1, 4), COUNT(*) FROM works WHERE dateModify NOT NULL GROUP BY '
                      'SUBSTR(dateModify, 1, 4)').fetchall()
    con.close()
    return render_template('d2.html',
                           cvs=get_cv(),
                           labels=[row[0] for row in res],
                           data=[row[1] for row in res]
                           )


def dict_factory(cursor, row):
    # обертка для преобразования
    # полученной строки. (взята из документации)
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_cv():
    con = sqlite3.connect('works.sqlite')
    con.row_factory = dict_factory
    res = list(con.execute('select * from works limit 20'))
    con.close()
    return res


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig


app.run()
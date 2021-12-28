import matplotlib.pyplot as plt
from flask import Flask
from flask import render_template
from flask import Response
import sqlite3
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)


@app.route("/")
def cv_index():
    cvs = get_cv()
    res = ""
    for i, cv in enumerate(cvs):
        res += f"<h1>{i + 1})</h1>"
        res += f"<p>Желаемая зарплата: asdasdasdsada {cv['salary']}.</p>"
        res += f"<p>Образование: {cv['educationType']}.</p>"

    return res


@app.route("/dashboard")
def dashboard():
    data = []
    with sqlite3.connect('works.sqlite') as con:
        data=list(con.execute('SELECT SUBSTR(dateModify, 1, 4), COUNT(*) FROM works WHERE dateModify NOT NULL GROUP BY SUBSTR(dateModify, 1, 4)'))
    return render_template('d3.html',
                           cvs=get_cv(),
                           data=[row[1] for row in data],
                           labels=[row[0] for row in data]
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
    with sqlite3.connect('works.sqlite') as con:
        (men_salary, men_count) = zip(*list(con.execute(
                                                'select salary,count(salary) from works where gender = "Мужской" group by salary')))
        (women_salary, women_count) = zip(*list(con.execute(
                                                    'select salary,count(salary) from works where gender = "Женский"  group by salary')))

        plt.plot(men_salary, men_count, color='r', label='Мужчины-высшее')
        plt.plot(women_salary, women_count, color='b', label='Женщины-высшее', linestyle='dashed')
        plt.xlabel('Зарплата')
        plt.ylabel("Кол-во")
        plt.title("Разброс зарплат")
        plt.legend()
    return plt.gcf()


app.run()
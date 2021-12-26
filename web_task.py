from flask import Flask
from flask import render_template
from flask import Response
import sqlite3
import random
import io
from collections import Counter
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


@app.route("/statistic")
def statistic():
    jobTitles = get_list_field('jobTitle')
    qualifications = get_list_field('qualification')
    res = ""
    peop_count = count_people_field1_not_match_field2(jobTitles, qualifications)
    res += f"<p>Из {peop_count[1]} людей не совпадают профессия и должность у {peop_count[0]}</p>"
    res += f"<p>Топ 5 образований людей, которые работают менеджерами:</p>"
    res += get_top(5, jobTitles, qualifications, "менеджер")
    res += f"<p>Топ 5 должностей людей, которые по диплому являются инженерами:</p>"
    res += get_top(5, qualifications, jobTitles,  "инженер")
    return res


def get_top(top_size, field_to_search, field_to_return, str_to_search):
    res = ''
    full_top = top(field_to_search, field_to_return, str_to_search)
    for i in range(top_size):
        res += f"<p>- {full_top[i][0]} - {full_top[i][1]} чел.</p>"
    return res


def get_list_field(field):
    con = sqlite3.connect('works.sqlite')
    res = list(con.execute(f'select {field} from works'))
    con.close()
    return res


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


def count_people_field1_not_match_field2(field1, field2):
    res_count = 0
    total = 0
    for (f1, f2) in zip(field1, field2):
        total += 1
        if not find_match(f1[0], f2[0]) and not find_match(f2[0], f1[0]):
            res_count += 1
    return res_count, total


def find_match(f1, f2):
    arr1 = str(f1).lower().replace('-', ' ').split()
    for word in arr1:
        if word in str(f2).lower():
            return True
    return False


def top(f_to_search, f_to_return, str_to_search):
    res = []
    for (f_s, f_r) in zip(f_to_search, f_to_return):
        if str(f_s[0]).lower().find(str_to_search[:-2]) != -1:
            if str(f_r[0]).find('None') == -1:
                res.append(f_r[0])

    return Counter(res).most_common()


app.run()
# -*- coding: utf-8 -*-

from flask import Flask, render_template, session, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, RadioField
# from wtforms.validators
from flask_bootstrap import Bootstrap
from searchAPI import *
# FilmSearch, PinyinSearch, TermsSearch, PicSearch, IDSearch, PlotSearch, get_relative_film, d3barjs

app = Flask(__name__)

app.config['SECRET_KEY'] = "WuYiQiTianLe"
bootstrap = Bootstrap(app)

class AccurateForm(FlaskForm):
    name = StringField("电影名:")
    time = StringField("年份:" )
    director = StringField("导演:" )
    stars = StringField("演员:")

    score = RadioField("电影评价",
        choices=[('1',"全部"), ('2',"搜好片"), ('3',"搜烂片")])

    search_type = RadioField("搜索类型",choices=[('1',"模糊搜索"),('2',"精确搜索")])
    submit = SubmitField("搜索")

@app.route('/', methods=['GET',"POST"])
def index():
    form = AccurateForm(csrf_enabled=False)
    data_index = {}

    if form.is_submitted():

        session["valid"]=True
        session[u'电影名']=form.name.data
        if len(form.time.data)>0:
            session[u'年份']=int(form.time.data.decode('utf-8'))
        session[u'导演']=form.director.data
        session[u'演员']=form.stars.data


        if form.search_type.data != "None":
            session['search_type']=form.search_type.data
        else:
            session['search_type']='1'
        print "stored", session['search_type']
        if form.score.data != "None":
            session['score']=form.score.data
        else:
            session['score']='1'

        return redirect(url_for("search_result"))

    return render_template("index.html",form=form)

@app.route('/s')
def search_result():
    movie_list = []
    arg_list = {}
    for arg in request.args.items():
        arg_list[arg[0]]=arg[1]
    if arg_list.get('q',None):
        movie_list = FilmSearch(arg_list['q']).search_film()

    if session.get('valid'):
        session.pop('valid',None)
        search_type = session.pop('search_type', None)
        if not search_type: search_type = '1'
        score = session.pop('score',None)
        if not score: score = '1'

        para_list =[u'电影名',u'年份',u'导演',u'演员']

        search_para_list = {}
        session.pop("name",None)
        for para in para_list:
            value = session.pop(para,None)
            if value:
                search_para_list[para]=value
        result_list = TermsSearch(search_para_list, search_type, score).search_film()
        movie_list = [movie for movie in result_list][:10]

    bar_json = d3barjs(movie_list)
    return render_template("s.html",result_list=movie_list,bar_json=bar_json)

@app.route('/plot')
def search_plot():
    return render_template("plot.html")

@app.route('/plot/result', methods=['GET','POST'])
def search_plot_result():
    attr_list = {}
    for q in request.args.items():
        attr_list[q[0]]=q[1]
    result_list=[]
    if attr_list.get('plot',None):
        result_list=PlotSearch(attr_list['plot']).search_film()
    return render_template("s.html",result_list=result_list)

@app.route('/co/<filmID>')
def relative_film(filmID):
    filmID = str(filmID)
    film_json = get_relative_film(filmID)
    # print filmID,type(str(filmID))
    return render_template("relative.html",film_json=film_json)

@app.route('/pic')
def search_picture():
    return render_template("pic.html")

@app.route("/pic/result")
def search_picture_result():
    # Search for picture
    attr_list = {}
    for q in request.args.items():
        attr_list[q[0]]=q[1]
    #
    # print attr_list

    result_list = []
    if attr_list.get('picfile',None):
        abs_path = "pic/data/"+attr_list['picfile']

        res_list = PicSearch(abs_path).search_film()
        # print res_list
        for mov in res_list:
            film_id = int(mov['path'].split('/')[-1].split('.')[0])
            print film_id

            result_list.append(IDSearch(film_id).search_film())
    print result_list
    return render_template("s.html",result_list=result_list)

@app.route("/stat")
def stat():
    return render_template('jsplay.html')


if __name__ == '__main__':
    app.run(debug=True)

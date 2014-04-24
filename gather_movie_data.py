import requests
import encrypt
import metacritic
import classifier
import re

import sqlite3
import os

from flask import Flask, request, session, g, redirect, url_for,\
                  render_template, flash

# Create application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
  DATABASE='/tmp/movie.db',
  DEBUG=True,
  SECRET_KEY='development key',
  USERNAME='admin',
  PASSWORD='default'
))

url = 'http://text-processing.com/api/sentiment/'
#clf = classifier.SentimentClassifier()
cur_source = ""
cur_movie = ""
cur_clf = "Naive Bayes 2-gram"

clfs = ["Naive Bayes 1-gram", "Naive Bayes 2-gram",
        "Naive Bayes 3-gram", "Naive Bayes 4-gram",
        "Naive Bayes 5-gram", "Decision Tree 1-gram",
        "Decision Tree 2-gram", "Decision Tree 3-gram"]

LOADING_DATASET = False
if LOADING_DATASET:
  clf_nbo = classifier.SentimentClassifier('nb_onegram')
  clf_nbt = classifier.SentimentClassifier('nb_twogram')
  clf_nbth = classifier.SentimentClassifier('nb_threegram')
  clf_nbf = classifier.SentimentClassifier('nb_fourgram')
  clf_nbfi = classifier.SentimentClassifier('nb_fivegram')
  clf_dto = classifier.SentimentClassifier('dt_onegram')
  clf_dtt = classifier.SentimentClassifier('dt_twogram')
  clf_dtth = classifier.SentimentClassifier('dt_threegram')

def add_movie_online( movie_name ):
  """
  This function adds a particular movie to the database
  It uses the sentiment analysis tools from nltk online
  """
  db = get_db()
  review_url = "http://www.metacritic.com/movie/" + movie_name + "/critic-reviews"
  m_data = metacritic.get_reviews( review_url )
  for critic in m_data['critics']:
    source_name = critic['source']
    quote = critic['quote']
    score = critic['score']
    sanitized_quote = re.sub('[^A-Za-z0-9 "`\'-.:;&]+', '', quote)
    try:
      r = requests.post( url, data= 'text=' + sanitized_quote )
      label = r.json()['label']
      positive = r.json()['probability']['pos']
      negative = r.json()['probability']['neg']
      neutral = r.json()['probability']['neutral']
    except:
      print "Error, skipping"
      label = ""
      positive = ""
      negative = ""
      neutral = ""

    db.execute('insert or ignore into entries (movie, positive, negative, ' \
               'neutral, label, source, quote, score) values ' \
               '(?, ?, ?, ?, ?, ?, ?, ?)',
               [movie_name, positive, negative, neutral, label, source_name, 
                quote, score])
  db.commit()

def add_movie( movie_name ):
  """
  This function adds a particular movie to the database
  """
  db = get_db()
  review_url = "http://www.metacritic.com/movie/" + movie_name + "/critic-reviews"
  m_data = metacritic.get_reviews( review_url )
  for critic in m_data['critics']:
    source_name = critic['source']
    quote = critic['quote']
    score = critic['score']
    sanitized_quote = re.sub('[^A-Za-z0-9 "`\'-.:;&]+', '', quote)
    
    res = clf_nbo.classify( sanitized_quote )
    positive_nbo = res['pos']
    negative_nbo = res['neg']
    label_nbo = res['label']
    
    res = clf_nbt.classify( sanitized_quote )
    positive_nbt = res['pos']
    negative_nbt = res['neg']
    label_nbt = res['label']
    
    res = clf_nbth.classify( sanitized_quote )
    positive_nbth = res['pos']
    negative_nbth = res['neg']
    label_nbth = res['label']
    
    res = clf_nbf.classify( sanitized_quote )
    positive_nbf = res['pos']
    negative_nbf = res['neg']
    label_nbf = res['label']
    
    res = clf_nbfi.classify( sanitized_quote )
    positive_nbfi = res['pos']
    negative_nbfi = res['neg']
    label_nbfi = res['label']

    label_dto = clf_dto.simple_classify( sanitized_quote )
    
    label_dtt = clf_dtt.simple_classify( sanitized_quote )
    
    label_dtth = clf_dtth.simple_classify( sanitized_quote )
    
    db.execute('insert or ignore into entries (movie, source, quote, score,'\
               'positive_nbo, negative_nbo, label_nbo,' \
               'positive_nbt, negative_nbt, label_nbt,' \
               'positive_nbth, negative_nbth, label_nbth,' \
               'positive_nbf, negative_nbf, label_nbf,' \
               'positive_nbfi, negative_nbfi, label_nbfi,' \
               'label_dto, label_dtt, label_dtth) values ' \
               '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,'\
               ' ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
               [movie_name, source_name, quote, score,
                positive_nbo, negative_nbo, label_nbo, 
               positive_nbt, negative_nbt, label_nbt,
               positive_nbth, negative_nbth, label_nbth,
               positive_nbf, negative_nbf, label_nbf,
               positive_nbfi, negative_nbfi, label_nbfi,
               label_dto, label_dtt, label_dtth])
  db.commit()

@app.route('/fill', methods=['POST'])
def fill_database():
  """
  This function fills the database with entries related to the movies
  found in a text file.
  """
  with open("movie_list.txt", 'r') as f:
    movies = f.readlines()
    for m in movies:
      add_movie( m.strip() )
  return redirect(url_for('show_movie_entries'))

def connect_db():
  rv = sqlite3.connect(app.config['DATABASE'])
  rv.row_factory = sqlite3.Row
  return rv

def get_db():
  """Opens a new database connection if there is none yet for the
  current application context.
  """
  if not hasattr(g, 'sqlite_db'):
    g.sqlite_db = connect_db()
  return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
  """Closes the database again at the end of the request."""
  if hasattr(g, 'sqlite_db'):
    g.sqlite_db.close()

@app.route('/')
def show_movie_entries():
  db = get_db()
  cur = db.execute('select movie, label_nbt, positive_nbt, negative_nbt, '\
                   'source, quote, score, id from entries order by id desc')
  entries = cur.fetchall()
  cur = db.execute('select distinct movie '\
                   'from entries order by movie asc')
  movies = cur.fetchall()
  cur = db.execute('select distinct source '\
                   'from entries order by source asc')
  sources = cur.fetchall()
  return render_template('show_movie_entries.html', entries=entries[:20],
                         movies=movies, sources=sources, clfs=clfs, nb=True)

def compute_stats( entries, nb ):
  total_score = 0
  total_pos = 0
  num = len( entries )
  if nb:
    for entry in entries:
      total_score += entry[6]
      total_pos += entry[2]
  else:
    for entry in entries:
      total_score += entry[4]
      if entry[1] == 'pos':
        total_pos += 1
  avg_score = total_score / num
  avg_pos = total_pos / num
  pos_per_score = total_pos / total_score
  return ( avg_score, avg_pos, pos_per_score )

@app.route('/', methods=['POST'])
#def show_specific_entries():
def show_entries_by_movie():
  global cur_movie
  global cur_source
  global cur_clf

  if 'movie' in request.form.keys():
    movie = request.form['movie']
    cur_movie = movie
    cur_source = ""
  elif 'source' in request.form.keys():
    source = request.form['source']
    cur_source = source
    cur_movie = ""
  elif 'clf' in request.form.keys():
    cur_clf = request.form['clf']

  if cur_movie != "":
    sel = 'movie'
    val = str(cur_movie)
  elif cur_source != "":
    sel = 'source'
    val = str(cur_source)

  if cur_clf == "Naive Bayes 1-gram":
    lbl = 'label_nbo'
    pos = 'positive_nbo'
    neg = 'negative_nbo'
    nb = True
  elif cur_clf == "Naive Bayes 2-gram":
    lbl = 'label_nbt'
    pos = 'positive_nbt'
    neg = 'negative_nbt'
    nb = True
  elif cur_clf == "Naive Bayes 3-gram":
    lbl = 'label_nbth'
    pos = 'positive_nbth'
    neg = 'negative_nbth'
    nb = True
  elif cur_clf == "Naive Bayes 4-gram":
    lbl = 'label_nbf'
    pos = 'positive_nbf'
    neg = 'negative_nbf'
    nb = True
  elif cur_clf == "Naive Bayes 5-gram":
    lbl = 'label_nbfi'
    pos = 'positive_nbfi'
    neg = 'negative_nbfi'
    nb = True
  elif cur_clf == "Decision Tree 1-gram":
    lbl = 'label_dto'
    pos = 'positive_dto'
    neg = 'negative_dto'
    nb = False
  elif cur_clf == "Decision Tree 2-gram":
    lbl = 'label_dtt'
    pos = 'positive_dtt'
    neg = 'negative_dtt'
    nb = False
  elif cur_clf == "Decision Tree 3-gram":
    lbl = 'label_dtth'
    pos = 'positive_dtth'
    neg = 'negative_dtth'
    nb = False
  
  db = get_db()
  if nb:
    cur = db.execute('select %s, %s, %s, %s, '\
                     'source, quote, score, id from entries where %s=(?)'\
                     'order by id desc' % (sel, lbl, pos, neg, sel), (val,))
  else:
    cur = db.execute('select %s, %s, '\
                     'source, quote, score, id from entries where %s=(?)'\
                     'order by id desc' % (sel, lbl, sel), (val,))
  entries = cur.fetchall()
  
  cur = db.execute('select distinct movie '\
                   'from entries order by movie asc')
  movies = cur.fetchall()
  cur = db.execute('select distinct source '\
                   'from entries order by source asc')
  sources = cur.fetchall()
  avg_score, avg_pos, pos_per_score = compute_stats( entries, nb )
  return render_template('show_movie_entries.html', entries=entries,
                         movies=movies, sources=sources, nb=nb,
                         avg_score=avg_score, avg_pos=avg_pos, 
                         pos_per_score=pos_per_score, name=val, clfs=clfs,
                         cur_movie=cur_movie, cur_source=cur_source,
                         cur_clf=cur_clf)

@app.route('/add', methods=['POST'])
def add_entry():
  add_movie( request.form['movie'] )
  return redirect(url_for('show_movie_entries'))

app.config['DEBUG'] = True
if __name__ == "__main__":
  app.run()

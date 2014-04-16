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
clf = classifier.NaiveBayesClassifier()

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
    res = clf.classify( sanitized_quote )
    positive = res['pos']
    negative = res['neg']
    label = res['label']

    db.execute('insert or ignore into entries (movie, positive, negative, ' \
               'label, source, quote, score) values ' \
               '(?, ?, ?, ?, ?, ?, ?)',
               [movie_name, positive, negative, label, source_name, 
                quote, score])
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
  cur = db.execute('select movie, positive, negative, label, '\
                   'source, quote, score, id from entries order by id desc')
  entries = cur.fetchall()
  return render_template('show_movie_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
  add_movie( request.form['movie'] )
  return redirect(url_for('show_movie_entries'))

app.config['DEBUG'] = True
if __name__ == "__main__":
  app.run()

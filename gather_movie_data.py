import requests
import encrypt
import metacritic
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
  DATABASE='/tmp/test_movie.db',
  DEBUG=True,
  SECRET_KEY='development key',
  USERNAME='admin',
  PASSWORD='default'
))

url = 'http://text-processing.com/api/sentiment/'

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
  cur = db.execute('select movie, positive, negative, neutral, label, '\
                   'critic, quote, score, id from entries order by id desc')
  entries = cur.fetchall()
  return render_template('show_movie_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
  db = get_db()
  #statuses = api.GetUserTimeline(screen_name='CBCNews')
  movie_name = request.form['movie']
  review_url = "http://www.metacritic.com/movie/" + movie_name + "/critic-reviews"
  m_data = metacritic.get_reviews( review_url )
  for critic in m_data['critics']:
    critic_name = critic['critic']
    quote = critic['quote']
    score = critic['score']
    print( critic_name )
    sanitized_quote = re.sub('[^A-Za-z0-9 "`\'-.:;&]+', '', quote)
    #print( quote )
    #print( sanitized_quote )
    try:
      r = requests.post( url, data= 'text=' + sanitized_quote )
      label = r.json()['label']
      positive = r.json()['probability']['pos']
      negative = r.json()['probability']['neg']
      neutral = r.json()['probability']['neutral']
      print( label )
    except:
      print "Error, skipping"
      label = ""
      positive = ""
      negative = ""
      neutral = ""

    db.execute('insert or ignore into entries (movie, positive, negative, ' \
               'neutral, label, critic, quote, score) values ' \
               '(?, ?, ?, ?, ?, ?, ?, ?)',
               [movie_name, positive, negative, neutral, label, critic_name, 
                quote, score])
  db.commit()
  return redirect(url_for('show_movie_entries'))

app.config['DEBUG'] = True
if __name__ == "__main__":
  app.run()

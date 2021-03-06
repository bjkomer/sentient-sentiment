import requests
import encrypt
import metacritic
import classifier
import re
import csv
import math

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
cur_source = ""
cur_movie = ""
cur_clf = "Naive Bayes 1-2-gram"

ERR_THRESH = 100 # Error threshold
LABEL_THRESH = 50 # Scores above this are considered positive
LABEL_THRESH2 = 70 # Scores above this are considered positive

clfs = ["Naive Bayes 1-gram", "Naive Bayes 2-gram",
        "Naive Bayes 1-2-gram",
        "Decision Tree 1-gram", "Decision Tree 2-gram", 
        "Decision Tree 3-gram", 
        "Decision Tree 1-2-gram",
        "KNN 1-gram", "KNN 1-2-gram", 
        "SCV 1-2-gram",
        "GBC 1-2-gram"]

clf_t = ["nb1", "nb2", "nb12",
         "dt1", "dt2", "dt3", "dt12",
         "knn1", "knn12",
         "svc12",
         "gbc12"]

LOADING_DATASET = False
if LOADING_DATASET:
  clf = []
  for tag in clf_t:
    clf.append( classifier.SentimentClassifier( tag ) )

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
  global clf
  db = get_db()
  review_url = "http://www.metacritic.com/movie/" + movie_name + "/critic-reviews"
  m_data = metacritic.get_reviews( review_url )
  for critic in m_data['critics']:
    source_name = critic['source']
    quote = critic['quote']
    score = critic['score']
    sanitized_quote = re.sub('[^A-Za-z0-9 "`\'-.:;&]+', '', quote)
    
    positive = []
    negative = []
    label = []
    for i in range( len( clf_t ) ):

      res = clf[i].classify( sanitized_quote )
      positive.append( res['pos'] )
      negative.append( res['neg'] )
      label.append( res['label'] )
    
    db.execute('insert or ignore into entries (movie, source, quote, score,'\
               'positive_nb1, negative_nb1, label_nb1,'\
               'positive_nb2, negative_nb2, label_nb2,'\
               'positive_nb12, negative_nb12, label_nb12,'\
               'positive_dt1, negative_dt1, label_dt1,'\
               'positive_dt2, negative_dt2, label_dt2,'\
               'positive_dt3, negative_dt3, label_dt3,'\
               'positive_dt12, negative_dt12, label_dt12,'\
               'positive_knn1, negative_knn1, label_knn1,'\
               'positive_knn12, negative_knn12, label_knn12,'\
               'positive_svc12, negative_svc12, label_svc12,'\
               'positive_gbc12, negative_gbc12, label_gbc12'\
               ') values '\
               '(?, ?, ?, ?,'\
               ' ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,'\
               ' ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,'\
               ' ?, ?, ?, ?, ?, ?, ?, ?, ?)',
               (movie_name, source_name, quote, score,
                positive[0], negative[0], label[0],
                positive[1], negative[1], label[1],
                positive[2], negative[2], label[2],
                positive[3], negative[3], label[3],
                positive[4], negative[4], label[4],
                positive[5], negative[5], label[5],
                positive[6], negative[6], label[6],
                positive[7], negative[7], label[7],
                positive[8], negative[8], label[8],
                positive[9], negative[9], label[9],
                positive[10], negative[10], label[10] ))
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
  cur = db.execute('select movie, label_nb12, positive_nb12, negative_nb12, '\
                   'source, quote, score, id from entries order by id desc')
  entries = cur.fetchall()
  cur = db.execute('select distinct movie '\
                   'from entries order by movie asc')
  movies = cur.fetchall()
  cur = db.execute('select distinct source '\
                   'from entries order by source asc')
  sources = cur.fetchall()
  return render_template('show_movie_entries.html', entries=entries[:20],
                         movies=movies, sources=sources, clfs=clfs)

def compute_stats( entries ):
  total_score = 0
  total_pos = 0
  total_err = 0
  num = len( entries )
  for entry in entries:
    total_score += entry[6]
    total_pos += entry[2]
    diff = ( entry[2]*100 - entry[6] ) ** 2
    if diff > ERR_THRESH:
      total_err += ( diff - ERR_THRESH )
  avg_score = total_score / num
  avg_pos = total_pos / num
  pos_per_score = total_pos / total_score
  avg_err = math.sqrt( total_err / num )
  return ( avg_score, avg_pos, pos_per_score, avg_err )

@app.route('/', methods=['POST'])
#def show_specific_entries():
def show_entries_by_movie():
  global cur_movie
  global cur_source
  global cur_clf
  global clfs
  global clf_t

  if 'movie' in request.form.keys():
    movie = request.form['movie']
    cur_movie = str(movie)
    cur_source = ""
  elif 'source' in request.form.keys():
    source = request.form['source']
    cur_source = str(source)
    cur_movie = ""
  elif 'clf' in request.form.keys():
    cur_clf = str(request.form['clf'])

  if cur_movie != "":
    sel = 'movie'
    val = cur_movie
  elif cur_source != "":
    sel = 'source'
    val = cur_source

  index = clfs.index( cur_clf )
  lbl = "label_" + clf_t[ index ]
  pos = "positive_" + clf_t[ index ]
  neg = "negative_" + clf_t[ index ]

  db = get_db()
  cur = db.execute('select %s, %s, %s, '\
                   'source, movie, quote, score, id from entries where %s=(?)'\
                   'order by id desc' % (lbl, pos, neg, sel), (val,))
  entries = cur.fetchall()
  
  cur = db.execute('select distinct movie '\
                   'from entries order by movie asc')
  movies = cur.fetchall()
  cur = db.execute('select distinct source '\
                   'from entries order by source asc')
  sources = cur.fetchall()
  avg_score, avg_pos, pos_per_score, avg_err = compute_stats( entries )
  return render_template('show_movie_entries.html', entries=entries,
                         movies=movies, sources=sources,
                         avg_score=avg_score, avg_pos=avg_pos, 
                         pos_per_score=pos_per_score, name=val, clfs=clfs,
                         cur_movie=cur_movie, cur_source=cur_source,
                         cur_clf=cur_clf, avg_err=avg_err)

def compare_sources():
  
  sources = ["The New York Times", "Time", 
             "Rolling Stone", "TV Guide", "TNT RoughCut"]
  #sources = ["The New York Times", "Time", 
  #           "Rolling Stone", "TV Guide"]
  #sources = ["The New York Times", 
  #           "Rolling Stone", "TV Guide"]

  
  with open('results.csv', 'wb') as csvfile:
    writer = csv.writer( csvfile, delimiter=',')
    
    db = get_db()
    m = []
    for source in sources:  
      cur = db.execute('select distinct movie from entries where source ='\
                       '? order by movie desc', (source,))
      entries = cur.fetchall()
      m.append( [x[0] for x in entries] )
    
    movies_in_all = []
    for i in m[0]:
      found = False
      for j in m[1:]:
        cur_found = False
        for k in j:
          if i == k:
            cur_found = True
            break
        if cur_found == False:
          found = False
          break
        else:
          found = True
      if found:
        movies_in_all.append( i )
        found = False

    print( movies_in_all )
    print( len( movies_in_all ) )

    for source in sources:
      print( [source]+movies_in_all )
      #cur = db.execute('select movie, score, label_nb12, positive_nb12 from entries where source ='\
      #                 '(?) and movie in (? ? ? ? ? ? ? ? ? ? ? ?) order by movie desc',
      #                 [source]+movies_in_all)
      cur = db.execute('select movie, score, label_nb12, positive_nb12 from entries where source ='\
                       '"%s" and movie in (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) order by '\
                       'movie desc'%source,
                       movies_in_all)
      entries = cur.fetchall()
      writer.writerow( ["Source:", source ] )
      writer.writerow( ["Movie", "Score", "Label", "Positive" ] )
      for entry in entries:
        writer.writerow( [entry[0], entry[1], entry[2], entry[3]] )
    
def hybrid_classifier():

  with open('results.csv', 'wb') as csvfile:
    writer = csv.writer( csvfile, delimiter=',')
    
    db = get_db()
    
    cur = db.execute('select score, label_dt12, label_nb12, label_dt1, '\
                     'label_gbc12, label_dt2, label_dt3, label_nb2 from entries')
    
    entries = cur.fetchall()
    num_entries = len( entries )
    l_thresh_list = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95]
    total_acc = []
    for lt in range( len( l_thresh_list ) ):
      total_acc.append(0.0)
    
    for entry in entries:
      for i,lt in enumerate(l_thresh_list):
        score = entry[0]
        dt1 = entry[1]
        dt12 = entry[3]
        gbc12 = entry[4]
        dt2 = entry[5]
        dt3 = entry[6]
        nb = entry[2]
        nb2 = entry[7]
        if dt1 == 'neg' and dt12 == 'neg' and gbc12 == 'neg' and dt2 == 'neg'\
        and dt3 == 'neg' and nb2 == 'pos':
          lbl = 'neg'
        else:
          lbl = nb
        if lbl == 'pos' and score >= lt:
          acc = 1.0
        elif lbl == 'neg' and score < lt:
          acc = 1.0
        else:
          acc = 0.0
        total_acc[i] += acc
    
    writer.writerow(["Accuracy of Hybrid Classifier, Varying Label Thresholds"])
    writer.writerow(["Classifier"]+l_thresh_list)
    writer.writerow( ["Hybrid DT1, DT2, DT12, GBC12, NB1"] + [ x/num_entries for x in total_acc ] )



@app.route('/data', methods=['POST'])
def generate_data():
  """
  This function organizes the data into a spreadsheet in various ways
  
  For each classifier it computes:
  -Computes average squared error
  -Percent correct
  -Reports the 10 movies with the most error
  -Reports the 10 movies with the least error
  -Reports the 10 sources with the most error
  -Reports the 10 sources with the least error
  -Reports sentiment rating for the top 10 highest scoring movies
  -Reports sentiment rating for the top 10 lowest scoring movies
  -Reports error for the top 10 highest scoring movies
  -Reports error for the top 10 lowest scoring movies
  """

  #compare_sources()
  #return redirect(url_for('show_movie_entries'))
  #hybrid_classifier()
  #return redirect(url_for('show_movie_entries'))

  with open('results.csv', 'wb') as csvfile:
    writer = csv.writer( csvfile, delimiter=',')
    
    db = get_db()
    
    cur = db.execute('select * from entries')
    
    entries = cur.fetchall()
    
    total_pos = []
    total_err = []
    total_lbl = [] # counts positive labels
    total_t_err = []
    total_t_err2 = []
    total_acc = []
    total_errm = [] # error normalized by label threshhold
    total_t_errm = [] # error normalized by label threshold, only counting incorrect labels
    total_acc2 = []
    total_score = 0.0
    num_entries = len( entries )
    l_thresh_list = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95]
    e_thresh_list = [x*5 for x in range(20)]

    for c in range( len( clf_t ) ):
      total_pos.append(0.0)
      total_err.append(0.0)
      total_lbl.append(0.0)
      l_thresh = []
      l2_thresh = []
      l3_thresh = []
      e_thresh = []
      e2_thresh = []
      for lt in range( len( l_thresh_list ) ):
        l_thresh.append(0.0)
        l2_thresh.append(0.0)
        l3_thresh.append(0.0)
      for et in range( len( e_thresh_list ) ):
        e_thresh.append(0.0)
        e2_thresh.append(0.0)
      total_acc.append( l_thresh )
      total_errm.append( l2_thresh )
      total_t_errm.append( l3_thresh )
      total_t_err.append( e_thresh )
      total_t_err2.append( e2_thresh )

    # Loop through each data point
    for entry in entries:
      # Loop through each classifier
      score = entry[4]
      total_score += score
      movie = entry[1]
      source = entry[2]
      for c in range( len( clf_t ) ):
        pos = entry[3*c+5]
        neg = entry[3*c+6]
        lbl = str(entry[3*c+7])
        err = (score - pos*100) ** 2
        
        for i,lt in enumerate(l_thresh_list):
          if lbl == 'pos' and score >= lt:
            acc = 1.0
            t_errm = 0
          elif lbl == 'neg' and score < lt:
            acc = 1.0
            t_errm = 0
          else:
            acc = 0.0
            #t_errm = (score - pos * lt * 2) ** 2
            if score >= lt:
              t_errm = (score - (lt + (100-lt)*2*(pos-.5))) ** 2
            else:
              #t_errm = (score - (lt + lt*(pos))) ** 2
              t_errm = (score - (lt*pos*2)) ** 2
          #errm = (score - pos * lt * 2) ** 2
          if score >= lt:
            errm = (score - (lt + (100-lt)*2*(pos-.5))) ** 2
          else:
            errm = (score - (lt*pos*2)) ** 2
          total_errm[c][i] += errm
          total_t_errm[c][i] += t_errm
          total_acc[c][i] += acc
        
        for i, et in enumerate(e_thresh_list):
          a = abs(score - pos*100)
          if a < et:
            t_err = 0.0
            t_err2 = 0.0
          else:
            t_err = (a - et) ** 2
            t_err2 = a ** 2
          total_t_err[c][i] += t_err
          total_t_err2[c][i] += t_err2

        total_pos[ c ] += pos
        total_err[ c ] += err
        total_lbl[ c ] += 1.0 if lbl == 'pos' else 0.0
    
    
    writer.writerow(["Varying Label Thresholds, Modified Error"])
    writer.writerow(["Classifier"]+l_thresh_list)
    for c in range( len( clf_t ) ):
      writer.writerow( [clf_t[c]] + [ math.sqrt(x/num_entries) for x in total_errm[c] ] )
    writer.writerow(["Varying Label Thresholds, Modified Error, only for incorrect labels"])
    writer.writerow(["Classifier"]+l_thresh_list)
    for c in range( len( clf_t ) ):
      writer.writerow( [clf_t[c]] + [ math.sqrt(x/num_entries) for x in total_t_errm[c] ] )
    writer.writerow(["Varying Label Thresholds"])
    writer.writerow(["Classifier"]+l_thresh_list)
    for c in range( len( clf_t ) ):
      writer.writerow( [clf_t[c]] + [ x/num_entries for x in total_acc[c] ] )
    writer.writerow([""])
    writer.writerow(["Varying Error Thresholds"])
    writer.writerow(["Threshold"]+e_thresh_list)
    for c in range( len( clf_t ) ):
      writer.writerow( [clf_t[c]] + [ math.sqrt(x/num_entries) for x in total_t_err[c] ] )
    writer.writerow([""])
    writer.writerow(["Varying Error Sharp Cutoff Thresholds"])
    writer.writerow(["Threshold"]+e_thresh_list)
    for c in range( len( clf_t ) ):
      writer.writerow( [clf_t[c]] + [ math.sqrt(x/num_entries) for x in total_t_err2[c] ] )

    

    """
    writer.writerow(["Average Score:", total_score/num_entries,
                     "Number of Reviews:", num_entries])
    writer.writerow(["Classifier", "Average Positive Sentiment", 
                     "Accuracy with 50 Threshold",
                     "Accuracy with 70 Threshold",
                     "Average Error","Average Error with Threshold",
                     "Percentage of Positive Labels"])
    for c in range( len( clf_t ) ):
      pos = total_pos[ c ] / num_entries
      lbl = total_lbl[ c ] / num_entries
      acc = total_acc[ c ] / num_entries
      acc2 = total_acc2[ c ] / num_entries
      err = math.sqrt( total_err[ c ] / num_entries )
      t_err = math.sqrt( total_t_err[ c ] / num_entries )

      writer.writerow([clf_t[c], pos, acc, acc2, err, t_err, lbl])
    """
  return redirect(url_for('show_movie_entries'))

@app.route('/add', methods=['POST'])
def add_entry():
  add_movie( request.form['movie'] )
  return redirect(url_for('show_movie_entries'))

app.config['DEBUG'] = True
if __name__ == "__main__":
  app.run()

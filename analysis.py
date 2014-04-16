import sqlite3
import cPickle

def predictability():
  """
  Compute overall predictability of score based on sentiment.
  """

  

def average_by_movie( movies ):
  """
  Computes average score and sentiment by movie
  """
  
  results = {}
  for movie in movies:
    total = 0
    num = len( movie['reviews'] )
    for review in movie['reviews']:
      total += review['score']

    results[movie['name']] = {'Score':total/num}

  return results

def average_by_source( sources ):
  """
  Computes average score and sentiment by source of review
  """
  
  results = {}
  for source in sources:
    total = 0
    num = len( source['reviews'] )
    for review in source['reviews']:
      total += review['score']

    results[source['name']] = {'Score':total/num}

  return results

def label_by_movie( movies ):
  """
  Computes average score of each label by movie
  """
  results = {}
  for movie in movies:
    num_pos = 0
    num_neg = 0
    num_neu = 0
    tot_pos = 0
    tot_neg = 0
    tot_neu = 0
    pos = -1
    neg = -1
    neu = -1
    for review in movie['reviews']:
      if review['label'] == 'pos':
        num_pos += 1
        tot_pos += review['score']
      elif review['label'] == 'neg':
        num_neg += 1
        tot_neg += review['score']
      else:
        num_neu += 1
        tot_neu += review['score']

    if num_pos > 0:
      pos = tot_pos/num_pos
    if num_neg > 0:
      neg = tot_neg/num_neg
    if num_neu > 0:
      pos = tot_neu/num_neu

    results[movie['name']] = {'Positve':pos,
                              'Negative':neg,
                              'Neutral':neu}

  return results


def label_by_source( sources ):
  """
  Computes average score of each label by source
  """
  results = {}
  for source in sources:
    num_pos = 0
    num_neg = 0
    num_neu = 0
    tot_pos = 0
    tot_neg = 0
    tot_neu = 0
    pos = -1
    neg = -1
    neu = -1
    for review in source['reviews']:
      if review['label'] == 'pos':
        num_pos += 1
        tot_pos += review['score']
      elif review['label'] == 'neg':
        num_neg += 1
        tot_neg += review['score']
      else:
        num_neu += 1
        tot_neu += review['score']

    if num_pos > 0:
      pos = tot_pos/num_pos
    if num_neg > 0:
      neg = tot_neg/num_neg
    if num_neu > 0:
      pos = tot_neu/num_neu

    results[source['name']] = {'Positve':pos,
                              'Negative':neg,
                              'Neutral':neu}

  return results

def average_sentiment_score_value():
  """
  Average amount of 'sentiment' each score point represents
  """

def average_sentiment_score_value_by_source( sources ):
  """
  Average amount of 'sentiment' each score point represents for each source
  """

def average_sentiment_score_value_by_movie( movies ):
  """
  Average amount of 'sentiment' each score point represents for each movie
  """

def generate_data():
  conn = sqlite3.connect('/tmp/test_movie.db')
  c = conn.cursor()
  
  # Generate by-movie data
  c.execute('select movie, positive, negative, neutral, label, '\
            'critic, quote, score from entries order by movie desc')
  data = c.fetchall()
  movies = []
  name = ""
  for item in data:
    if str(item[1]) == "":
      continue
    if item[0] != name:
      if name != "":
        movies.append( movie )
      movie = {'name':item[0],
               'reviews':[]}
      name = item[0]
    movie['reviews'].append( {'source':item[5],
                              'positive':item[1],
                              'negative':item[2],
                              'neutral':item[3],
                              'label':item[4],
                              'score':item[7]})
  movies.append( movie )
  # Generate by-source data
  c.execute('select movie, positive, negative, neutral, label, '\
            'critic, quote, score from entries order by critic desc')
  data = c.fetchall()
  sources = []
  name = ""
  for item in data:
    if str(item[1]) == "":
      continue
    if item[5] != name:
      if name != "":
        sources.append( source )
      source = {'name':item[5],
               'reviews':[]}
      name = item[5]
    source['reviews'].append( {'movie':item[0],
                              'positive':item[1],
                              'negative':item[2],
                              'neutral':item[3],
                              'label':item[4],
                              'score':item[7]})
  sources.append( source )

  with open( "movie_data.pkl", 'wb' ) as dump_file:
    cPickle.dump({'movies':movies,'sources':sources}, dump_file)

def main():
  #generate_data()
  data = cPickle.load( open( "movie_data.pkl", 'rb' ) )

  movies = data['movies']
  sources = data['sources']
  
  print( average_by_movie( movies ) )
  print( average_by_source( sources ) )
  print( label_by_movie( movies ) )
  print( label_by_source( sources ) )

if __name__ == "__main__":
  main()

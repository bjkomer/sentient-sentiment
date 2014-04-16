import cPickle
import nltk.data
from nltk.util import ngrams


class NaiveBayesClassifier():

  def __init__( self ):
    self.classifier = nltk.data.load("classifiers/movie_reviews_NaiveBayes.pickle")

  def classify( self, quote ):
    tokens = nltk.word_tokenize(quote)
    feats = dict([(token, True) for token in tokens + ngrams(tokens, 2)])
    prob = self.classifier.prob_classify( feats )
    label = 'pos'
    if prob.prob('neg') > .5:
      label = 'neg'
    return {'pos':prob.prob('pos'),'neg':prob.prob('neg'),'label':label}
  
  def simple_classify( self, quote ):
    tokens = nltk.word_tokenize(quote)
    feats = dict([(token, True) for token in tokens + ngrams(tokens, 2)])
    return self.classifier.classify( feats )

class EPAClassifier():

  def __init__():
    build_table()

  def build_table():
    """
    Build tfidf EPA table
    """

def main():
  data = cPickle.load( open( "movie_data.pkl", 'rb' ) )

  movies = data['movies']
  sources = data['sources']

  classifier = NaiveBayesClassifier()

  for r in movies[0]['reviews']:
    print( classifier.classify(r['quote']), r['score'], r['positive'],
          r['negative'])
  
if __name__ == "__main__":
  main()

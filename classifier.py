import cPickle
import nltk.data
from nltk.util import ngrams


class SentimentClassifier():

  def __init__( self ):
    self.nb_onegram = None
    self.nb_twogram = nltk.data.load("classifiers/movie_reviews_NaiveBayes_2gram.pickle")
    self.nb_threegram = None
    self.nb_fourgram = None
    self.dt_twogram = None
    self.dt_onegram = None

    self.classifier = self.nb_twogram
    self.ngrams = 2

  def classify( self, quote ):
    tokens = nltk.word_tokenize(quote)
    if self.ngrams == 1:
      feats = dict([(token, True) for token in tokens])
    elif self.ngrams == 2:
      feats = dict([(token, True) for token in tokens + ngrams(tokens, 2)])
    elif self.ngrams == 3:
      feats = dict([(token, True) for token in tokens + ngrams(tokens, 2) +
                    ngrams(tokens, 3)])
    elif self.ngrams == 4:
      feats = dict([(token, True) for token in tokens + ngrams(tokens, 2) +
                    ngrams(tokens, 3) + ngrams(tokens, 4)])
    prob = self.classifier.prob_classify( feats )
    label = 'pos'
    if prob.prob('neg') > .5:
      label = 'neg'
    return {'pos':prob.prob('pos'),'neg':prob.prob('neg'),'label':label}
  
  def simple_classify( self, quote ):
    tokens = nltk.word_tokenize(quote)
    if self.ngrams == 1:
      feats = dict([(token, True) for token in tokens])
    elif self.ngrams ==2:
      feats = dict([(token, True) for token in tokens + ngrams(tokens, 2)])
    return self.classifier.classify( feats )

  def set_classifier( self, name ):
    if name == 'nb_onegram':
      if self.nb_onegram is None:
        self.nb_onegram = nltk.data.load("classifiers/movie_reviews_NaiveBayes_1gram.pickle")
      self.classifier = self.nb_onegram
      self.ngrams = 1
    elif name == 'nb_twogram':
      if self.nb_twogram is None:
        self.nb_twogram = nltk.data.load("classifiers/movie_reviews_NaiveBayes_2gram.pickle")
      self.classifier = self.nb_twogram
      self.ngrams = 2
    elif name == 'nb_threegram':
      if self.nb_threegram is None:
        self.nb_threegram = nltk.data.load("classifiers/movie_reviews_NaiveBayes_3gram.pickle")
      self.classifier = self.nb_threegram
      self.ngrams = 3
    elif name == 'nb_fourgram':
      if self.nb_fourgram is None:
        self.nb_fourgram = nltk.data.load("classifiers/movie_reviews_NaiveBayes_4gram.pickle")
      self.classifier = self.nb_fourgram
      self.ngrams = 4
    elif name == 'dt_onegram':
      if self.dt_onegram is None:
        self.dt_onegram = nltk.data.load("classifiers/movie_reviews_DecisionTree_1gram.pickle")
      self.classifier = self.dt_onegram
      self.ngrams = 1
    elif name == 'dt_twogram':
      if self.dt_twogram is None:
        self.dt_twogram = nltk.data.load("classifiers/movie_reviews_DecisionTree_2gram.pickle")
      self.classifier = self.dt_twogram
      self.ngrams = 2

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

  classifier = SentimentClassifier()

  for r in movies[0]['reviews']:
    print( classifier.classify(r['quote']), r['score'], r['positive'],
          r['negative'])
  
if __name__ == "__main__":
  main()

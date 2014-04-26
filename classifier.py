import cPickle
import nltk.data
from nltk.util import ngrams


class SentimentClassifier():

  def __init__( self, clf_type='nb12' ):

    # {Name:[Classifier, Prob_Classify?, NGrams]}
    self.clf = {"nb1":[None,True,[1]], "nb2":[None,True,[2]], "nb3":[None,True,[3]],
                 "nb4":[None,True,[4]], "nb5":[None,True,[5]],
                 "nb12":[None,True,[1,2]], "nb123":[None,True,[1,2,3]],
                 "nb1234":[None,True,[1,2,3,4]],
                 "dt1":[None,False,[1]], "dt2":[None,False,[2]],
                 "dt3":[None,False,[3]],
                 "dt4":[None,False,[4]], "dt12":[None,False,[1,2]],
                 "knn1":[None,True,[1]], "knn12":[None,True,[1,2]],
                 "svc12":[None,False,[1,2]],
                 "gbc12":[None,True,[1,2]]}

    self.set_classifier( clf_type )

  def generate_features( self, quote ):
    tokens = nltk.word_tokenize(quote)
    full_tokens = []
    for n in self.ngrams:
      if n == 1:
        full_tokens += tokens
      else:
        full_tokens += ngrams( tokens, n )

    return dict([(token, True) for token in full_tokens])

  def classify( self, quote ):
    
    feats = self.generate_features( quote )
    if self.prob:
      prob = self.clf[ self.cur_clf ][0].prob_classify( feats )
      label = 'pos'
      if prob.prob('neg') > .5:
        label = 'neg'
      return {'pos':prob.prob('pos'),'neg':prob.prob('neg'),'label':label}
    else:
      label =  self.clf[ self.cur_clf ][0].classify( feats )
      p_pos = 1 if label == 'pos' else 0
      p_neg = 1 if label != 'pos' else 0

      return {'pos':p_pos,'neg':p_neg,'label':label}
  
  def clf_string( self, name ):

    if name == "nb1":
      return "classifiers/movie_reviews_NaiveBayes_1gram.pickle"
    elif name == "nb2":
      return "classifiers/movie_reviews_NaiveBayes_2gram.pickle"
    elif name == "nb3":
      return "classifiers/movie_reviews_NaiveBayes_3gram.pickle"
    elif name == "nb4":
      return "classifiers/movie_reviews_NaiveBayes_4gram.pickle"
    elif name == "nb5":
      return "classifiers/movie_reviews_NaiveBayes_5gram.pickle"
    elif name == "nb12":
      return "classifiers/movie_reviews_NaiveBayes_1-2gram.pickle"
    elif name == "nb123":
      return "classifiers/movie_reviews_NaiveBayes_1-2-3gram.pickle"
    elif name == "nb1234":
      return "classifiers/movie_reviews_NaiveBayes_1-2-3-4gram.pickle"
    elif name == "dt1":
      return "classifiers/movie_reviews_DecisionTree_1gram.pickle"
    elif name == "dt2":
      return "classifiers/movie_reviews_DecisionTree_2gram.pickle"
    elif name == "dt3":
      return "classifiers/movie_reviews_DecisionTree_3gram.pickle"
    elif name == "dt4":
      return "classifiers/movie_reviews_DecisionTree_4gram.pickle"
    elif name == "dt12":
      return "classifiers/movie_reviews_DecisionTree_1-2gram.pickle"
    elif name == "svc12":
      return "classifiers/movie_reviews_SVC_1-2gram.pickle"
    elif name == "knn1":
      return "classifiers/movie_reviews_KNN_1gram.pickle"
    elif name == "knn12":
      return "classifiers/movie_reviews_KNN_1-2gram.pickle"
    elif name == "gbc12":
      return "classifiers/movie_reviews_GradientBoostingClassifier_1-2gram.pickle"
    else:
      print( "Unknown Classifier chosen, defaulting to Naive Bayes" )
      return "classifiers/movie_reviews_NaiveBayes_1-2gram.pickle"

  def set_classifier( self, name ):
    if self.clf[name][0] is None:
      self.clf[name][0] = nltk.data.load( self.clf_string( name ) )
      self.ngrams = self.clf[name][2]
      self.prob = self.clf[name][1]
      self.cur_clf = name
    """
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
    elif name == 'nb_fivegram':
      if self.nb_fivegram is None:
        self.nb_fivegram = nltk.data.load("classifiers/movie_reviews_NaiveBayes_5gram.pickle")
      self.classifier = self.nb_fivegram
      self.ngrams = 5
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
    elif name == 'dt_threegram':
      if self.dt_threegram is None:
        self.dt_threegram = nltk.data.load("classifiers/movie_reviews_DecisionTree_3gram.pickle")
      self.classifier = self.dt_threegram
      self.ngrams = 3
    """
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

from re import X

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


class CustomLogisticRegression(object):
    '''
    '''

    def __init__(self, reviews, labels, tsize):
        '''
        '''

        #  train / test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            reviews, labels, test_size=tsize, random_state=69)
        self.vectorizer = CountVectorizer()
        self.model = LogisticRegression()

    def train_model(self):
        '''
        '''
        # vectorize the test data
        self.ctmTr = self.vectorizer.fit_transform(self.X_train)
        self.X_test_dtm = self.vectorizer.transform(self.X_test)

        # train model -- need to log the output from this*!
        self.model.fit(self.ctmTr, self.X_test_dtm)

    def check_model_accuracy(self):
        '''
        '''
        self.y_pred_class = self.model.predict(self.X_test_dtm)

        self.score = accuracy_score(self.y_test, self.y_pred_class)

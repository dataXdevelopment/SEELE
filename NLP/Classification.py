import os
import random
import re

import numpy as np
import pandas as pd
import spacy
import tensorflow as tf
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from spacy.util import compounding, minibatch


class BinaryClassifier(object):

    def __init__(self, articles, labels):

        ## data bundling from raw data ## split T/T data

        ## base model

        self.cv = CountVectorizer()

        self.model = LogisticRegression()

        ## optimiser


class BertClassifier(object):

    def __init__(self):

        self.model = TFBertForSequenceClassification.from_pretrained(
            "bert-base-uncased")

        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


class GlobalOptimiser(object):

    def __init__(self, lrate, eps, cnorm):

        self.optimiser = tf.keras.optimizers.Adam(learning_rate=lrate,
                                                  epsilon=eps,
                                                  clipnorm=cnorm)

        ## loss function

        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

        ## metrics

        metrics = [tf.keras.metrics.SparseCategoricalAccuracy("accuracy")]

        ## compile the optimiser

        model.compile(optimizer=self.optimizer,
                      loss=self.loss,
                      metrics=self.metrics)

        ## fit the model

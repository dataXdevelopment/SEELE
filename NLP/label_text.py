import nltk
import pandas as pd

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer  # noqa: E402


def read_file(filename):
    '''

    '''
    df = pd.read_csv(filename)

    return df


def clean_data(df):
    '''
    Note that you shouldn't remove emoji if parsing into Vader;
    This is because Vader uses the emoji to determine sentiment
    '''
    # remove emoji if  necessary
    df.astype(str).apply(
        lambda x: x.str.exsncode('ascii', 'ignore').str.decode('ascii'))

    return df


def label_sentiment_manual(df):
    '''
    Label sentiment based on the numerical rating (1-10)
    assigned to the review. If review / text has no rating we will have
    to use Vader to assign a sentiment label. Ref. Label Sentinment 02? #

    Labels range: Positive, Negative, Neutral
    '''

    # containers
    ls = []

    # labels
    for row in df.iterrows():
        if row['rating'] >= 7:
            label = '1'  # positive
        elif row['rating'] <= 4:
            label = '-1'  # negative
        else:
            label = '0'  # neutral
        ls.append(label)

    df['manual_labels'] = ls

    return df


def label_sentinment_vader(df):
    '''
    '''
    sid = SentimentIntensityAnalyzer()

    df['vader_scores'] = df['review'].apply(
        lambda review: sid.polarity_scores(review))

    df['vader_compound'] = df['vader_scores'].apply(
        lambda score_dict: score_dict['compound'])

    # needs fix - assign range for Neutral values
    df['comp_score'] = df['vader_compound'].apply(lambda x: '1'
                                                  if x >= 0 else '-1')

    return df

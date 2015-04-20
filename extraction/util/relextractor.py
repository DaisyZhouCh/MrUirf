# -*- coding: utf-8 -*-

from nltk.corpus import stopwords
from pymongo     import MongoClient

def relevance_chi_square(coll, text):

    flag     = text['flag']
    tokens   = text['tokens']
    content  = text['content']
    entities = text['entity']
    print '-'*60
    print content

    for entity in entities:

        print entity

        entity_word = entity['word']
        entity_type = entity['type']

        exile_words = stopwords.words('english')
        exile_words.append(entity_word) # entity itself need not execute relevance
        exile_puncs = ['!', '"', '#', '$', '%', '&', '\'','(', ')', '*', '+',
                       ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', 
                       '[', '\\',']', '^', '_', '`', '{', '|', '}', '~', '...']
        exile_words = exile_words + exile_puncs

        # calculate the relevance scores of every word and the entity
        for token in [t for t in tokens if t.lower() not in exile_words]:
            n11 = 0.0   # token hit     |   type hit
            n10 = 0.0   # token hit     |   type not hit
            n01 = 0.0   # token not hit |   type hit
            n00 = 0.0   # token not hit |   type not hit

            corpus      = coll.find().limit(100)
            for corpus_peer in corpus:
                corpus_texts = corpus_peer['texts']

                for corpus_text in corpus_texts:
                    ct_entity_types = corpus_text['entity_types']
                    ct_tokens       = corpus_text['tokens']

                    if token in ct_tokens:
                        if entity_type in ct_entity_types:  n11 += 1
                        else :                              n10 += 1
                    else:
                        if entity_type in ct_entity_types:  n01 += 1
                        else :                              n00 += 1

            n   = n11 + n10 + n01 + n00
            e11 = n * ((n11+n10)/n) * ((n11+n01)/n)
            e10 = n * ((n10+n11)/n) * ((n10+n00)/n)
            e01 = n * ((n01+n11)/n) * ((n01+n00)/n)
            e00 = n * ((n00+n10)/n) * ((n00+n01)/n)
            X2  = 0

            pairs = [{'n':n11, 'e':e11}, {'n':n10, 'e':e10},
                     {'n':n01, 'e':e01}, {'n':n00, 'e':e00}] 
            for pair in pairs: X2 += ((pair['n'] - pair['e']) ** 2) / pair['e']

            # if X2 value greater than or equal to 10.83
            # means the relevance rate of entity and token is greater than 0.999
            if X2 >= 10.83: print token, X2

    return

if __name__ == '__main__':

    client = MongoClient('mongodb://localhost:27017/')

    twcoll = client.msif.twitter_tweets

    sample = twcoll.find_one({'username':'@Pat_M514'})

    tweets = sample['texts'][90:110]

    for tweet in tweets:

        relevance_chi_square(twcoll, tweet)

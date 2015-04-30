# -*- coding: utf-8 -*-

'''
    MEMO
    2015-4-30
    1. In the first test, we choose the peers crawled in 2015-04-23, totally 100
peers, as corpus. In this corpus, we induce more than 300,000 tweets and more
than 60,000 patterns. So we want to filter out a set of patterns, which peers
using most and the size of the set will not be too big. After evaluation, we
found that those patterns talked by more than 40 peers are frequently used, and
the tweets in these patterns make up nearly 60 percent. Finally we determined to
use this set.
    2. Then we find that the patterns used by more than 40 people are always
short ones, which do not contain any infomation. So we need filter pattern
length also. In the evaluate we find the patterns whose length greater than or
equal to 8 make up nearly 80 percent. Finally we determined to filter out those
patterns longer than or equal to 8. However, the rule together with the rule
above: used by more than 40 people, the result only make up 5 percent in all
tweets. To make the test set larger, we modify the rules: 1. the pattern longer
than or equal to 7, which make up 90 percent patterns; 2. the pattern used by
more than 10 peers, which means used by more than 10 percent peers in corpus, as
if in a larger corpus like real twitter, it is still a huge and convinced test
set. Filtering under these two rule, we filter out 10 percent tweets.
'''

import re
from pymongo     import MongoClient

def convert_pos(pos):

    adv_set = ['RB', 'RBR', 'RBS', 'WRB']               # for adverb
    adj_set = ['JJ', 'JJR', 'JJS']                      # for adjective
    det_set = ['',   'DT', 'PDT', 'WDT']                # for determiner
    prp_set = ['PR', 'PRP', 'PRP$','WP',  'WP$']        # for pronoun
    veb_set = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'] # for verb
    nou_set = ['NN', 'NNS', 'NNP', 'NNPS']              # for noun
    jun_set = ['',   'TO',  'CC',  'CD',  'UH',  'RP',  # for junk
               'IN', 'MD',  'LS',  'EX',  'POS', '-LRB-', 
               '-NONE-',    '$',   '#',   '\'',  ':', '`']

    if   pos in adv_set: return adv_set[0]
    elif pos in adj_set: return adj_set[0]
    elif pos in det_set: return det_set[0]
    elif pos in prp_set: return prp_set[0]
    elif pos in veb_set: return veb_set[0]
    elif pos in nou_set: return nou_set[0]
    elif pos in jun_set: return jun_set[0]
    else : return pos

def pos_sentence_collection(db, filter):

    sents  = db.twitter_sentences
    peers  = db.twitter_tweets.find(filter)

    for peer_index, peer in enumerate(peers):

        texts    = peer['texts']
        texts_len= len(texts)
        username = peer['username']
        print "STAT: %s %s" % ( username, '-'*50 )
        print "STAT: This is the %s peer." % str(peer_index + 1)
        print "STAT: Start sentences pattern scanning."

        for text_index, text in enumerate(texts):

            if text_index % 300 == 0 :
                print "STAT: %s %% scanned."   \
                % str( 100 * float(text_index) / texts_len )[:5]

            if len(text['entity_types']) == 0 : continue

            pos     = [convert_pos(item[1]) for item in text['pos']]
            pos     = [item for item in pos if not item == '']
            pos_str = " ".join( pos )
            pos_lst = re.split(r'[.|,]', pos_str)

            for item in pos_lst:
                if len(item) > 0 and item[0] == ' ': item = item[1:]
                if len(item) > 0 and item[-1]== ' ': item = item[:len(item)-1]
                if len(item) ==0: continue

                pattern = sents.find_one({'pattern':item})
                if pattern == None:
                    data = {}
                    data['pattern'] = item
                    set_first       = {'username':username, 'index':text_index, 
                                       'entity':[], 'relevance_index':[]}
                    data['set']     = [set_first]
                    sents.insert(data)
                else:
                    sets = pattern['set']
                    for set in sets:
                        if text_index == set['index'] and \
                           username   == set['username']:
                            break
                    else:
                        set_new = {'username':username, 'index':text_index,
                                   'entity':[], 'relevance_index':[]}
                        sets.append(set_new)
                        sents.update({'pattern':item}, {'$set':{'set':sets}})

        print "SUCC: Scan done."
        print
        print

def evaluate_people_limit(db, people_limit, pattern_len = 0):

    sents   = db.twitter_sentences
    patterns= sents.find()
    result  = []

    for pattern in patterns:
        item = {}
        item['pattern'] = pattern['pattern']
        item['people'] = []
        item['sentences'] = len(pattern['set'])
        for set in pattern['set']:
            if set['username'] not in item['people']:
                item['people'].append(set['username'])
        item['people'] = len(item['people'])

        result.append(item)

    all = sum([item['sentences'] for item in result])
    filter = []
    for item in result:
        if item['people'] >= people_limit:
            if len(item['pattern'].split()) >= pattern_len:
                filter.append(item)
    fter= sum([item['sentences'] for item in filter])
    print "fter in all: %s %%" % str(100 * float(fter) / all)
    print "patterns: %d" % len(filter)

    with file('frequent_patterns.txt', 'w') as f:
        for item in filter:
            f.write('%s\t%s\t%s\n' % (item['pattern'], item['people'], \
                    item['sentences']))

def evaluate_pattern_len(db, pattern_len):

    twsent  = db.twitter_sentences
    sents   = twsent.find()
    all     = sents.count()
    result  = []

    for sent in sents:
        if len(sent['pattern'].split()) >= pattern_len:
            result.append(sent)
    result = len(result)

    print "result in all: %s %%" % str(100 * float(result) / all)


if __name__ == "__main__":

    client = MongoClient('mongodb://localhost:27017/')
    twdb   = client.msif

    # pos_sentence_collection(twdb, {'time':'2015-04-23'})
    # evaluate_pattern_len(twdb, 7)
    # evaluate_people_limit(twdb, 10, 7)

    ''' to fix cursor timeout
    twsents= twdb.twitter_sentences
    tweets = twdb.twitter_tweets
    people = []
    peers = tweets.find({'time':'2015-04-23'})
    for peer in peers:
        people.append(peer['username'])

    people_have = []
    sents = twsents.find()
    for sent in sents:
        sets = sent['set']
        for set in sets:
            peer = set['username']
            if peer not in people_have:
                people_have.append(peer)

    people_not = [peer for peer in people if peer not in people_have]

    for peer in people_not:
        pos_sentence_collection(twdb, {'username':peer})
    '''


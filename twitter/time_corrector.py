import re
from pymongo  import MongoClient
from datetime import datetime, date

if __name__ == "__main__":

    client = MongoClient('mongodb://localhost:27017/')
    tweets = client.mruirf.twitter_tweets
    peers  = tweets.find()

    for peer in peers:
        peer_time = peer['time']
        p_time_lst= peer_time.split('-')
        year = int(p_time_lst[0])
        month= int(p_time_lst[1])
        day  = int(p_time_lst[2])
        peer_time = date(year, month, day)

        texts  = peer['texts']
        for text in texts[::-1]:
            text_time = text['time']
            if re.match(r'\d+s', text_time): text_time = str(peer_time)
            t_time_lst= text_time.split('-')
            year = int(t_time_lst[0])
            month= int(t_time_lst[1])
            day  = int(t_time_lst[2])
            text_time = date(year, month, day)

            if text_time > peer_time:
                text_time = date(year-1, month, day)
                text['time'] = str(text_time)

        tweets.update({'username':peer['username']}, {'$set':{'texts':texts}})


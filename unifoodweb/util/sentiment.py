import sqlite3
from pprint import pprint
from LDA import *
from JST import *
from db_manager import *


def intersect(a, b):
    return list(set(a) & set(b))


def readData(users = None):

    if users == None:
        doc_set = execute_select('SELECT id,text,score FROM rating')
        reviews = []
        score = []
        for d in doc_set:
            reviews.append(d[1])
            score.append(d[2])
        return reviews, score
    else:
        reviews = []
        score = []
        join = '"' + '","'.join(str(u) for u in users) + '"'
        doc_set = execute_select('SELECT id,text,score FROM rating where userid in (' + join + ')')
        for d in doc_set:
            reviews.append(d[1])
            score.append(d[2])

    return reviews, score


def buildJstModel(users = None, words = 10, topics = 5, iterations = 20):

    reviews, score = readData(users)
    sampler = Jst(topics, 2.5, 0.3, 0.1)
    sampler.run(reviews, score, iterations, None, True)

    topics = sampler.getTopKWords(words)
    execute_statement('DELETE FROM topic')
    for index, top in enumerate(topics):
        join = ','.join(str(e) for e in top[2])
        execute_statement(
            'INSERT INTO topic VALUES (' + str(index) + ',' + str(top[0]) + ',' + str(top[1]) + ',"' + join + '")')


def update_experience_crs(crs, users, value):
    for user in users.split(','):
        statement = 'update user set experience = experience + '+str(value) + ' where id = "' + user+'"'
        # print(statement)
        crs.execute(statement)


def update_experience(users, value):
    for user in users.split(','):
        statement = 'update user set experience = experience + '+str(value) + ' where id = "' + user+'"'
        execute_statement(statement)


def calculate_users_experience(user_list):
    users = '"' + '","'.join(str(u) for u in user_list) + '"'
    products = execute_select('select DISTINCT(productid) FROM rating WHERE userid IN ('+users+')')
    inc = 0
    execute_statement('update user set experience = 0')
    for product in products:
        print(product)
        inc = inc + 1
        select = "select group_concat(userid),count(score) as num_score from rating where productid = '"+product[0]+"' group by score order by num_score desc"
        rat = execute_select(select)
        value = 1
        tmp = 0
        rate = 1/len(rat)
        for r in rat:
            if r[1] != tmp:
                value = value - rate
                tmp = r[1]
                update_experience(r[0], value)


def getRateDistribution(userRate,user_words, topic_words):

    topic_words = topic_words.split(',')
    distribution = []
    display = False
    for rate in userRate:
        product_words = (execute_select('select words from product where id = "' + rate[0] + '"'))
        pprint(rate[0])
        if product_words[0][0] == None:
            ldaProduct(rate[0])
        product_words = (execute_select('select words from product where id = "' + rate[0] + '"')[0][0]).split(',')
        user_product = intersect(user_words,product_words)
        pprint(intersect(user_product,topic_words))
        inters = len(intersect(user_product,topic_words))
        if inters > 0:
            display = True
        distribution.append(inters)

    # print(distribution)
    return distribution,display


def getUserDistribution(userId):

    userRates = execute_select('select productid from rating where userid = "'+userId+'" order by timestamp')
    pos_neg_words = execute_select('select pos_words,neg_words  from user where id = "'+userId+'"')[0]
    if pos_neg_words[0] == None:
        ldaUser(userId)
        pos_neg_words = execute_select('select pos_words,neg_words from user where id = "'+userId+'"')[0]
    user_words = (str(pos_neg_words[0])+','+str(pos_neg_words[1])).split(',')
    topics = execute_select('SELECT id, sentiment, words from topic order by id')

    topic_pos = []
    topic_neg = []
    for t in topics:
        chart_data = ['Topic_'+str(t[0])]
        distrib, display = getRateDistribution(userRates, user_words, t[2])
        if not display:
            continue
        chart_data.extend(distrib)
        words = []
        for w in str(t[2]).split(','):
            words.append(w)
        if t[1] == 1:
            sent = 'Positive'
            topic_pos.append([['Topic_'+str(t[0]), sent, words], chart_data])
        else:
            sent = 'Negative'
            topic_neg.append([['Topic_'+str(t[0]), sent, words], chart_data])
    # for t in topic_pos:
    #     print(t)
    return [topic_pos, topic_neg]


def getProductDistribution(productId):
    words = execute_select('select words from product where id = "'+productId+'"')[0][0]
    if words == None:
        ldaProduct(productId)
        words = execute_select('select words from product where id = "'+productId+'"')[0][0]
    topics = execute_select('SELECT id, sentiment, words from topic order by id')

    topic_pos = []
    topic_neg = []
    chart_data = []
    for t in topics:
        tpc_chart_data = ['Topic_'+str(t[0]), len((intersect(t[2], words[0])))]
        if tpc_chart_data[1] < 0:
            continue
        words = []
        for w in str(t[2]).split(','):
            words.append(w)
        if t[1] == 1:
            sent = 'Positive'
            topic_pos.append([['Topic_'+str(t[0]), sent, words], tpc_chart_data])
        else:
            sent = 'Negative'
            topic_neg.append([['Topic_'+str(t[0]), sent, words], tpc_chart_data])
    for t in topic_pos:
        chart_data.append(t[1])
    for t in topic_neg:
        chart_data.append(t[1])
    # print(topic_pos, topic_neg, chart_data)
    return [topic_pos, topic_neg, chart_data]
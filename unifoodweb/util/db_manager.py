import sqlite3, csv, sys
from math import pow
from pprint import pprint


path_database = 'reviewapp.db'
# path_database = 'dataset.db'


class ProgressBar():

    def __init__(self, blen, slen):
        self.bar_len = blen
        self.total = slen
        self.current = 0

    def step(self):
        self.current += 1
        current_len = int(round(self.bar_len * self.current / float(self.total)))
        perc = round(100.0 * self.current / float(self.total), 1)
        bar = '=' * current_len + '-' * (self.bar_len - current_len)
        sys.stdout.write('\r[%s] %s%s | %s / %s' % (bar, perc, '%', self.current, self.total))
        sys.stdout.flush()


def set_database_path(path):
    global path_database
    path_database = path


def initialize_util():
    global path_database

    # connect to database (or create it)
    db = sqlite3.connect(path_database)
    crs = db.cursor()

    print('DROP TABLEs utils')
    # clean db of dataset
    crs.execute('DROP TABLE IF EXISTS utils')
    db.commit()

    print('CREATE TABLEs utils\n')
    # create utils table
    crs.execute('''CREATE TABLE IF NOT EXISTS utils
										(id integer PRIMARY KEY, type text, name text)''')
    db.commit()

    db.close()


def initialize_dataset():
    global path_database

    # connect to database (or create it)
    db = sqlite3.connect(path_database)
    crs = db.cursor()

    print('DROP TABLEs rating, user, product,topic')
    # clean db of dataset
    crs.execute('DROP TABLE IF EXISTS product')
    crs.execute('DROP TABLE IF EXISTS user')
    crs.execute('DROP TABLE IF EXISTS rating')
    crs.execute('DROP TABLE IF EXISTS topic')
    db.commit()

    print('CREATE TABLEs rating, user, product\n')
    # create ratings table
    crs.execute('''CREATE TABLE IF NOT EXISTS rating
										(id integer PRIMARY KEY,
										productid text, userid text, score real, text text,timestamp int)''')
    # create users table
    crs.execute('''CREATE TABLE IF NOT EXISTS user
										(id text PRIMARY KEY, num_rating int, av_score real, var_score real, experience real, experience_level real, pos_words text,neg_words text)''')
    # create products table
    crs.execute('''CREATE TABLE IF NOT EXISTS product
										(id text PRIMARY KEY, num_rating int, av_score real, var_score real,words text)''')
    crs.execute('''CREATE TABLE IF NOT EXISTS topic
											(id int PRIMARY KEY, name text, sentiment int, words text)''')
    db.commit()

    db.close()


def execute_select(select):
    global path_database
    db = sqlite3.connect(path_database)
    crs = db.cursor()
    crs.execute(select)
    result = crs.fetchall()
    db.close()
    return result


def execute_statement(statement):
    global path_database
    db = sqlite3.connect(path_database)
    crs = db.cursor()
    while True:
        try:
            crs.execute(statement)
            break
        except:
            None
    db.commit()
    db.close()
    return


def calculate_variance(object_data):
    numerator = 0
    for rate in object_data[3]:
        numerator += pow((float(rate) - object_data[2]), 2)
    return abs(numerator / float(object_data[1]))


def import_dataset(filename):
    global path_database
    # connect to database
    db = sqlite3.connect(path_database)
    crs = db.cursor()

    # RATINGS
    print('INSERT INTO rating')
    # setup progress bar
    len_dataset = sum(1 for _ in open(filename, 'r', encoding='utf-8', errors='ignore'))
    prgbar = ProgressBar(40, len_dataset)
    # read dataset
    with open(filename, 'r', encoding='utf-8', errors='ignore') as food:
        dataset = csv.reader(food, delimiter='\n')
        # jump first row
        next(dataset)
        # for each row, insert values in db
        for index, row in enumerate(dataset):
            x = row[0].split('\t')
            crs.execute("INSERT INTO rating VALUES (?,?,?,?,?)", (index,str(x[0]), str(x[1]), x[2], str(x[3])))
            prgbar.step()
    db.commit()

    # USERS
    crs.execute("SELECT DISTINCT(userid),count(score),AVG(score),GROUP_CONCAT(score) FROM rating GROUP BY userid")
    list_users = crs.fetchall()
    # setup progress bar
    prgbar = ProgressBar(40, len(list_users))
    print('INSERT INTO user')
    parameters = []
    for user in list_users:

        # create object user_data to store [userid, count, avg, rating_list, var]
        user_data = []
        user_data.append(user[0])
        user_data.append(user[1])
        user_data.append(user[2])
        # get all score ratings of user
        user_data.append(user[3].split(','))
        # calculate variance
        user_data.append(calculate_variance(user_data))
        parameters.append((user_data[0], user_data[1], user_data[2], user_data[4], 0, None, None, None))
        prgbar.step()
    crs.executemany("INSERT INTO user VALUES (?,?,?,?,?,?,?,?)", parameters)
    db.commit()

    # PRODUCTS
    crs.execute("SELECT DISTINCT(productid),count(score),AVG(score),GROUP_CONCAT(score) FROM rating GROUP BY productid")
    list_products = crs.fetchall()
    # setup progress bar
    prgbar = ProgressBar(40, len(list_products))
    parameters = []
    print('\nINSERT INTO product')
    for product in list_products:
        # create object product_data to store
        product_data = []
        product_data.append(product[0])
        product_data.append(product[1])
        product_data.append(product[2])
        # get all score ratings of user
        product_data.append(product[3].split(','))
        # calculate variance
        product_data.append(calculate_variance(product_data))
        parameters.append((product_data[0], product_data[1], product_data[2], product_data[4],None))
        prgbar.step()
    crs.executemany("INSERT INTO product VALUES (?,?,?,?,?)", parameters)
    db.commit()
    db.close()


def import_json(filename):
    global path_database
    # connect to database
    db = sqlite3.connect(path_database)
    crs = db.cursor()
    import json


    # RATINGS
    print('INSERT INTO rating')
    # setup progress bar
    len_dataset = sum(1 for _ in open(filename, 'r', encoding='utf-8', errors='ignore'))
    prgbar = ProgressBar(40, len_dataset)
    # read dataset
    with open(filename, 'r', encoding='utf-8', errors='ignore') as food:

        for index, row in enumerate(food):
            x = json.loads(row)
            crs.execute("INSERT INTO rating VALUES (?,?,?,?,?,?)", (index,str(x['asin']), str(x['reviewerID']), str(x['overall']), str(x['reviewText']),str(x['unixReviewTime'])))
            prgbar.step()
    db.commit()
    print()

    # USERS
    crs.execute("SELECT DISTINCT(userid),count(score),AVG(score),GROUP_CONCAT(score) FROM rating GROUP BY userid")
    list_users = crs.fetchall()
    # setup progress bar
    prgbar = ProgressBar(40, len(list_users))
    print('INSERT INTO user')
    parameters = []
    for user in list_users:

        # create object user_data to store [userid, count, avg, rating_list, var]
        user_data = []
        user_data.append(user[0])
        user_data.append(user[1])
        user_data.append(user[2])
        # get all score ratings of user
        user_data.append(user[3].split(','))
        # calculate variance
        user_data.append(calculate_variance(user_data))
        parameters.append((user_data[0], user_data[1], user_data[2], user_data[4], 0, None, None,None))
        prgbar.step()
    crs.executemany("INSERT INTO user VALUES (?,?,?,?,?,?,?,?)", parameters)
    db.commit()

    # PRODUCTS
    crs.execute("SELECT DISTINCT(productid),count(score),AVG(score),GROUP_CONCAT(score) FROM rating GROUP BY productid")
    list_products = crs.fetchall()
    # setup progress bar
    prgbar = ProgressBar(40, len(list_products))
    parameters = []
    print('\nINSERT INTO product')
    for product in list_products:
        # create object product_data to store
        product_data = []
        product_data.append(product[0])
        product_data.append(product[1])
        product_data.append(product[2])
        # get all score ratings of user
        product_data.append(product[3].split(','))
        # calculate variance
        product_data.append(calculate_variance(product_data))
        parameters.append((product_data[0], product_data[1], product_data[2], product_data[4], None))
        prgbar.step()
    crs.executemany("INSERT INTO product VALUES (?,?,?,?,?)", parameters)
    db.commit()
    db.close()

from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import theano.tensor as T
from libs import cnn
import pickle
from libs.color_matcher import ColorMatcher


USERS_LENGTH = 14
RATINGS_LENGTH = 843
LIKE = 1
DISLIKE = 0.1
basic_info = "details, brand_name, img_url, product_name, productid, product_url, love_count"
import os
face_categories = pickle.load(open('app/libs/data/face_categories.pkl', 'rb'))
def loss_func(y_true, y_pred):
    temp = np.dot(y_true, y_pred)
    temp_true = y_true.nonzero_values()
    temp_pred = temp.nonzero_values()
    temp_pred = temp_pred / temp_true
    loss = T.mean((temp_pred - temp_true)**2)
    return loss

class Recommender:
    def __init__(self):
        self.offset = 0
        self.cnx = create_engine('postgresql://ubuntu:pinpass@34.205.76.95:5432/ubuntu')
        self.model, _ = cnn.load('rec/autoencoder_model')
        self.model.compile(loss = loss_func, optimizer = 'adadelta')
        self.tried_products = set()
        self.suggestions = []
        self.cm = ColorMatcher()
        self.pred_ratings = None
        self.user_cats = pickle.load(open('app/libs/data/rec/user_cats.pkl', 'rb'))


    def fetch_popular(self, n, offset=0):
        qry = '''SELECT {} FROM product ORDER BY rev_count
         DESC limit {} OFFSET {}'''.format(basic_info, n, offset)
        selection = pd.read_sql_query(qry,self.cnx)
        return selection.to_json()

    def fetch_all_products(self):
        qry = '''SELECT product_name, productid FROM product'''
        products = pd.read_sql_query(qry, self.cnx)
        return products.to_json()

    def fetch_product(self, pid):
        qry = '''SELECT {} FROM product WHERE productid={}'''.format(basic_info, pid)
        product = pd.read_sql_query(qry, self.cnx)
        return product.to_json()

    def get_pred_array(self, likes, dislikes=[], users_data=None):
        # self.tried_products = self.tried_products.union(set(likes + dislikes))
        preferences = np.zeros(RATINGS_LENGTH)
        for like in likes:
            if like <= RATINGS_LENGTH:
                preferences[like] = LIKE
        for dislike in dislikes:
            if dislike <= RATINGS_LENGTH:
                preferences[dislike] = DISLIKE
        if not users_data:
            users_data = np.zeros(USERS_LENGTH)
        pred = self.model.predict([users_data.reshape(1, -1),
            preferences.reshape(1, -1)])
        return list(enumerate(pred[0]))

    def get_skin_color(self, img):
        return self.cm.compute_skin_color(img)

    def recommend_products_with_skin_color(self, category, skin_color, tried_products=[], pred_ratings=None):
        products = self.cm.get_products(category, skin_color)
        products = products.sort_values("dist")
        if pred_ratings:
            # products is already limited to the ones close to skin color.
            ranked = np.take(pred_ratings, products.productid.values, axis=0)
            products['pred_ratings'] = ranked[:, 1]
            products = products[products.pred_ratings > 0.5]
        # products = products.groupby("productid").head
        products = products[products.productid.isin(tried_products) == False]
        return products

    def recommend_products(self, category, pred_ratings, tried_products=[]):
        q = """SELECT {} FROM product WHERE categories LIKE '%%{}%%'""".format(basic_info, category)
        products = pd.read_sql(q, self.cnx)
        products['pred_ratings'] = np.take(pred_ratings, products.productid.values, axis=0)[:, 1]
        products = products.sort_values(['pred_ratings'], ascending=[False])
        products = products[products['productid'].isin(tried_products) == False]
        return products

    def recommend(self, category, likes=[], dislikes=[], skin_color=None, age=None, eye_color=None, topn=10):
        user_data = None
        pred_ratings = None
        if age:
            user_data = self.insert_age_info(age, user_data)
        if eye_color:
            user_data = self.insert_eye_color(eye_color, user_data)
        tried_products = set(likes + dislikes)
        pred_ratings = self.get_pred_array(likes, dislikes, user_data)
        if skin_color and category in face_categories:
            products = self.recommend_products_with_skin_color(category,\
                skin_color, tried_products=tried_products,\
                pred_ratings=pred_ratings)
            products = products.head(topn)
            return products
        products = self.recommend_products(category, pred_ratings=pred_ratings,\
            tried_products=tried_products).head(topn)
        return products
        # no preferences, sending popular products instead

    def insert_eye_color(self, value, user_data=None):
        label = "eye_color[T.{}]".format(value)
        if label not in self.user_cats:
            return
        ind = self.user_cats.index(label)
        user_data[ind] = 1
        return user_data

    def insert_age_info(self, age, user_data=None):
        if not user_data:
            user_data = np.zeros(USERS_LENGTH)
        if age < 18:
            return
        if age <= 24:
            ind = 0
        elif age <= 34:
            ind = 1
        elif age <= 44:
            ind = 2
        elif age <= 54:
            ind = 3
        else:
            ind = 4
        user_data[ind] = 1
        return user_data

from libs import cnn, img_processing
from sqlalchemy import create_engine
from sklearn.metrics import pairwise
import numpy as np
import pandas as pd

basic_info = "brand_name, img_url, product_name, productid, product_url, love_count"

class ColorMatcher(object):
    def __init__(self):
        self.model, _ = cnn.load('skin/skin_model')
        self.im_p = img_processing.ImageProcessor('app/libs/data/skin/face.xml')
        self.cnx = create_engine('postgresql://ubuntu:pinpass@34.205.76.95:5432/ubuntu')

    def compute_skin_color(self, img):
        face = self.im_p.crop_face(img, 45)
        face = self.im_p.crop_face(img, 45)
        face_arr = self.im_p.img_to_arr(face)
        assert face_arr.shape == (299, 299, 3)
        pred = self.model.predict(np.expand_dims(np.swapaxes(face_arr, 0, 2), axis=0))
        return self.im_p.arr_to_color(pred)[0]

    def get_products(self, category, skin_color, threshold=30):
        q = """SELECT * FROM color WHERE product_id in (SELECT product_id FROM product
        WHERE categories LIKE '%%{}%%')""".format(category)
        face_colors = pd.read_sql(q, self.cnx)
        X = face_colors[['red', 'green', 'blue']]
        face_colors['dist'] = pairwise.euclidean_distances(X, skin_color)
        face_colors = face_colors[face_colors.dist < threshold]
        keys = face_colors.color_id.values
        q = """SELECT {}, product_id FROM product WHERE product_id in
        (SELECT product_id FROM color WHERE color_id in ({}))"""\
        .format(basic_info, ','.join(str(x) for x in keys))
        best_c = pd.read_sql(q, self.cnx)
        return pd.merge(best_c, face_colors, on='product_id').sort_values('dist')

import cv2
from PIL import Image
from keras.preprocessing import image as image_utils
import numpy as np
import requests
from io import BytesIO

class ImageProcessor:
    def __init__(self, xml):
        self.FACE_CASCADE = cv2.CascadeClassifier(xml)


    def get_bounds(self, img_arr):
        """Returns the coordinates of the face"""
        gray = self.fetch_gray(img_arr)
        faces = self.FACE_CASCADE.detectMultiScale(gray, 1.3, 6)
        x = 6
        while len(faces) == 0 and x > 0:
            x -= 1
            faces = self.FACE_CASCADE.detectMultiScale(gray, 1.3, x)
        if len(faces) < 1:
            return None
        face = faces[0]
        crop = [face[0], face[1], face[0] + face[2], face[1] + face[3]]
        return crop


    def fetch_gray(self, img):
        """Get the image in greyscale for CV2"""
        cv_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        return gray


    def get_image(self, path, url=False):
        if url:
            response = requests.get(path)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(path)
        return img


    def crop_face(self, img, padding=0):
        """Crop the image with an optional padding"""
        img_arr = np.array(img)
        crop = self.get_bounds(img_arr)
        if not crop:
            return None
        crop[0] += padding
        crop[1] += padding
        crop[2] -= padding
        crop[3] -= padding
        return img.crop(crop)

    def get_color(self, img, bound=25):
        color = img.crop((0, 0, bound, bound))
        color_arr = image_utils.img_to_array(color)
        color_mean = np.mean(color_arr.reshape(3, bound*bound), axis=1)
        color_mean *= 1/255
        return color_mean

    def img_to_arr(self, img, resize=True):
        if resize:
            img = img.resize((299, 299))
        img_arr = image_utils.img_to_array(img)
        img_arr = np.divide(img_arr, 255)
        return img_arr

    def arr_to_color(self, arr):
        return np.multiply(arr, 255)

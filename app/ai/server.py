import os
from flask import Flask, request, render_template, redirect
from tensorflow.keras.preprocessing import image
import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model('breast_cancer_model.h5')

app = Flask(__name__)

@app.route('/')
def predict_cancer():
    img_path = '/data/images/image'
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.
    
    prediction = model.predict(img_array)
    return str(prediction[0][0])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

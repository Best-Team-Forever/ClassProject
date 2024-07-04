import os
from flask import Flask, request, render_template, redirect
from tensorflow.keras.preprocessing import image
import tensorflow as tf
import numpy as np

# Load the saved model
model = tf.keras.models.load_model('breast_cancer_model.h5')

# Function to predict cancer from a single image
def predict_cancer(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.
    
    prediction = model.predict(img_array)
    return prediction[0][0]

app = Flask(__name__, template_folder='.')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            file_path = 'uploaded_image.png'
            file.save(file_path)
            probability = predict_cancer(file_path)
            return render_template('result.html', probability=probability)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

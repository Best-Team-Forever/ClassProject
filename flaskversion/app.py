from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import tensorflow as tf
import numpy as np
import pydicom
import cv2
import os
import csv
from tensorflow.keras.applications.densenet import preprocess_input
import uuid

app = Flask(__name__)

# Load the pre-trained DenseNet121 model
model = tf.keras.models.load_model('fine_tuned_weights.h5')


def preprocess_image(dicom_path):
    dicom = pydicom.dcmread(dicom_path)
    image = dicom.pixel_array
    if image.max() > 0:
        image = (image - image.min()) / (image.max() - image.min())  # Normalize to [0, 1]
    image = cv2.resize(image, (224, 224))
    image = np.stack((image,) * 3, axis=-1)  # Convert to 3 channels
    image = preprocess_input(image)  # Normalize to [-1, 1] if using tf.keras.applications.densenet.preprocess_input
    return image, dicom


def classify_image(image, model):
    image = np.expand_dims(image, axis=0)
    predictions = model.predict(image)
    probability = predictions[0][0]
    label = 'ABNORMAL' if probability > 0.5 else 'NORMAL'
    return label, probability

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        dicom_path = os.path.join('uploads', file.filename)
        file.save(dicom_path)

        try:
            image, dicom = preprocess_image(dicom_path)
            label, probability = classify_image(image, model)

            image_rgb = cv2.cvtColor(dicom.pixel_array.astype(np.uint8), cv2.COLOR_GRAY2RGB)
            annotated_image_path = os.path.join('static', 'annotated_image.png')
            cv2.imwrite(annotated_image_path, image_rgb)

            return render_template('result.html', label=label, probability=probability, image_path='static/annotated_image.png')
        except Exception as e:
            return f"Error processing file {dicom_path}: {e}"

@app.route('/save_patient_info', methods=['POST'])
def save_patient_info():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    comments = request.form['comments']
    label = request.form['label']
    probability = request.form['probability']
    image_path = request.form['image_path']

    patient_id = str(uuid.uuid4())
    image_id = str(uuid.uuid4())
    image_save_path = os.path.join('patient_images', f"{image_id}.png")
    os.makedirs(os.path.join('patient_images'), exist_ok=True)
    os.rename(os.path.join(image_path), image_save_path)

    with open(os.path.join('patient_data.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([patient_id, first_name, last_name, comments, label, probability, image_save_path])

    return redirect(url_for('results'))

@app.route('/results')
def results():
    entries = []
    if os.path.exists(os.path.join('patient_data.csv')):
        with open(os.path.join('patient_data.csv'), mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                entries.append({
                    'patient_id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'comments': row[3],
                    'label': row[4],
                    'probability': row[5],
                    'image_path': row[6]
                })
    return render_template('results.html', entries=entries)

@app.route('/result/<patient_id>')
def result(patient_id):
    if os.path.exists(os.path.join('patient_data.csv')):
        with open(os.path.join('patient_data.csv'), mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == patient_id:
                    # Correct the image path
                    # image_path = row[6].replace('flaskversion/', '')
                    return render_template('result.html', label=row[4], probability=row[5], image_path=image_path, 
                                           first_name=row[1], last_name=row[2], comments=row[3])
    return "Patient not found"

@app.route('/patient_images/<filename>')
def patient_images(filename):
    return send_from_directory(os.path.join('patient_images'), filename)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    if not os.path.exists(os.path.join('uploads')):
        os.makedirs(os.path.join('uploads'))
    if not os.path.exists(os.path.join('static')):
        os.makedirs(os.path.join('static'))
    if not os.path.exists(os.path.join('patient_images')):
        os.makedirs(os.path.join('patient_images'))
    app.run(debug=True)

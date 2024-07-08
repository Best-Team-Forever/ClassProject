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

# Disable template caching
app.config['TEMPLATES_AUTO_RELOAD'] = True

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
        # Ensure the uploads directory exists
        uploads_dir = 'uploads'
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"Uploads directory: {uploads_dir}")

        dicom_path = os.path.join(uploads_dir, file.filename)
        print(f"DICOM path: {dicom_path}")
        file.save(dicom_path)

        try:
            image, dicom = preprocess_image(dicom_path)
            label, probability = classify_image(image, model)
            probability *= 100.0
            probability = round(probability, 2)

            image_rgb = cv2.cvtColor(dicom.pixel_array.astype(np.uint8), cv2.COLOR_GRAY2RGB)
            annotated_image_path = os.path.join('static', 'annotated_image.png')
            print(f"Annotated image path: {annotated_image_path}")
            cv2.imwrite(annotated_image_path, image_rgb)

            # Append cache buster to the image path
            image_path = f'static/annotated_image.png?{uuid.uuid4()}'
            print(f"Image path with cache buster: {image_path}")

            return render_template('result.html', label=label, probability=probability, image_path=image_path)
        except Exception as e:
            return f"Error processing file {dicom_path}: {e}"

@app.route('/save_patient_info', methods=['POST'])
def save_patient_info():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        comments = request.form['comments']
        label = request.form['label']
        probability = request.form['probability']
        image_path = request.form['image_path']

        # Generate unique IDs for the patient and the image
        patient_id = str(uuid.uuid4())
        image_id = str(uuid.uuid4())

        # Define the directory and file path for the image
        image_dir = os.path.join('patient_images')
        image_save_path = os.path.join(image_dir, f"{image_id}.png")
        print(f"Image save path: {image_save_path}")

        # Ensure the directory exists
        os.makedirs(image_dir, exist_ok=True)

        # Move the uploaded image to the designated directory
        os.rename(image_path.split('?')[0], image_save_path)

        # Open the CSV file and append the new patient data
        csv_file_path = os.path.join('patient_data.csv')
        print(f"CSV file path: {csv_file_path}")
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([patient_id, first_name, last_name, comments, label, probability, image_save_path])

        print(f"Successfully saved patient info: {patient_id}, {first_name}, {last_name}")

        # Redirect to the results page after successful data saving
        return redirect(url_for('results'))

    except Exception as e:
        # Handle exceptions (e.g., log the error, return an error message)
        print(f"Error occurred: {e}")
        return "An error occurred while saving patient info.", 500

@app.route('/results')
def results():
    entries = []
    csv_file_path = 'patient_data.csv'
    print(f"CSV file path for reading: {csv_file_path}")
    if os.path.exists(csv_file_path):
        with open(csv_file_path, mode='r') as file:
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
    csv_file_path = 'patient_data.csv'
    print(f"CSV file path for specific patient: {csv_file_path}")
    if os.path.exists(csv_file_path):
        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == patient_id:
                    image_path = f"{row[6]}?{uuid.uuid4()}"  # Append cache buster
                    print(f"Patient image path with cache buster: {image_path}")
                    return render_template('result.html', label=row[4], probability=row[5], image_path=image_path, 
                                           first_name=row[1], last_name=row[2], comments=row[3])
    return "Patient not found"

@app.route('/patient_images/<filename>')
def patient_images(filename):
    file_path = os.path.join('patient_images', filename)
    print(f"Serving patient image: {file_path}")
    return send_from_directory('patient_images', filename)

@app.route('/about')
def about():
    return render_template('about.html')

@app.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('patient_images', exist_ok=True)
    app.run(debug=True)

import os
import uuid

import cv2
import numpy as np
import pydicom
import tensorflow as tf
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from tensorflow.keras.applications.densenet import preprocess_input

from database import Database
from email_service import EmailService

PATIENT_IMAGES = 'patient_images'

app = Flask(__name__)

# Disable template caching
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.database = Database('database', 'patient_data.csv')
app.email_service = EmailService()

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
        annotated_image_directory = 'static'

        os.makedirs(annotated_image_directory, exist_ok=True)
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
            annotated_image_path = os.path.join(annotated_image_directory, f'{uuid.uuid4()}.png')
            print(f"Annotated image path: {annotated_image_path}")

            # Save the image with compression
            compression_params = [cv2.IMWRITE_PNG_COMPRESSION, 9]  # Set the compression level (0-9)
            image_saved = cv2.imwrite(annotated_image_path, image_rgb, compression_params)
            print(f"Annotated image saved: {image_saved}")

            return render_template('result.html', label=label, probability=probability, image_path=annotated_image_path)
        except Exception as e:
            return f"Error processing file {dicom_path}: {e}"


@app.route('/save_patient_info', methods=['POST'])
def save_patient_info():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        comments = request.form['comments']
        label = request.form['label']
        probability = request.form['probability']
        image_path = request.form['image_path']

        image_id, patient_id = generate_ids()

        # Define the directory and file path for the image
        image_save_path = define_image_directory(image_id)

        # Move the uploaded image to the designated directory
        os.rename(image_path.split('?')[0], image_save_path)

        app.database.save_patient_record(patient_id, first_name, last_name, email, comments, label, probability,
                                         image_save_path)

        # Redirect to the results page after successful data saving
        return redirect(url_for('results'))

    except Exception as e:
        # Handle exceptions (e.g., log the error, return an error message)
        print(f"Error occurred: {e}")
        return "An error occurred while saving patient info.", 500


def define_image_directory(image_id):
    if not os.path.exists(PATIENT_IMAGES):
        os.makedirs(PATIENT_IMAGES)
    image_save_path = os.path.join(PATIENT_IMAGES, f"{image_id}.png")
    print(f"Image save path: {image_save_path}")
    # Ensure the directory exists
    # os.makedirs(image_dir, exist_ok=True)
    return image_save_path


def generate_ids():
    # Generate unique IDs for the patient and the image
    patient_id = str(uuid.uuid4())
    image_id = str(uuid.uuid4())
    return image_id, patient_id


@app.route('/results')
def results():
    entries = app.database.read_all_records()
    return render_template('results.html', entries=entries)


@app.route('/result/<patient_id>')
def result(patient_id):
    try:
        label, probability, image_path, first_name, last_name, comments, email = app.database.read_record(patient_id)

        return render_template('result.html', label=label, probability=probability, image_path=image_path,
                               first_name=first_name, last_name=last_name, comments=comments, email=email)
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Patient not found"


@app.route('/send_email/<patient_id>', methods=['POST'])
def send_email(patient_id):
    try:
        label, probability, image_path, first_name, last_name, comments, email = app.database.read_record(patient_id)
        app.email_service.send_email(first_name, last_name, email, float(probability))
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        print(f"Error occurred: {e}")
        return {"status": "error", "message": "Patient not found"}, 500


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
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == "__main__":
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('patient_images', exist_ok=True)
    app.run(debug=True)

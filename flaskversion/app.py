from flask import Flask, request, render_template
import tensorflow as tf
import numpy as np
import pydicom
import cv2
import os
from tensorflow.keras.applications.densenet import preprocess_input

app = Flask(__name__)

# Load the pre-trained DenseNet121 model
model = tf.keras.models.load_model('flaskversion/fine_tuned_weights.h5')

def preprocess_image(dicom_path):
    dicom = pydicom.dcmread(dicom_path)
    image = dicom.pixel_array
    print(f"Original image shape: {image.shape}")
    if image.max() > 0:  # Avoid division by zero
        image = (image - image.min()) / (image.max() - image.min())  # Normalize the images
    image = cv2.resize(image, (224, 224))  # Resize image to the size expected by the model
    image = np.stack((image,)*3, axis=-1)  # Convert to 3 channels
    image = preprocess_input(image)  # Preprocess the images
    return image, dicom

def classify_image(image, model):
    image = np.expand_dims(image, axis=0)  # Add batch dimension
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

            # Save the processed image (without annotations) for display
            image_rgb = cv2.cvtColor(dicom.pixel_array.astype(np.uint8), cv2.COLOR_GRAY2RGB)
            annotated_image_path = 'static/annotated_image.png'
            cv2.imwrite(annotated_image_path, image_rgb)

            return render_template('result.html', label=label, probability=probability, image_path=annotated_image_path)
        except Exception as e:
            print(f"Error processing file {dicom_path}: {e}")
            return f"Error processing file {dicom_path}: {e}"

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)

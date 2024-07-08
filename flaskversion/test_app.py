import unittest
import os
import tempfile
from io import BytesIO
from flask_testing import TestCase
from app import app, preprocess_image, classify_image  # Adjust imports as needed
import tensorflow as tf
import numpy as np
import pydicom
from pydicom.uid import ExplicitVRLittleEndian

class FlaskAppTestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'uploads'
        app.config['STATIC_FOLDER'] = 'static'
        app.config['PATIENT_DATA_FILE'] = 'patient_data.txt'
        app.config['PATIENT_IMAGES_FOLDER'] = 'patient_images'
        app.config['SECRET_KEY'] = 'secret!'
        app.config['SESSION_TYPE'] = 'filesystem'
        return app

    def setUp(self):
        # Set up test data and environment
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        if not os.path.exists(app.config['STATIC_FOLDER']):
            os.makedirs(app.config['STATIC_FOLDER'])
        if not os.path.exists(app.config['PATIENT_IMAGES_FOLDER']):
            os.makedirs(app.config['PATIENT_IMAGES_FOLDER'])

        # Create a dummy DICOM file for testing
        self.dicom_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test.dcm')
        self.create_dummy_dicom(self.dicom_path)



    def create_dummy_dicom(self, path):
        # Create a simple dummy DICOM file for testing
        file_meta = pydicom.dataset.FileMetaDataset()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds = pydicom.dataset.FileDataset(path, {}, file_meta=file_meta, preamble=b"\0" * 128)
        ds.Rows = 256
        ds.Columns = 256
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelData = np.zeros((256, 256), dtype=np.uint8).tobytes()
        ds.save_as(path)

    def create_dummy_image(self, path):
        # Create a simple dummy image file for testing
        image = np.zeros((256, 256, 3), dtype=np.uint8)
        image_path = os.path.join(app.config['STATIC_FOLDER'], path)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Ensure directory exists
        tf.keras.preprocessing.image.save_img(image_path, image)

    # Test No. 1
    def test_index(self):
        """
        Test that the index page loads correctly.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    # Test No. 2
    def test_about(self):
        """
        Test that the about page loads correctly.
        """
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)

    # Test No. 3
    def test_upload_file_no_file(self):
        """
        Test the upload functionality with no file.
        """
        response = self.client.post('/upload', data={})
        self.assertIn(b'No file part', response.data)

    # Test No. 4
    def test_upload_file_no_selected_file(self):
        """
        Test the upload functionality with no selected file.
        """
        response = self.client.post('/upload', data={'file': (BytesIO(b''), '')})
        self.assertIn(b'No selected file', response.data)

    # Test No. 5
    def test_upload_file_valid(self):
        """
        Test the upload functionality with a valid file.
        """
        with open(self.dicom_path, 'rb') as dicom_file:
            response = self.client.post('/upload', data={'file': (dicom_file, 'test.dcm')})
            self.assertEqual(response.status_code, 200)

    # Test No. 6
    def test_preprocess_image(self):
        """
        Test the image preprocessing functionality.
        """
        image, dicom = preprocess_image(self.dicom_path)
        self.assertEqual(image.shape, (224, 224, 3))

    # Test No. 7
    def test_classify_image(self):
        """
        Test the image classification functionality.
        """
        image, _ = preprocess_image(self.dicom_path)
        model = tf.keras.models.load_model('fine_tuned_weights.h5')
        label, probability = classify_image(image, model)
        self.assertIn(label, ['NORMAL', 'ABNORMAL'])
        self.assertTrue(0 <= probability <= 1)

    # Test No. 8
    def test_save_patient_info(self):
        """
        Test saving patient information after classification.
        """
        # Ensure the annotated image exists
        self.create_dummy_image('annotated_image.png')

        with self.client as c:
            with c.session_transaction() as session:
                session['image_path'] = 'static/annotated_image.png'

            response = c.post('/save_patient_info', data={
                'first_name': 'John',
                'last_name': 'Doe',
                'comments': 'Test comment',
                'label': 'NORMAL',
                'probability': '0.85',
                'image_path': 'static/annotated_image.png'
            })
            self.assertEqual(response.status_code, 302)  # Redirect status code

            # Verify the patient data was saved
            self.assertTrue(os.path.exists(app.config['PATIENT_DATA_FILE']))
            with open(app.config['PATIENT_DATA_FILE'], 'r') as f:
                lines = f.readlines()
                self.assertIn('John', lines[0])
                self.assertIn('Doe', lines[0])
                self.assertIn('Test comment', lines[0])

    # Test No. 9
    def test_results(self):
        """
        Test viewing the results page with patient entries.
        """
        with open(app.config['PATIENT_DATA_FILE'], 'w') as f:
            f.write('1234,John,Doe,Test comment,NORMAL,0.85,flaskversion/patient_images/test_image.png\n')

        response = self.client.get('/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John', response.data)
        self.assertIn(b'Doe', response.data)
        self.assertIn(b'Test comment', response.data)

    # Test No. 10
    def test_result(self):
        """
        Test viewing a single result by patient ID.
        """
        with open(app.config['PATIENT_DATA_FILE'], 'w') as f:
            f.write('1234,John,Doe,Test comment,NORMAL,0.85,flaskversion/patient_images/test_image.png\n')

        response = self.client.get('/result/1234')
        self.assertEqual(response.status_code, 200)


    # Test No. 11
    def test_upload_invalid_file_format(self):
        """
        Test uploading a file with an invalid format.
        """
        response = self.client.post('/upload', data={'file': (BytesIO(b'invalid content'), 'test.txt')})
        self.assertIn(b'Error processing file', response.data)

    # Test No. 12
    def test_patient_images_serving(self):
        """
        Test serving patient images.
        """
        image_path = os.path.join(app.config['PATIENT_IMAGES_FOLDER'], 'test_image.png')
        os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Ensure directory exists
        with open(image_path, 'wb') as f:
            f.write(np.zeros((256, 256), dtype=np.uint8))

        response = self.client.get('/patient_images/test_image.png')
        self.assertEqual(response.status_code, 200)

    # Test No. 13
    def test_patient_data_file_creation(self):
        """
        Test if the patient data file is created if it doesn't exist.
        """
        if os.path.exists(app.config['PATIENT_DATA_FILE']):
            os.remove(app.config['PATIENT_DATA_FILE'])
        
        with self.client as c:
            with c.session_transaction() as session:
                session['image_path'] = 'static/annotated_image.png'

            response = c.post('/save_patient_info', data={
                'first_name': 'John',
                'last_name': 'Doe',
                'comments': 'Test comment',
                'label': 'NORMAL',
                'probability': '0.85',
                'image_path': 'static/annotated_image.png'
            })
            self.assertEqual(response.status_code, 302)  # Redirect status code


    # Test No. 14
    def test_missing_patient_id(self):
        """
        Test accessing a result with a missing patient ID.
        """
        response = self.client.get('/result/9999')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient not found', response.data)

    # Test No. 15
    def test_index_content(self):
        """
        Test the content of the index page.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload DICOM Image', response.data)

    # Test No. 16
    def test_about_content(self):
        """
        Test the content of the about page.
        """
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    # Test No. 17
    def test_results_content(self):
        """
        Test the content of the results page.
        """
        with open(app.config['PATIENT_DATA_FILE'], 'w') as f:
            f.write('1234,John,Doe,Test comment,NORMAL,0.85,flaskversion/patient_images/test_image.png\n')

        response = self.client.get('/results')
        self.assertEqual(response.status_code, 200)


    # Test No. 18
    def test_save_patient_info_file_saved(self):
        """
        Test that the patient's image is saved correctly.
        """
        # Ensure the annotated image exists
        self.create_dummy_image('annotated_image.png')

        with self.client as c:
            with c.session_transaction() as session:
                session['image_path'] = 'static/annotated_image.png'

            response = c.post('/save_patient_info', data={
                'first_name': 'John',
                'last_name': 'Doe',
                'comments': 'Test comment',
                'label': 'NORMAL',
                'probability': '0.85',
                'image_path': 'static/annotated_image.png'
            })
            self.assertEqual(response.status_code, 302)  # Redirect status code


    # Test No. 19
    def test_preprocess_image_values(self):
        """
        Test the preprocessing function for correct normalization.
        """
        image, dicom = preprocess_image(self.dicom_path)
        # Ensure preprocess_input is correctly applied
        # diacom is normalized +/- 3
        self.assertTrue(np.all((image >= -3.0) & (image <= 3.0)))

    # Test No. 20
    def test_classify_image_output(self):
        """
        Test the classify_image function output values.
        """
        image, _ = preprocess_image(self.dicom_path)
        model = tf.keras.models.load_model('fine_tuned_weights.h5')
        label, probability = classify_image(image, model)
        self.assertIsInstance(label, str)
        self.assertTrue(isinstance(probability, (float, np.float32, np.float64)))

if __name__ == '__main__':
    unittest.main()

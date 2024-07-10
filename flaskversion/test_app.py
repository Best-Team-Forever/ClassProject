import os
import shutil
import unittest
from io import BytesIO
from unittest.mock import Mock

import numpy as np
import pydicom
import tensorflow as tf
from callee import String
from flask_testing import TestCase
from pydicom.uid import ExplicitVRLittleEndian

from app import app, preprocess_image, classify_image, generate_ids, PATIENT_IMAGES, \
    define_image_directory  # Adjust imports as needed


def create_dummy_dicom(directory):
    dicom_path = os.path.join(directory, 'test.dcm')
    # Create a simple dummy DICOM file for testing
    file_meta = pydicom.dataset.FileMetaDataset()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds = pydicom.dataset.FileDataset(dicom_path, {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.Rows = 256
    ds.Columns = 256
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelData = np.zeros((256, 256), dtype=np.uint8).tobytes()
    ds.save_as(dicom_path)
    return dicom_path


def create_dummy_image(file_path):
    # Create a simple dummy image file for testing
    image = np.zeros((256, 256, 3), dtype=np.uint8)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
    tf.keras.preprocessing.image.save_img(file_path, image)
    return file_path


class FlaskAppTestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        app.config['STATIC_FOLDER'] = 'test_static'
        app.config['PATIENT_DATA_FILE'] = 'patient_data.txt'
        app.config['PATIENT_IMAGES_FOLDER'] = 'test_patient_images'
        app.config['SECRET_KEY'] = 'secret!'
        app.config['SESSION_TYPE'] = 'filesystem'
        return app

    def setUp(self):
        # Set up test data and environment
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['STATIC_FOLDER'])
        os.makedirs(app.config['PATIENT_IMAGES_FOLDER'])

    def tearDown(self):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
        shutil.rmtree(app.config['STATIC_FOLDER'])
        shutil.rmtree(app.config['PATIENT_IMAGES_FOLDER'])

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
        dicom_path = create_dummy_dicom(app.config['UPLOAD_FOLDER'])
        with open(dicom_path, 'rb') as dicom_file:
            response = self.client.post('/upload', data={'file': (dicom_file, 'test.dcm')})
            self.assertEqual(response.status_code, 200)

    # Test No. 6
    def test_preprocess_image(self):
        """
        Test the image preprocessing functionality.
        """
        dicom_path = create_dummy_dicom(app.config['UPLOAD_FOLDER'])
        image, dicom = preprocess_image(dicom_path)
        self.assertEqual(image.shape, (224, 224, 3))

    # Test No. 7
    def test_classify_image(self):
        """
        Test the image classification functionality.
        """
        dicom_path = create_dummy_dicom(app.config['UPLOAD_FOLDER'])
        image, _ = preprocess_image(dicom_path)
        model = tf.keras.models.load_model('fine_tuned_weights.h5')
        label, probability = classify_image(image, model)
        self.assertIn(label, ['NORMAL', 'ABNORMAL'])
        self.assertTrue(0 <= probability <= 1)
        os.remove(dicom_path)

    def test_generate_ids(self):
        image_id, patient_id = generate_ids()
        self.assertIsNotNone(image_id)
        self.assertIsNotNone(patient_id)
        self.assertNotEquals(image_id, patient_id)

    def test_define_image_directory(self):
        image_id = '10'
        expected = os.path.join(PATIENT_IMAGES, f"{image_id}.png")
        result = define_image_directory(image_id)
        self.assertEqual(expected, result)

    # Test No. 8
    def test_save_patient_info(self):
        """
        Test saving patient information after classification.
        """
        # Ensure the annotated image exists
        image_file_name = 'save_patient_information_test.png'
        image_path = create_dummy_image(os.path.join(app.config['STATIC_FOLDER'], image_file_name))
        app.database = Mock()

        with self.client as c:
            with c.session_transaction() as session:
                session['image_path'] = os.path.join('static', image_path)

            first_name = 'John'
            last_name = 'Doe'
            email = 'john@doe.com'
            comments = 'Test comment'
            label = 'NORMAL'
            probability = '0.85'

            response = c.post('/save_patient_info', data={
                'first_name': first_name,
                'last_name': last_name,
                'email' : email,
                'comments': comments,
                'label': label,
                'probability': probability,
                'image_path': image_path
            })
            self.assertEqual(response.status_code, 302)  # Redirect status code

            app.database.save_patient_record.assert_called_once_with(String(), first_name, last_name, email, comments, label,
                                                                     probability, String())

    @unittest.skip
    def test_results(self):
        """
        Test viewing the results page with patient entries.
        """

        app.database = Mock()

        patient_id = '1234'
        label = 'NORMAL'
        probability = '0.85'
        image_path = 'flaskversion/patient_images/test_image.png'
        first_name = 'John'
        last_name = 'Doe'
        email = 'john@doe.com'
        comments = 'comment'

        entries = [{'patient_id': patient_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'comments': comments,
                    'label': label,
                    'probability': probability,
                    'image_path': image_path}]

        app.database.read_all_records = Mock(return_value=[entries])

        response = self.client.get('/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(first_name, response.data)
        self.assertIn(last_name, response.data)
        self.assertIn(comments, response.data)

    @unittest.skip
    def test_result(self):
        """
        Test viewing a single result by patient ID.
        """
        with open(app.config['PATIENT_DATA_FILE'], 'w') as f:
            f.write('1234,John,Doe,john@doe.com,Test comment,NORMAL,0.85,flaskversion/patient_images/test_image.png\n')

        response = self.client.get('/result/1234')
        self.assertEqual(response.status_code, 200)

    @unittest.skip
    def test_upload_invalid_file_format(self):
        """
        Test uploading a file with an invalid format.
        """
        response = self.client.post('/upload', data={'file': (BytesIO(b'invalid content'), 'test.txt')})
        self.assertIn(b'Error processing file', response.data)

    @unittest.skip
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

    @unittest.skip
    def test_patient_data_file_creation(self):
        """
        Test if the patient data file is created if it doesn't exist.
        """
        with self.client as c:
            with c.session_transaction() as session:
                session['image_path'] = 'static/save_patient_information_test.png'

            response = c.post('/save_patient_info', data={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@doe.com',
                'comments': 'Test comment',
                'label': 'NORMAL',
                'probability': '0.85',
                'image_path': 'static/save_patient_information_test.png'
            })
            self.assertEqual(302, response.status_code)  # Redirect status code

    @unittest.skip
    def test_missing_patient_id(self):
        """
        Test accessing a result with a missing patient ID.
        """
        response = self.client.get('/result/9999')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient not found', response.data)

    @unittest.skip
    def test_index_content(self):
        """
        Test the content of the index page.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload DICOM Image', response.data)

    @unittest.skip
    def test_about_content(self):
        """
        Test the content of the about page.
        """
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    @unittest.skip
    def test_results_content(self):
        """
        Test the content of the results page.
        """
        with open(app.config['PATIENT_DATA_FILE'], 'w') as f:
            f.write('1234,John,Doe,john@doe.com,Test comment,NORMAL,0.85,flaskversion/patient_images/test_image.png\n')

        response = self.client.get('/results')
        self.assertEqual(response.status_code, 200)

    @unittest.skip
    def test_preprocess_image_values(self):
        """
        Test the preprocessing function for correct normalization.
        """
        image, dicom = preprocess_image(self.dicom_path)
        # Ensure preprocess_input is correctly applied
        # diacom is normalized +/- 3
        self.assertTrue(np.all((image >= -3.0) & (image <= 3.0)))

    @unittest.skip
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

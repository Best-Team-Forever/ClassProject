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
        return app

    def setUp(self):
        # Set up test data and environment
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        if not os.path.exists(app.config['STATIC_FOLDER']):
            os.makedirs(app.config['STATIC_FOLDER'])

        # Create a dummy DICOM file for testing
        self.dicom_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test.dcm')
        self.create_dummy_dicom(self.dicom_path)

    def tearDown(self):
        # Clean up after tests
        if os.path.exists(self.dicom_path):
            os.remove(self.dicom_path)

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

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_data(self):
        response = self.client.get('/')
        self.assertIn(b'Upload', response.data)

    def test_upload_file_no_file(self):
        response = self.client.post('/upload', data={})
        self.assertIn(b'No file part', response.data)

    def test_upload_file_no_selected_file(self):
        response = self.client.post('/upload', data={'file': (BytesIO(b''), '')})
        self.assertIn(b'No selected file', response.data)

    def test_preprocess_image(self):
        image, dicom = preprocess_image(self.dicom_path)
        self.assertEqual(image.shape, (224, 224, 3))

    def test_classify_image(self):
        image, _ = preprocess_image(self.dicom_path)
        model = tf.keras.models.load_model('fine_tuned_weights.h5')
        label, probability = classify_image(image, model)
        self.assertIn(label, ['NORMAL', 'ABNORMAL'])

    def test_classify_probability(self):
        image, _ = preprocess_image(self.dicom_path)
        model = tf.keras.models.load_model('fine_tuned_weights.h5')
        label, probability = classify_image(image, model)
        self.assertTrue(0 <= probability <= 1)

    def test_result_page_render(self):
        with self.client as client:
            client.post('/upload', data={'file': (open(self.dicom_path, 'rb'), 'test.dcm')})
            response = client.get('/result')
            self.assertEqual(response.status_code, 404)

    def test_save_comment_route(self):
        response = self.client.post('/save-comment', data={'comment': 'Test comment'})
        self.assertEqual(response.status_code, 404)  # Method Not Allowed
    
    def test_invalid_dicom_file(self):
        invalid_dicom_path = os.path.join(app.config['UPLOAD_FOLDER'], 'invalid.dcm')
        with open(invalid_dicom_path, 'w') as f:
            f.write('Invalid DICOM file content')

        response = self.client.post('/upload', data={'file': (open(invalid_dicom_path, 'rb'), 'invalid.dcm')})
        self.assertIn(b'Error processing file', response.data)

    def test_static_file_exists(self):
        # Check if the static file (annotated_image.png) exists after upload
        with self.client as client:
            client.post('/upload', data={'file': (open(self.dicom_path, 'rb'), 'test.dcm')})
            static_file_path = os.path.join(app.config['STATIC_FOLDER'], 'annotated_image.png')
            self.assertTrue(os.path.exists(static_file_path))

    def test_upload_file_success(self):
        # Test successful upload and result rendering
        with self.client as client:
            response = client.post('/upload', data={'file': (open(self.dicom_path, 'rb'), 'test.dcm')})
            self.assertEqual(response.status_code, 200)

    def test_upload_file_result(self):
        # Test successful upload and result rendering
        with self.client as client:
            response = client.post('/upload', data={'file': (open(self.dicom_path, 'rb'), 'test.dcm')})
            self.assertIn(b'Classification Result', response.data)

if __name__ == '__main__':
    unittest.main()

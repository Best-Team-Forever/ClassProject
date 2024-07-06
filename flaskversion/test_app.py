import unittest
import os
from io import BytesIO
from flask_testing import TestCase
from app import app, preprocess_image, classify_image  # Adjust import as needed
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
        self.assertTrue(0 <= probability <= 1)

if __name__ == '__main__':
    unittest.main()

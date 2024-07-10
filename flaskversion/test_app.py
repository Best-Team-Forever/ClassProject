import csv
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
from database import Database
from email_service import EmailService


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
        app.config['PATIENT_DATA_FOLDER'] = 'test_database'
        app.config['PATIENT_DATA_FILE'] = 'patient_data.txt'
        app.config['PATIENT_IMAGES_FOLDER'] = 'test_patient_images'
        app.config['SECRET_KEY'] = 'secret!'
        app.config['SESSION_TYPE'] = 'filesystem'
        return app

    def setUp(self):
        # Set up test data and environment
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['UPLOAD_FOLDER'])

        if os.path.exists(app.config['STATIC_FOLDER']):
            shutil.rmtree(app.config['STATIC_FOLDER'])
        os.makedirs(app.config['STATIC_FOLDER'])

        if os.path.exists(app.config['PATIENT_IMAGES_FOLDER']):
            shutil.rmtree(app.config['PATIENT_IMAGES_FOLDER'])
        os.makedirs(app.config['PATIENT_IMAGES_FOLDER'])

        if os.path.exists(app.config['PATIENT_DATA_FOLDER']):
            shutil.rmtree(app.config['PATIENT_DATA_FOLDER'])
        os.makedirs(app.config['PATIENT_DATA_FOLDER'])

    def tearDown(self):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
        shutil.rmtree(app.config['STATIC_FOLDER'])
        shutil.rmtree(app.config['PATIENT_IMAGES_FOLDER'])
        shutil.rmtree(app.config['PATIENT_DATA_FOLDER'])

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

    # Test No. 8
    def test_generate_ids(self):
        image_id, patient_id = generate_ids()
        self.assertIsNotNone(image_id)
        self.assertIsNotNone(patient_id)
        self.assertNotEquals(image_id, patient_id)

    # Test No. 9
    def test_define_image_directory(self):
        image_id = '10'
        expected = os.path.join(PATIENT_IMAGES, f"{image_id}.png")
        result = define_image_directory(image_id)
        self.assertEqual(expected, result)

    # Test No. 10
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
                'email': email,
                'comments': comments,
                'label': label,
                'probability': probability,
                'image_path': image_path
            })
            self.assertEqual(response.status_code, 302)  # Redirect status code

            app.database.save_patient_record.assert_called_once_with(String(), first_name, last_name, email, comments,
                                                                     label,
                                                                     probability, String())

    # Test No. 11
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

        app.database.read_all_records = Mock(return_value=entries)

        response = self.client.get('/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(first_name), response.data)
        self.assertIn(str.encode(last_name), response.data)
        self.assertIn(str.encode(comments), response.data)

    # Test No. 12
    def test_result(self):
        """
        Test viewing a single result by patient ID.
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

        app.database.read_record = Mock(
            return_value=[label, probability, image_path, first_name, last_name, comments, email])

        response = self.client.get(f'/result/{patient_id}')

        app.database.read_record.assert_called_once_with(patient_id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(first_name), response.data)
        self.assertIn(str.encode(last_name), response.data)
        self.assertIn(str.encode(comments), response.data)
        self.assertIn(str.encode(label), response.data)
        self.assertIn(str.encode(email), response.data)

    # Test No. 13
    def test_upload_invalid_file_format(self):
        """
        Test uploading a file with an invalid format.
        """
        response = self.client.post('/upload', data={'file': (BytesIO(b'invalid content'), 'test.txt')})
        self.assertIn(b'Error processing file', response.data)

    # Test No. 14
    def test_patient_data_file_creation(self):
        """
        Test if the patient data file is created if it doesn't exist.
        """
        directory = app.config['PATIENT_DATA_FOLDER']
        file_name = app.config['PATIENT_DATA_FILE']
        database = Database(directory, file_name)

        patient_id = '1234'
        label = 'NORMAL'
        probability = '0.85'
        first_name = 'John'
        last_name = 'Doe'
        email = 'john@doe.com'
        comments = 'comment'
        image_path = 'image.png'

        database.save_patient_record(patient_id, first_name, last_name, email, comments, label, probability, image_path)

        self.assertTrue(os.path.exists(os.path.join(directory, file_name)))

        with open(os.path.join(directory, file_name), mode='r') as file:
            reader = csv.reader(file)
            rows = 0
            for row in reader:
                rows += 1
                self.assertEqual(patient_id, row[0])
                self.assertEqual(first_name, row[1])
                self.assertEqual(last_name, row[2])
                self.assertEqual(email, row[3])
                self.assertEqual(comments, row[4])
                self.assertEqual(label, row[5])
                self.assertEqual(probability, row[6])
                self.assertEqual(image_path, row[7])
            self.assertEqual(1, rows)

    # Test No. 15
    def test_missing_patient_id(self):
        """
        Test accessing a result with a missing patient ID.
        """

        app.database = Mock()
        app.database.read_record = Mock()
        app.database.read_record.side_effect = Exception("Record not found")

        response = self.client.get('/result/9999')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient not found', response.data)

    # Test No. 16
    def test_index_content(self):
        """
        Test the content of the index page.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload DICOM Image', response.data)

    # Test No. 17
    def test_about_content(self):
        """
        Test the content of the about page.
        """
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    # Test No. 18
    def test_preprocess_image_values(self):
        """
        Test the preprocessing function for correct normalization.
        """
        dicom_path = create_dummy_dicom(app.config['UPLOAD_FOLDER'])
        image, dicom = preprocess_image(dicom_path)
        # Ensure preprocess_input is correctly applied
        # diacom is normalized +/- 3
        self.assertTrue(np.all((image >= -3.0) & (image <= 3.0)))

    # Test No. 19
    def test_classify_image_output(self):
        """
        Test the classify_image function output values.
        """
        dicom_path = create_dummy_dicom(app.config['UPLOAD_FOLDER'])
        image, _ = preprocess_image(dicom_path)
        model = tf.keras.models.load_model('fine_tuned_weights.h5')
        label, probability = classify_image(image, model)
        self.assertIsInstance(label, str)
        self.assertTrue(isinstance(probability, (float, np.float32, np.float64)))

    # Test No. 20
    def test_database_read_all_records(self):
        directory = app.config['PATIENT_DATA_FOLDER']
        file_name = app.config['PATIENT_DATA_FILE']

        patients = [{'patient_id': '1234',
                     'label': 'NORMAL',
                     'probability': '0.12',
                     'image_path': 'test_image.png',
                     'first_name': 'John',
                     'last_name': 'Doe',
                     'email': 'john@doe.com',
                     'comments': 'comment'},
                    {'patient_id': '2345',
                     'label': 'ABNORMAL',
                     'probability': '0.85',
                     'image_path': 'test_image_2.png',
                     'first_name': 'Harry',
                     'last_name': 'Potter',
                     'email': 'harry@potter.com',
                     'comments': 'comment second patient'}
                    ]

        data_file_path = os.path.join(directory, file_name)
        with open(data_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            for patient in patients:
                writer.writerow(
                    [patient['patient_id'], patient['first_name'], patient['last_name'], patient['email'],
                     patient['comments'], patient['label'], patient['probability'], patient['image_path']])

        database = Database(directory, file_name)

        entries = database.read_all_records()
        self.assertEqual(2, len(entries))
        self.assertEqual(patients[0]['patient_id'], entries[0]['patient_id'])
        self.assertEqual(patients[1]['patient_id'], entries[1]['patient_id'])

    # Test No. 21
    def test_database_creates_directory(self):
        directory = 'test_database_directory'
        file_name = app.config['PATIENT_DATA_FILE']

        if os.path.exists(directory):
            shutil.rmtree(directory)

        Database(directory, file_name)
        self.assertTrue(os.path.exists(directory))
        shutil.rmtree(directory)

    # Test No. 22
    def test_database_directory_cannot_be_empty(self):
        directory = ''
        file_name = app.config['PATIENT_DATA_FILE']

        try:
            Database(directory, file_name)
        except ValueError as ve:
            print(ve)
            return
        self.fail("Empty directory accepted by Database")

    # Test No. 23
    def test_database_directory_cannot_be_none(self):
        directory = None
        file_name = app.config['PATIENT_DATA_FILE']

        try:
            Database(directory, file_name)
        except ValueError as ve:
            print(ve)
            return
        self.fail("None directory accepted by Database")

    # Test No. 24
    def test_database_filename_cannot_be_empty(self):
        directory = app.config['PATIENT_DATA_FOLDER']
        file_name = ''

        try:
            Database(directory, file_name)
        except ValueError as ve:
            print(ve)
            return
        self.fail("Empty file name accepted by Database")

    # Test No. 25
    def test_database_filename_cannot_be_none(self):
        directory = app.config['PATIENT_DATA_FOLDER']
        file_name = None

        try:
            Database(directory, file_name)
        except ValueError as ve:
            print(ve)
            return
        self.fail("None file accepted by Database")

    # Test No. 26
    def test_database_read_record(self):
        directory = app.config['PATIENT_DATA_FOLDER']
        file_name = app.config['PATIENT_DATA_FILE']

        patient = {'patient_id': '1234',
                   'label': 'NORMAL',
                   'probability': '0.12',
                   'image_path': 'test_image.png',
                   'first_name': 'John',
                   'last_name': 'Doe',
                   'email': 'john@doe.com',
                   'comments': 'comment'}

        data_file_path = os.path.join(directory, file_name)
        with open(data_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                patient['patient_id'], patient['first_name'], patient['last_name'], patient['email'],
                patient['comments'], patient['label'], patient['probability'], patient['image_path']])

        database = Database(directory, file_name)
        label, probability, image_path, first_name, last_name, comments, email = database.read_record(
            patient['patient_id'])

        self.assertEqual(label, patient['label'])
        self.assertEqual(probability, patient['probability'])
        self.assertEqual(image_path, patient['image_path'])
        self.assertEqual(first_name, patient['first_name'])
        self.assertEqual(last_name, patient['last_name'])
        self.assertEqual(comments, patient['comments'])
        self.assertEqual(email, patient['email'])

    # Test No. 27
    def test_database_read_record_when_record_does_not_exist(self):
        directory = app.config['PATIENT_DATA_FOLDER']
        file_name = app.config['PATIENT_DATA_FILE']
        patient_id = '1234'

        database = Database(directory, file_name)

        try:
            database.read_record(patient_id)
        except Exception as ex:
            print(ex)
            return
        self.fail("Database returned successfully when reading non existing record")

    # Test No. 28
    def test_database_read_record_when_patient_id_is_empty(self):
        directory = app.config['PATIENT_DATA_FOLDER']
        file_name = app.config['PATIENT_DATA_FILE']
        patient_id = ''

        database = Database(directory, file_name)

        try:
            database.read_record(patient_id)
        except ValueError as ve:
            self.assertEqual('Patient ID cannot be empty', str(ve))
            print(ve)
            return
        self.fail("Database returned successfully when getting empty patient id")

    # Test No. 29
    def test_build_email_message(self):
        email_service = EmailService()

        subject = 'subject'
        sender = 'sender'
        receiver = 'receiver'
        content = 'content'

        email_message = email_service.build_message(subject, sender, receiver, content)

        self.assertEqual(subject, email_message['Subject'])
        self.assertEqual(sender, email_message['From'])
        self.assertEqual(receiver, email_message['To'])

    def test_send_email(self):

        app.database = Mock()

        patient_id = '1234'
        label = 'ABNORMAL'
        probability = '0.85'
        image_path = 'test_image.png'
        first_name = 'John'
        last_name = 'Doe'
        email = 'john@doe.com'
        comments = 'comment'

        app.database.read_record = Mock(
            return_value=[label, probability, image_path, first_name, last_name, comments, email])
        app.email_service = Mock()
        app.email_service.send_email = Mock()

        response = self.client.get(f'/send_email/{patient_id}')
        self.assertEqual(200, response.status_code)
        app.database.read_record.assert_called_once_with(patient_id)
        app.email_service.send_email.assert_called_once_with(email, float(probability))


if __name__ == '__main__':
    unittest.main()

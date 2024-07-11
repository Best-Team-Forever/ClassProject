from behave import *

from database import Database


@given("{patient_name}'s image has been uploaded")
def step_impl(context, patient_name):
    context.database = Database('behave_database', 'database.csv')


@when("A radiologist saves {patient_name}'s information")
def step_impl(context, patient_name):
    patient_information = {'patient_id': '1234',
                           'label': 'NORMAL',
                           'probability': '0.85',
                           'first_name': patient_name,
                           'last_name': 'Doe',
                           'email': 'john@doe.com',
                           'comments': 'comment',
                           'image_path': 'image.png'}

    context.patient_information = patient_information
    context.database.save_patient_record(patient_information['patient_id'], patient_information['first_name'],
                                         patient_information['last_name'], patient_information['email'],
                                         patient_information['comments'], patient_information['label'],
                                         patient_information['probability'], patient_information['image_path'])
    print(f"Save {patient_name} info")


@then("{patient_name}'s information is available in the application")
def step_impl(context, patient_name):
    label, probability, image_path, first_name, last_name, comments, email = context.database.read_record(
        context.patient_information['patient_id'])

    assert label == context.patient_information['label']
    assert probability == context.patient_information['probability']
    assert image_path == context.patient_information['image_path']
    assert first_name == context.patient_information['first_name']
    assert last_name == context.patient_information['last_name']
    assert email == context.patient_information['email']
    assert comments == context.patient_information['comments']

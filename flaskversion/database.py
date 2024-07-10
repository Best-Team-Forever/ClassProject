import csv
import os.path


class Database(object):
    def __init__(self, directory, file_name):
        self.database_path = os.path.join(directory, file_name)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_patient_record(self, patient_id, first_name, last_name, email, comments, label, probability, image_file_name):
        # Open the CSV file and append the new patient data
        print(f"CSV file path: {self.database_path}")
        with open(self.database_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([patient_id, first_name, last_name, email, comments, label, probability, image_file_name])

        print(f"Successfully saved patient info: {patient_id}, {first_name}, {last_name}, {email}")

    def read_all_records(self):
        entries = []
        print(f"CSV file path for reading: {self.database_path}")
        if os.path.exists(self.database_path):
            with open(self.database_path, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    entries.append({
                        'patient_id': row[0],
                        'first_name': row[1],
                        'last_name': row[2],
                        'email' : row[3],
                        'comments': row[4],
                        'label': row[5],
                        'probability': row[6],
                        'image_path': row[7]
                    })
        return entries

    def read_record(self, patient_id):
        print(f"CSV file path for specific patient: {self.database_path}")
        if os.path.exists(self.database_path):
            with open(self.database_path, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == patient_id:
                        # label, probability, image_path, first_name, last_name, comments, email
                        return row[5], row[6], row[7], row[1], row[2], row[4], row[3] 
        raise Exception("Record not found")

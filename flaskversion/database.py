import csv
import os.path


class Database(object):
    def __init__(self, file_path):
        self.database_path = file_path
        if not os.path.exists(file_path):
            os.makedirs(file_path)

    def save_patient_record(self, patient_id, first_name, last_name, comments, label, probability, image_file_name):
        # Open the CSV file and append the new patient data
        print(f"CSV file path: {self.database_path}")
        with open(self.database_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([patient_id, first_name, last_name, comments, label, probability, image_file_name])

        print(f"Successfully saved patient info: {patient_id}, {first_name}, {last_name}")

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
                        'comments': row[3],
                        'label': row[4],
                        'probability': row[5],
                        'image_path': row[6]
                    })
        return entries

    def read_record(self, patient_id):
        print(f"CSV file path for specific patient: {self.database_path}")
        if os.path.exists(self.database_path):
            with open(self.database_path, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == patient_id:
                        return row[4], row[5], row[6], row[1], row[2], row[3]
        raise Exception("Record not found")

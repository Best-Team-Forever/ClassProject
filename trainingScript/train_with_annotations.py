import os
import tensorflow as tf
import pandas as pd
import numpy as np
import pydicom
import cv2
import shutil
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
from tensorflow.keras.models import Model

# Set paths
base_dir = '/Users/davidrasmussen/mammoimages/physionet.org/files/vindr-mammo/1.0.0/'
images_dir = os.path.join(base_dir, 'images')
breast_annotations_file = os.path.join(base_dir, 'breast-level_annotations.csv')
finding_annotations_file = os.path.join(base_dir, 'finding_annotations.csv')
output_dir = '/Users/davidrasmussen/mammoimages/selected_images'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load annotations
breast_annotations = pd.read_csv(breast_annotations_file)
finding_annotations = pd.read_csv(finding_annotations_file)

print(f"Loaded {len(breast_annotations)} breast annotations")
print(f"Loaded {len(finding_annotations)} finding annotations")

# Preprocess function
def preprocess_image(dicom_path):
    dicom = pydicom.dcmread(dicom_path)
    image = dicom.pixel_array
    image = cv2.resize(image, (224, 224))  # Resize image to the size expected by the model
    image = np.stack((image,)*3, axis=-1)  # Convert to 3 channels
    image = image / 255.0  # Normalize the image
    return image, dicom

# Find and copy up to 10 abnormal images
def find_and_copy_abnormal_images():
    selected_count = 0  # Count the number of selected images
    for _, row in breast_annotations.iterrows():
        if selected_count >= 10:
            break
        
        study_id = row['study_id']
        image_id = row['image_id']
        image_subfolder = os.path.join(images_dir, study_id)
        
        if not os.path.exists(image_subfolder):
            print(f"Subfolder does not exist: {image_subfolder}")
            continue

        dicom_files = [f for f in os.listdir(image_subfolder) if f.endswith('.dicom')]
        if not dicom_files:
            print(f"No DICOM files found in: {image_subfolder}")
            continue

        for dicom_file in dicom_files:
            dicom_path = os.path.join(image_subfolder, dicom_file)
            try:
                bboxes_row = finding_annotations[finding_annotations['image_id'] == image_id]
                if not bboxes_row.empty:
                    if 'finding_categories' in bboxes_row.columns and not bboxes_row['finding_categories'].str.contains("No Finding").all():
                        # Copy image to output_dir if it is abnormal and we haven't reached the limit
                        output_path = os.path.join(output_dir, os.path.basename(dicom_path))
                        shutil.copy(dicom_path, output_path)
                        selected_count += 1
                        print(f"Copied {dicom_path} to {output_path}")
                        
                        if selected_count >= 10:
                            break

            except Exception as e:
                print(f"Error processing file {dicom_path}: {e}")
                continue
    print(f"Copied {selected_count} images with abnormalities to the output directory")

# Load images and labels
def load_dataset():
    images = []
    labels = []
    bboxes = []
    count = 0  # Count the number of processed images
    
    for _, row in breast_annotations.iterrows():
        study_id = row['study_id']
        image_id = row['image_id']
        image_subfolder = os.path.join(images_dir, study_id)
        
        if not os.path.exists(image_subfolder):
            print(f"Subfolder does not exist: {image_subfolder}")
            continue

        dicom_files = [f for f in os.listdir(image_subfolder) if f.endswith('.dicom')]
        if not dicom_files:
            print(f"No DICOM files found in: {image_subfolder}")
            continue

        for dicom_file in dicom_files:
            dicom_path = os.path.join(image_subfolder, dicom_file)
            try:
                image, dicom = preprocess_image(dicom_path)
                label = 0  # Default label for NORMAL
                bbox_list = []

                # Extract bounding boxes and determine abnormality from finding annotations
                bboxes_row = finding_annotations[finding_annotations['image_id'] == image_id]
                if not bboxes_row.empty:
                    if 'finding_categories' in bboxes_row.columns and not bboxes_row['finding_categories'].str.contains("No Finding").all():
                        label = 1  # Label 1 for ABNORMAL

                    for _, bbox in bboxes_row.iterrows():
                        if not pd.isnull(bbox['xmin']) and not pd.isnull(bbox['ymin']) and not pd.isnull(bbox['xmax']) and not pd.isnull(bbox['ymax']):
                            xmin, ymin, xmax, ymax = int(bbox['xmin']), int(bbox['ymin']), int(bbox['xmax']), int(bbox['ymax'])
                            bbox_list.append([xmin, ymin, xmax, ymax])
                
                images.append(image)
                labels.append(label)
                bboxes.append(bbox_list)
                count += 1

                print(f"Processed file {dicom_path}: label={label}, bounding_boxes={bbox_list}")
            except Exception as e:
                print(f"Error processing file {dicom_path}: {e}")
                continue

    print(f"Processed {count} images")
    return np.array(images), np.array(labels), bboxes

# Find and copy abnormal images
find_and_copy_abnormal_images()

# Load and split dataset
images, labels, bboxes = load_dataset()
print(f"Loaded {len(images)} images, {len(labels)} labels")

x_train, x_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42)
print(f"Training set size: {len(x_train)}")
print(f"Validation set size: {len(x_val)}")

# Create data generators
train_datagen = ImageDataGenerator(horizontal_flip=True, vertical_flip=True)
val_datagen = ImageDataGenerator()

train_generator = train_datagen.flow(x_train, y_train, batch_size=32)
val_generator = val_datagen.flow(x_val, y_val, batch_size=32)

# Build the model
base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
predictions = Dense(1, activation='sigmoid')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# Freeze the base model
for layer in base_model.layers:
    layer.trainable = False

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
print("Starting training...")
model.fit(train_generator, validation_data=val_generator, epochs=10)

# Unfreeze some layers of the base model for fine-tuning
for layer in base_model.layers[-50:]:
    layer.trainable = True

# Recompile the model with a lower learning rate
model.compile(optimizer=tf.keras.optimizers.Adam(1e-5), loss='binary_crossentropy', metrics=['accuracy'])

# Continue training the model
print("Continuing training with fine-tuning...")
model.fit(train_generator, validation_data=val_generator, epochs=10)

# Save the fine-tuned model
model.save('fine_tuned_weights.h5')
print("Model training complete and saved.")

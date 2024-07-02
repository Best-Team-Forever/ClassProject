import tensorflow as tf
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Load the DenseNet121 model pretrained on ImageNet
base_model = DenseNet121(weights='imagenet', include_top=False)

# Add global average pooling layer
x = base_model.output
x = GlobalAveragePooling2D()(x)

# Add a fully connected layer and a sigmoid output layer
predictions = Dense(1, activation='sigmoid')(x)

# Define the model
model = Model(inputs=base_model.input, outputs=predictions)

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Prepare the dataset
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

validation_datagen = ImageDataGenerator(
    rescale=1./255
)

train_generator = train_datagen.flow_from_directory(
    'dataset/train',
    target_size=(224, 224),
    batch_size=16,  # Reduced batch size for quicker training
    class_mode='binary',
    shuffle=True
)

validation_generator = validation_datagen.flow_from_directory(
    'dataset/validation',
    target_size=(224, 224),
    batch_size=16,  # Reduced batch size for quicker training
    class_mode='binary',
    shuffle=True
)

# Train the model
model.fit(
    train_generator,
    steps_per_epoch=50,  # Limited steps for initial testing
    validation_data=validation_generator,
    validation_steps=25,  # Limited steps for initial testing
    epochs=3  # Reduced epochs for quick feedback
)

# Save the model to a file
model.save('breast_cancer_model.h5')
print('Model saved successfully.')

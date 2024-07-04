import sys


# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.preprocessing import image

# Load the saved model
# model = tf.keras.models.load_model('/data/model/breast_cancer_model.h5')


# Function to predict cancer from a single image
def predict_cancer(img_path):
    #    img = image.load_img(img_path, target_size=(224, 224))
    #    img_array = image.img_to_array(img)
    #    img_array = np.expand_dims(img_array, axis=0)
    #    img_array /= 255.

    #    prediction = model.predict(img_array)
    #    return prediction[0][0]
    return 0.067


if __name__ == '__main__':
    print(predict_cancer("image"))

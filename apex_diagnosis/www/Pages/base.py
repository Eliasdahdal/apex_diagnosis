from __future__ import unicode_literals
import frappe
from frappe import _
import os
import numpy as np
import tensorflow as tf
from keras.models import load_model
from keras.models import model_from_json
from PIL import Image

@frappe.whitelist(allow_guest=True)
# Load the model and preprocessing functions
def load_my_model():
    # Load the model architecture from JSON
    json_file = open('/home/elias/Apex-Diagnosis/apps/apex_diagnosis/model1.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    # Load the model weights
    loaded_model.load_weights('/home/elias/Apex-Diagnosis/apps/apex_diagnosis/model1.h5')

    # Compile the model
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return loaded_model

loaded_model = load_my_model()

# Load the VGG16 model with the top classification layers
base_model_VGG16 = tf.keras.applications.VGG16(
    weights='imagenet',
    include_top=False,
    input_shape=(299, 299, 3)
)


@frappe.whitelist(allow_guest=True)
# Function to preprocess an image
def preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.resize((299, 299))  # Resize the image to (299, 299)
    img = img.convert('RGB')  # Ensure the image has 3 color channels (RGB)
    img = np.array(img)
    img = img / 255.0  # Normalize pixel values to the range [0, 1]
    img = np.expand_dims(img, axis=0)
    img = tf.convert_to_tensor(img, dtype=tf.float32)  # Convert to a TensorFlow tensor
    return img


@frappe.whitelist(allow_guest=True)
# Function to make predictions
def predict_image(img):
    prediction = loaded_model.predict(img)
    class_indices = np.argmax(prediction, axis=1)  # Extract class indices
    return class_indices

@frappe.whitelist(allow_guest=True)
def sanitize_filename(filename):
    # You can customize this function to sanitize the filename as needed
    # For simplicity, this example replaces spaces with underscores
    return filename.replace(' ', '_')

@frappe.whitelist(allow_guest=True)
def index():
    messages = []
    class_percentages_list = []
    image_paths = []

    files = frappe.request.files.getlist("files[]")

    for file in files:
        if file.filename == "":
            messages.append({"message": "No selected file"})
            continue

        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            messages.append({"message": "File type not allowed"})
            continue

        filename = sanitize_filename(file.filename)
        file_path = os.path.join("/home/elias/Apex-Diagnosis/apps/apex_diagnosis/apex_diagnosis/public/img", filename.replace('\\', '/'))
        file_path = file_path.replace('\\', '/')

        print(f"Sanitized Filename: {filename}")
        print(f"File Path: {file_path}")

        file.save(file_path)
        image_paths.append(file_path)

        img = preprocess_image(file_path)
        class_indices = predict_image(img)

        class_names = ["NORMAL", "PNEUMONIA"]
        class_probabilities = loaded_model.predict(img)
        class_percentages = {class_names[i]: round(100 * class_probabilities[0][i], 2) for i in range(len(class_names))}
        class_percentages_list.append(class_percentages)

        messages.append({
            "message": f"Uploaded file: {filename}",
            "class_percentage": class_percentages,
            "image_path": file_path
        })
        
        print(messages)

    return messages

def get_context(context):

    # context.patient = frappe.db.get_all('Patient')
    # print(context.patient)
    context.csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    
    return context


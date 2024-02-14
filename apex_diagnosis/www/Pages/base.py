from __future__ import unicode_literals
import frappe
from frappe import _
import os
import numpy as np
import tensorflow as tf
from keras.models import load_model
from keras.models import model_from_json
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))
model_json_name = "/model1.json"
model_h5_name = "/model1.h5"

model_json_path = current_dir + model_json_name
model_h5_path = current_dir + model_h5_name

# print(os.path.abspath(os.path.join(current_dir, '..')) + "5555555555555555555555555555555555555555555555555555")


@frappe.whitelist(allow_guest=True)
# Load the model and preprocessing functions
def load_my_model():
    # Load the model architecture from JSON

    json_file = open(model_json_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    # Load the model weights
    loaded_model.load_weights(model_h5_path)

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
    first_name = frappe.request.form.get("first_name")
    last_name = frappe.request.form.get("last_name")
    governorate = frappe.request.form.get("governorate")
    latitude  = frappe.request.form.get("latitude")
    longitude = frappe.request.form.get("longitude")
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

        image_path = file_path.replace('/home/elias/Apex-Diagnosis/apps/apex_diagnosis/apex_diagnosis/public/', '/assets/apex_diagnosis/')
        todo = frappe.get_doc({"doctype":"apex patient",
                               "first_name": first_name,
                               "last_name": last_name,
                               "governorate_name":governorate,
                               "latitude":latitude,
                               "longitude":longitude,
                               "chest_image":image_path,})
        todo.insert(ignore_permissions = True)
        
        print(messages)

    return messages

def get_context(context):

    
    context.apex_patient = frappe.db.get_all('apex patient',fields=["latitude","longitude"])
    context.csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    
    return context


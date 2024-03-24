from __future__ import unicode_literals
import frappe
from frappe import _
import os
import numpy as np
import tensorflow as tf
from keras.models import load_model
from keras.models import model_from_json
from PIL import Image
import requests
import json
import skimage
import torch
import torchvision
import torchxrayvision as xrv
import io
import base64
import matplotlib.pyplot as plt



current_dir = os.path.dirname(os.path.abspath(__file__))
model_json_name = "/model1.json"
model_h5_name = "/model1.h5"


model_json_path = current_dir + model_json_name
model_h5_path = current_dir + model_h5_name

@frappe.whitelist(allow_guest=True)
# Assuming segmentation_model_path contains the path to your model file
def load_segmentation_model():
    # Load the model
    model = xrv.baseline_models.chestx_det.PSPNet()
    # Ensure the model is in evaluation mode
    model.eval()
    return model


@frappe.whitelist(allow_guest=True)
def image_segmentation(img_path, name):
    img = skimage.io.imread(img_path)
    img = xrv.datasets.normalize(img, 255)  # convert 8-bit image to [-1024, 1024] range
    segmentation_model = load_segmentation_model()
    # Assuming img has 3 color channels (RGB)
    if len(img.shape) == 3:
        img = img.mean(2)[None, ...]  # Convert to single color channel
    else:
        # Handle grayscale images or other cases
        img = img[None, ...]

    transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(), xrv.datasets.XRayResizer(512)])
    img = transform(img)
    img = torch.from_numpy(img)
    with torch.no_grad():
        pred = segmentation_model(img)

    # Define the path where you want to save the image
    plt.figure(figsize=(26, 5))
    plt.subplot(1, len(segmentation_model.targets) + 1, 1)
    plt.imshow(img[0], cmap='gray')
    for i in range(len(segmentation_model.targets)):
        plt.subplot(1, len(segmentation_model.targets) + 1, i + 2)
        plt.imshow(pred[0, i])
        plt.title(segmentation_model.targets[i])
        plt.axis('off')
    plt.tight_layout()
    
    # Define the directory where you want to save the image
    save_dir = "/home/elias/Apex-Diagnosis/apps/apex_diagnosis/apex_diagnosis/public/img"
    # Concatenate the name with the file extension
    save_path = os.path.join(save_dir, name)

    # Save the figure as a PNG file with the specified name
    plt.savefig(save_path)
    # Close the plot to free up memory
    plt.close()

@frappe.whitelist(allow_guest=True)
def image_segmentation_index():
    messages = []
    image_paths = []
    files = frappe.request.files.getlist("segma_files[]")
    
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
        
        segmentation_result=image_segmentation(file_path,file.filename)
        
        messages.append({
            "message": f"{filename}",
            "image_path": file_path,
        })
        
    return messages

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


def sent_to_llm(message):
    url = 'https://www.chatbase.co/api/v1/chat'
    headers = {
        'Authorization': 'Bearer c709d9c5-706f-42e3-951f-a0fcd53e2c32',
        'Content-Type': 'application/json'
    }
    data = {
        "messages": [
            {"content": "كيف يمكنني مساعدتك?", "role": "assistant"},
            {"content": message, "role": "user"}
        ],
        "chatbotId": "UV_rVP0e9dhD-U-wqHoQT",
        "stream": False,
        "temperature": 0.4
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status() 
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None


@frappe.whitelist(allow_guest=True)
def index():
    messages = []
    class_percentages_list = []
    image_paths = []
    diagnosis_list =[]
    first_name = frappe.request.form.get("first_name")
    last_name = frappe.request.form.get("last_name")
    symptoms =  frappe.request.form.get("symptoms")
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
    
        
        # symptoms_with_images = "after upload my chest x-ray image the result is normal percentage = " + str(class_percentages["NORMAL"]) + " and pneumonia percentage = " + str(class_percentages["PNEUMONIA"]) + " and my is " + symptoms
        # diagnosis = sent_to_llm(symptoms_with_images)
        # diagnosis_list.append(diagnosis['text'])
        # diagnosis_list.append("Lorem ipsum dolor sit amet consectetur adipisicing elit. In consequatur autem eum maxime laborum voluptate deserunt enim veniam, ea, vitae ab at nam facere rerum eligendi sint voluptatem iste? Quia?")

        symptoms_with_images = "بعد أن قمت برفع الصورة الشعاعية الصدرية كانت النتيجة الطبيعة بنسبة مئوية   = " + str(class_percentages["NORMAL"]) + " وبنسبة مئوية اني مصاب  = " + str(class_percentages["PNEUMONIA"]) + " وأعراضي هي " + symptoms + "قم بنصيحتي ماهي اختصاصات الأطباء الذي يجب أن اقوم بزيارتهم لكي ينصحوني بالعلاج بلاضافة للادوية و التحاليلة التي تتوقعها "
        diagnosis = sent_to_llm(symptoms_with_images)
        diagnosis_list.append(diagnosis['text'])



        messages.append({
            "message": f"Uploaded file: {filename}",
            "class_percentage": class_percentages,
            "image_path": file_path,
            "diagnosis": diagnosis['text'],
        })
        
    todos = []
    


    for message in messages:
        normal_percentage = message['class_percentage']['NORMAL']  
        pneumonia_percentage = message['class_percentage']['PNEUMONIA']
        # Adjusting the image path
        image_path = message['image_path'].replace('/home/elias/Apex-Diagnosis/apps/apex_diagnosis/apex_diagnosis/public/', '/assets/apex_diagnosis/')
        # Storing relevant information in a dictionary
        todo_info = {
            "first_name": first_name,
            "last_name": last_name,
            "governorate_name": governorate,
            "patient_symptoms": symptoms,
            "pathological_diagnosis":message['diagnosis'],
            "latitude": latitude,
            "longitude": longitude,
            "normal_percentage": normal_percentage,
            "pneumonia_percentage": pneumonia_percentage,
            "chest_image": image_path,
        }

        # Appending the dictionary to the list
        todos.append(todo_info)

    # Inserting todos outside the loop
    for todo_info in todos:
        todo = frappe.get_doc({
            "doctype": "apex patient",
            **todo_info  # Unpacking the todo_info dictionary
        })
        todo.insert(ignore_permissions=True)
        
        print(messages)

    return messages

def get_context(context):

    
    context.apex_patient = frappe.db.get_all('apex patient',fields=["latitude","longitude"])
    context.csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    
    return context


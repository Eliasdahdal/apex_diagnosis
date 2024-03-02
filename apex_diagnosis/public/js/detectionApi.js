var predict_image = function (formData, csrf) {
    return new Promise(function (resolve, reject) {
        var settings = {
            "url": "/api/method/apex_diagnosis.www.Pages.base.index",
            "method": "POST",
            "timeout": 0,
            "data": formData,
            "contentType": false,
            "processData": false,
            "beforeSend": function (xhr) {
                xhr.setRequestHeader('X-Frappe-CSRF-Token', csrf);
            }
        };

        $.ajax(settings).done(function (response) {
            resolve({
                success: true,
                response: response
            });
        }).fail(function (jqXHR, textStatus, errorThrown) {
            reject({
                success: false,
                message: jqXHR.responseText
            });
        });
    });
}
var detectionResultDiv = document.querySelector('.detection-result');
console.log(detectionResultDiv)

// Function to create and append elements to the body
function createImageElement(message, parentElement) {
    var container = document.createElement('div');
    container.className = 'image-container';

    var image = document.createElement('img');
    image.className = 'chest-image';
    var imagePath = message.image_path.replace(/.*\/public\//, '/assets/apex_diagnosis/');
    image.src = imagePath;
    image.alt = 'Uploaded Image';
    
    var percentages = document.createElement('div');
    percentages.className = 'class-percentages';
    percentages.textContent = `NORMAL: ${message.class_percentage.NORMAL.toFixed(2)}%, PNEUMONIA: ${message.class_percentage.PNEUMONIA.toFixed(2)}%`;

    container.appendChild(image);
    container.appendChild(document.createElement('br'));
    container.appendChild(percentages);

    // Append the image-container to the specified parentElement
    parentElement.appendChild(container);
}


    //for validation
    // Get the form and its input fields
    var form = document.querySelector('.main-form');
    var inputs = form.querySelectorAll('input[type=text]');

    // Reset the form and clear the input fields
    function resetForm() {
    form.reset();
    inputs.forEach(function(input) {
        input.value = '';
    });
    }

    // Function to validate the form
    function validateForm() {

        var first_name = document.getElementById("first_name").value;
        var last_name = document.getElementById("last_name").value;
        var governorate = document.querySelector('select[name="governorate"]').value;
        var files = document.getElementById('uploadFile').files;
        var isValid = true;

        // Check first name is not empty
        if (first_name === "") {
            document.getElementById("first_name-error").innerHTML = "Please enter your first name";
            isValid = false;
        } else {
            document.getElementById("first_name-error").innerHTML = "";
        }

        // Check last name is not empty
        if (last_name === "") {
            document.getElementById("last_name-error").innerHTML = "Please enter your last name";
            isValid = false;
        } else {
            document.getElementById("last_name-error").innerHTML = "";
        }

        // Check governorate name is not empty
        if (governorate === "Choose your governorate") {
            document.getElementById("governorate-error").innerHTML = "Please choose your governorate ";
            isValid = false;
        }else {
            document.getElementById("governorate-error").innerHTML = "";
        }

        // Validate file upload
        if (files.length === 0) {
            document.getElementById("image-upload-error").innerHTML = "Please select at least one file";
            isValid = false;
        }else {
            document.getElementById("image-upload-error").innerHTML = "";
        }

        return isValid;
    }

    document.getElementById("submit").addEventListener("click", function (event) {
        event.preventDefault();
        if (validateForm()) {
            var formData = new FormData(document.getElementById("image-upload-form"));
            
            // Show loading overlay
            document.querySelector('.loading-overlay').style.display = 'block';
    
            predict_image(formData, csrf_token)
                .then(function (result) {
                    if (result.success) {
                        var detectionResult = result.response.message;
                        detectionResult.forEach(function(message) {
                            createImageElement(message, detectionResultDiv);
                        });
                    } else {
                        // Show error message
                        alert(result.message);
                    }
                })
                .catch(function (error) {
                    // Show error message
                    alert(error.message);
                })
                .finally(function () {
                    // Hide loading overlay regardless of success or failure
                    document.querySelector('.loading-overlay').style.display = 'none';
                });
        }
    });
    


// Drop and Drag Area

"use strict";
function dragNdrop(event) {
    var files = event.target.files;
    var preview = document.getElementById("preview");
    preview.innerHTML = ""; // Clear previous previews

    for (var i = 0; i < files.length; i++) {
        var fileName = URL.createObjectURL(files[i]);
        var previewImg = document.createElement("img");
        previewImg.setAttribute("src", fileName);
        preview.appendChild(previewImg);
    }
}

function drag() {
    document.getElementById('uploadFile').parentNode.className = 'draging dragBox';
}
function drop() {
    document.getElementById('uploadFile').parentNode.className = 'dragBox';
}



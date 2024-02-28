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


document.getElementById("submit").addEventListener("click", function (event) {
    event.preventDefault();

    var formData = new FormData(document.getElementById("image-upload-form"));

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
        });
});




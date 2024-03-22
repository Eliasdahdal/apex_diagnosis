//segmentation api
var segmentation_image = function (formData, csrf) {
    return new Promise(function (resolve, reject) {
        var settings = {
            "url": "/api/method/apex_diagnosis.www.Pages.base.image_segmentation_index",
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


// Function to validate the form
function validateSegmentationForm() {
    var files = document.getElementById('segmaUploadFile').files;
    var isValid = true;
    
    // Validate file upload
    if (files.length === 0) {
        document.getElementById("image-upload-error").innerHTML = "Please select image";
        isValid = false;
    }else {
        document.getElementById("image-upload-error").innerHTML = "";
    }
    return isValid;
}


document.getElementById("segmentation_submit").addEventListener("click", function (event) {
    event.preventDefault();
    if (validateSegmentationForm()) {
        var formData = new FormData(document.getElementById("image-segmentation-form"));

        // Show loading overlay
        document.querySelector('.loading-overlay').style.display = 'block';

        segmentation_image(formData, csrf_token)
            .then(function (result) {
                if (result.success) {
                    // Extract image path from the response
                    var imagePath = result.response.message[0].image_path;
                    
                    // Construct full image URL
                    var imageUrl = '/assets/apex_diagnosis/img/' + imagePath.split('/').pop();

                    // Set the image source
                    document.getElementById('segmentationImage').src = imageUrl;
                } else {
                    // Show error message
                    alert(result.response.message);
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

// document.addEventListener("DOMContentLoaded", function () {
//     const dropArea = document.getElementById("drop-area");
//     const fileInput = document.getElementById("fileInput");
//     const previewContainer = document.getElementById("preview-container");
//     const dropText = document.getElementById("drop-text");

//     // Handle click to open file dialog
//     dropArea.addEventListener("click", () => fileInput.click());

//     // Handle file selection
//     fileInput.addEventListener("change", handleFiles);

//     // Drag & Drop events
//     dropArea.addEventListener("dragover", (e) => {
//         e.preventDefault();
//         dropArea.style.borderColor = "#007bff";
//     });

//     dropArea.addEventListener("dragleave", () => {
//         dropArea.style.borderColor = "#ddd";
//     });

//     dropArea.addEventListener("drop", (e) => {
//         e.preventDefault();
//         dropArea.style.borderColor = "#ddd";
//         fileInput.files = e.dataTransfer.files;
//         handleFiles();
//     });

//     function handleFiles() {
//         previewContainer.innerHTML = ""; // Clear previous previews
//         previewContainer.style.minHeight = "250px";
//         const files = fileInput.files;

//         if (files.length === 0) {
//             dropText.style.display = "block";
//             return;
//         }

//         dropText.style.display = "none";

//         Array.from(files).forEach((file) => {
//             const fileType = file.type.split("/")[0];

//             if (fileType === "image" || fileType === "video") {
//                 const reader = new FileReader();
//                 reader.onload = function (e) {
//                     const preview = document.createElement(fileType === "image" ? "img" : "video");
//                     preview.src = e.target.result;
//                     preview.style.cssText = `
//                         width: 100%;
//                         height: 100%;
//                         object-fit: contain;
//                         display: block;
//                         opacity: 1;
//                     `;
//                     // Add video controls if it's a video
//                     if (fileType === "video") {
//                         preview.controls = true;
//                     }
//                     previewContainer.appendChild(preview);
//                 };
//                 reader.readAsDataURL(file);
//             }
//         });
//     }
    
// });
// function updatePreview(clickedImage) {
    
//     var mainImage = document.getElementById("main-preview");
//     // Change the main image source to the clicked thumbnail
//     mainImage.src = clickedImage.src;
// }


document.addEventListener("DOMContentLoaded", function () {
    /*** File Upload (Image/Video) ***/
    const dropArea = document.getElementById("drop-area");
    const fileInput = document.getElementById("fileInput");
    const previewContainer = document.getElementById("preview-container");
    const dropText = document.getElementById("drop-text");

    if (dropArea) {
        // Click to open file dialog
        dropArea.addEventListener("click", () => fileInput.click());

        // Handle file selection
        fileInput.addEventListener("change", handleFiles);

        // Drag & Drop events
        dropArea.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropArea.style.borderColor = "#007bff";
        });

        dropArea.addEventListener("dragleave", () => {
            dropArea.style.borderColor = "#ddd";
        });

        dropArea.addEventListener("drop", (e) => {
            e.preventDefault();
            dropArea.style.borderColor = "#ddd";
            fileInput.files = e.dataTransfer.files;
            handleFiles();
        });
    }

    function handleFiles() {
        previewContainer.innerHTML = ""; // Clear previous previews
        previewContainer.style.minHeight = "250px";
        const files = fileInput.files;

        if (files.length === 0) {
            dropText.style.display = "block";
            return;
        }

        dropText.style.display = "none";

        Array.from(files).forEach((file) => {
            const fileType = file.type.split("/")[0];

            if (fileType === "image" || fileType === "video") {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const preview = document.createElement(fileType === "image" ? "img" : "video");
                    preview.src = e.target.result;
                    preview.style.cssText = `
                        width: 100%;
                        height: 100%;
                        object-fit: contain;
                        display: block;
                        opacity: 1;
                    `;
                    // Add video controls if it's a video
                    if (fileType === "video") {
                        preview.controls = true;
                    }
                    previewContainer.appendChild(preview);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    /*** Grad-CAM Preview (For AI Predictions) ***/
    const thumbnails = document.querySelectorAll(".grad-cam-thumbnail");
    const mainImage = document.getElementById("main-preview");

    if (thumbnails.length > 0 && mainImage) {
        // Set first thumbnail as default preview
        updatePreview(thumbnails[0]);
    }

    thumbnails.forEach((thumbnail) => {
        thumbnail.addEventListener("click", function () {
            updatePreview(thumbnail);
        });
    });

    function updatePreview(clickedImage) {
        if (mainImage) {
            mainImage.src = clickedImage.src;
        }
    }
});

const video = document.getElementById("history-video");

function showControls() {
    video.setAttribute("controls", "controls");
  }

function hideControls() {
    video.removeAttribute("controls");
  }
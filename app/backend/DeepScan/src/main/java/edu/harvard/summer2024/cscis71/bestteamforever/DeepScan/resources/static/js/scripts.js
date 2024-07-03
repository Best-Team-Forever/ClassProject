// src/main/resources/static/js/scripts.js
document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    form.addEventListener("submit", function(event) {
        const fileInput = document.querySelector("input[type='file']");
        if (fileInput.files.length === 0) {
            alert("Please select a file to upload.");
            event.preventDefault();
        }
    });
});

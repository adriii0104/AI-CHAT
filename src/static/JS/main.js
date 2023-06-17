document.addEventListener('DOMContentLoaded', function() {
    var audioFileInput = document.getElementById('audioFileInput');
    var uploadButton = document.getElementById('uploadButton');

    uploadButton.addEventListener('click', function() {
        var file = audioFileInput.files[0];
        var formData = new FormData();
        formData.append('audio', file);

        fetch('/voiceclone', {
            method: 'POST',
            body: formData
        })
        .then(function(response) {
            return response.text();
        })
        .then(function(result) {
            console.log(result);
        });
    });
});
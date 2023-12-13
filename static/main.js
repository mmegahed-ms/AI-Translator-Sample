$(function() {
  // Radio button change event handler
  $('input[type=radio][name=translationType]').change(function() {
      if (this.value == 'text') {
          $('#text-translation-form').show();
          $('#document-translation-form').hide();
      } else if (this.value == 'document') {
          $('#text-translation-form').hide();
          $('#document-translation-form').show();
      }
  });


  $("#translate-document").on("click", function(e) {
    e.preventDefault();
    var languageVal = document.getElementById("select-to-language-document").value;
    var languagefrom = document.getElementById("select-from-language-document").value;
    var formData = new FormData();
    var file = document.getElementById("document").files[0];
      // Check if a file has been selected
  if (!file) {
    alert("Please select a file before translating.");
    return;
  }
    formData.append("file", file);
    formData.append("to", languageVal);
    formData.append("from", languagefrom);
    var translateButton = this;

    // Check if it's a download button
    var isDownloadButton = translateButton.classList.contains("download-button");

    if (!isDownloadButton) {
      // If not a download button, perform translation
      translateButton.textContent = "Translating...";
      document.getElementById("progress-bar").style.display = "block"; // Show the progress bar
      
      $.ajax({
        url: '/translate-document',
        method: 'POST',
        processData: false,
        contentType: false,
        data: formData,
        xhrFields: {
            responseType: 'blob' // Ensure that the data is treated as a Blob
          },
        success: function(data, status, xhr) {
          var blob = new Blob([data], { type: xhr.getResponseHeader('Content-Type') });
          var url = window.URL.createObjectURL(blob);
          translateButton.textContent = "Download translation";
          translateButton.classList.add("download-button"); // Add a class to identify it as a download button
          document.getElementById("progress-bar").style.display = "none"; // Hide the progress bar
          translateButton.onclick = function(e) {
            e.preventDefault();
            var link = document.createElement('a');
            link.href = url;
            link.download = xhr.getResponseHeader('X-Downloaded-File-Name');
            link.click();
          };
          var translationStatus = xhr.getResponseHeader('X-Translation-Status');
          document.getElementById("translation-status").textContent = translationStatus;
          document.getElementById("translation-status").style.display = "block";
        },
        error: function(jqXHR, textStatus, errorThrown) {
          // Display an error message
          document.getElementById("translation-status").textContent = "Translation failed";
          document.getElementById("translation-status").style.display = "block";
          document.getElementById("progress-bar").style.display = "none"; // Hide the progress bar
        }

      });
    } else {
      // If it's already a download button, do nothing or handle additional logic as needed
    }
  });

  //  reset the button when a new file is selected
  document.getElementById("document").addEventListener("change", function() {
    var translateButton = document.getElementById("translate-document");
    translateButton.textContent = "Translate document";
    translateButton.classList.remove("download-button");
    translateButton.onclick = null; // Remove the click event handler
    // hide translation status
    document.getElementById("translation-status").style.display = "none";
          // When a new file is selected, hide the progress bar and reset its width
    document.getElementById("progress-bar").style.display = "none"; // Hide the progress bar

  });
  document.getElementById("select-to-language-document").addEventListener("change", function() {
    var translateButton = document.getElementById("translate-document");
    translateButton.textContent = "Translate document";
    translateButton.classList.remove("download-button");
    translateButton.onclick = null; // Remove the click event handler
    // hide translation status
    document.getElementById("translation-status").style.display = "none";
    // When a new language is selected, hide the progress bar and reset its width
    document.getElementById("progress-bar").style.display = "none"; // Hide the progress bar
  });
  // Translate text with flask route
  $("#translate").on("click", function(e) {
      e.preventDefault();
      var translateVal = document.getElementById("text-to-translate").value;
      var languageVal = document.getElementById("select-language").value;
      var languagefrom = document.getElementById("select-from-language").value;
      var translateRequest = {
          'text': translateVal,
          'to': languageVal,
          'from': languagefrom
      }

      if (translateVal !== "") {
          $.ajax({
              url: '/translate-text',
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              dataType: 'json',
              data: JSON.stringify(translateRequest),
              success: function(data) {
                  for (var i = 0; i < data.length; i++) {
                      document.getElementById("translation-result").textContent = data[i].translations[0].text;
                      document.getElementById("detected-language-result").textContent = data[i].detectedLanguage.language;
                      if (document.getElementById("detected-language-result").textContent !== "") {
                          document.getElementById("detected-language").style.display = "block";
                      }
                      document.getElementById("confidence").textContent = data[i].detectedLanguage.score;
                  }
              }
          });
      }
  });
});

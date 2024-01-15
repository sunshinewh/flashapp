function showMeaning() {
  var x = document.getElementById("meaning");
  var y = document.getElementById("meaning_hidden");
  var z = document.getElementById("show_hide");
  if (x.style.display === "none") {
    x.style.display = "block";
    y.style.display = "none";
    z.innerHTML = "H I D E";
  } else {
    x.style.display = "none";
    y.style.display = "block";
    z.innerHTML = "S H O W";
  }
}

document.getElementById('speakButton').addEventListener('click', function() {
  var text = document.getElementById('textToSpeak').innerText;
  fetchTTS(text);
});

function fetchTTS(text) {
  // Example using a generic TTS API
  fetch('TTS_API_ENDPOINT', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_API_KEY'
      },
      body: JSON.stringify({
          text: text,
          lang: 'fr-FR'  // French language
      })
  })
  .then(response => response.blob())
  .then(blob => {
      var audio = new Audio(URL.createObjectURL(blob));
      audio.play();
  })
  .catch(error => console.error('Error:', error));
}

document.getElementById('correct_button').addEventListener('click', function() {
  var xhr = new XMLHttpRequest();
  var word = "{{ card.word }}"; // Get the current word
  var deckName = "{{ card.deck }}"; // Get the deck name
  var nextUrl = this.getAttribute('data-next-url'); // Get the next URL from the button

  xhr.open("POST", "/log_correct_click", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function () {
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
          // Redirect after logging the click
          window.location.href = nextUrl;
      }
  }
  xhr.send(JSON.stringify({word: word, deck: deckName}));
});

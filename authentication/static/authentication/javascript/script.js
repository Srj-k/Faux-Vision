import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyA21hPsndPm1DQz5dYuKZW89xb0ixkfeW4",
    authDomain: "faux-vision-a1f13.firebaseapp.com",
    projectId: "faux-vision-a1f13",
    storageBucket: "faux-vision-a1f13.firebasestorage.app",
    messagingSenderId: "62644276493",
    appId: "1:62644276493:web:178a47f7fce6744c997444"
  };

  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);

  function googleLogin() {
      let provider = new firebase.auth.GoogleAuthProvider();
      firebase.auth().signInWithPopup(provider)
      .then((result) => {
          result.user.getIdToken().then((idToken) => {
              fetch("", {
                  method: "POST",
                  headers: {
                      "Content-Type": "application/json",
                      "X-CSRFToken": "{{ csrf_token }}"
                  },
                  body: JSON.stringify({ idToken: idToken, google_login: true })
              }).then(response => response.json())
              .then(data => {
                  if (data.status === "success") {
                      window.location.href = "/prediction/";  // Redirect to prediction page
                  } else {
                      alert("Google login failed: " + data.message);
                  }
              });
          });
      })
      .catch(error => {
          console.error(error);
          alert("Google Sign-In failed");
      });
  }
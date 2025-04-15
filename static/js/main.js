// document.addEventListener("DOMContentLoaded", function () {
//     const micButton = document.getElementById("micButton");
//     const responseBox = document.getElementById("responseBox");
  
//     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
//     const recognition = new SpeechRecognition();
//     recognition.interimResults = false;
//     recognition.lang = 'en-US';
  
//     micButton.addEventListener("click", () => {
//       recognition.start();
//       micButton.classList.add("listening");
//       responseBox.innerHTML = "Listening...";
//     });
  
//     recognition.addEventListener("result", async (event) => {
//       const transcript = Array.from(event.results)
//         .map(result => result[0].transcript)
//         .join("");
  
//       responseBox.innerHTML = `Heard: "${transcript}"`;
  
//       // Send transcript to backend for AI classification
//       const response = await fetch("/process_speech", {
//         method: "POST",
//         body: JSON.stringify({ transcript }),
//         headers: {
//           "Content-Type": "application/json"
//         }
//       });
  
//       const data = await response.json();
  
//       // Display AI response
//       responseBox.innerHTML = `
//         <div><strong>AI Intent:</strong> ${data.intent}</div>
//         <div><strong>Message:</strong> ${data.message}</div>
//       `;
  
//       //  Update UI based on intent
//       function handleUIUpdate(intent) {
//         const body = document.body;
//         const root = document.documentElement;
      
//         switch (intent) {
//           case "greeting":
//             body.style.backgroundColor = "#e6ffe6";
//             break;
//           case "comfort":
//             body.style.backgroundColor = "#fff0f0";
//             break;
//           case "calm":
//             body.style.backgroundColor = "#f5f5dc";
//             break;
//           case "text_bigger":
//             root.style.setProperty("--font-size", "1.5em");
//             break;
//           case "text_smaller":
//             root.style.setProperty("--font-size", "1em");
//             break;
//           case "contrast_on":
//             body.classList.add("high-contrast");
//             break;
//           case "contrast_off":
//             body.classList.remove("high-contrast");
//             break;
//           default:
//             body.style.backgroundColor = "#ffffff";
//         }
//       }
      
//     });
  
//     recognition.addEventListener("end", () => {
//       micButton.classList.remove("listening");
//     });
  
//     function handleUIUpdate(intent) {
//       const body = document.body;
  
//       switch (intent) {
//         case "greeting":
//           body.style.backgroundColor = "#e6ffe6";
//           break;
//         case "comfort":
//           body.style.backgroundColor = "#fff0f0";
//           break;
//         case "calm":
//           body.style.backgroundColor = "#f5f5dc";
//           break;
//         case "reassure":
//           body.style.backgroundColor = "#e0f7fa";
//           break;
//         case "connection":
//           body.style.backgroundColor = "#ffe6f2";
//           break;
//         case "wonder":
//           body.style.backgroundColor = "#f0f8ff";
//           break;
//         default:
//           body.style.backgroundColor = "#ffffff";
//       }
//     }
//   });
  
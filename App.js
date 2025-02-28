import { useState } from "react";
import "./App.css";

function App() {
  const [imageBase64, setImageBase64] = useState("");
  const [imageName, setImageName] = useState(""); // New state for filename
  const [retrievedImage, setRetrievedImage] = useState("");
  const [isLoading, setIsLoading] = useState(false); // Loading state

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImageName(file.name); // Store filename
      setIsLoading(true); // Show spinner

      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64String = reader.result;
        setImageBase64(base64String);
        sendToBackend(base64String, file.name); // Pass filename
      };
      reader.onerror = (error) => {
        console.error("Error converting image to Base64:", error);
        setIsLoading(false);
      };
    }
  };

  const sendToBackend = async (base64Image, filename) => {
    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image: base64Image, image_id: filename }),
      });
  
      const data = await response.json();
      console.log("Retrieved results:", data);
  
      if (data.image_base64) {
        setRetrievedImage(`data:image/jpeg;base64,${data.image_base64}`);
      }
    } catch (error) {
      console.error("Error sending image to backend:", error);
    } finally {
      setIsLoading(false); // Hide spinner after processing
    }
  };

  return (
    <div className="App">
      <h1>CBIR Demo</h1>
      <input type="file" accept="image/*" onChange={handleImageUpload} />
      {isLoading && <img src="/spinner.gif" alt="Loading..." style={{ width: "50px", marginTop: "10px" }} />} {/* Spinner */}
      <div style={{
        display: "flex",
        justifyContent: "space-around"
      }}>
        {imageBase64 && (
          <div>
            <p><strong>Filename:</strong> {imageName}</p> {/* Display filename */}
            <img src={imageBase64} alt="Uploaded Preview" style={{ maxWidth: "500px", marginTop: "10px" }} />
          </div>
        )}
        {retrievedImage && (
          <div>
            <h3>Retrieved Image:</h3>
            <img src={retrievedImage} alt="Retrieved from Index" style={{ maxWidth: "500px", marginTop: "10px" }} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

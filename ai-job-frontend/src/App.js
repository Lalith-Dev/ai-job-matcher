import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    const token = "PASTE_YOUR_TOKEN_HERE";

    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post(
      "http://127.0.0.1:8000/api/resumes/upload/",
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      }
    );

    setResult(response.data);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>AI Job Matcher</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={handleUpload}>Upload Resume</button>

      {result && (
        <div>
          <h3>Extracted Skills:</h3>
          <pre>{result.skills}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
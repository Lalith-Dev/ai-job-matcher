import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDesc);

    const res = await axios.post(
      "http://127.0.0.1:8000/api/resumes/ats-analyze/",
      formData
    );

    setResult(res.data);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>ATS Resume Analyzer</h2>

      <textarea
        rows="6"
        placeholder="Paste Job Description"
        onChange={(e) => setJobDesc(e.target.value)}
      />

      <br /><br />

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />

      <br /><br />

      <button onClick={handleSubmit}>Analyze</button>

      {result && (
        <div>
          <h3>Match Score: {result.match_score}</h3>

          <h4>Matched Skills:</h4>
          <pre>{JSON.stringify(result.skills_match.matched_skills, null, 2)}</pre>

          <h4>Missing Skills:</h4>
          <pre>{JSON.stringify(result.skills_match.missing_skills, null, 2)}</pre>

          <h4>Experience:</h4>
          <p>{result.experience_years} years</p>

          <h4>Suggestions:</h4>
          <pre>{JSON.stringify(result.suggestions, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
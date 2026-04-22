import React, { useState } from "react";
import axios from "axios";
import "./App.css";

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
    <div className="container">
  <h2>ATS Resume Analyzer</h2>

  <textarea
    rows="6"
    placeholder="Paste Job Description"
    onChange={(e) => setJobDesc(e.target.value)}
  />

  <input type="file" onChange={(e) => setFile(e.target.files[0])} />

  <br /><br />

  <button onClick={handleSubmit}>
    {loading ? "Analyzing..." : "Analyze Resume"}
  </button>

  {result && (
    <div>
      <h3>Match Score: {result.match_score}%</h3>

      <h4>Matched Skills</h4>
      {result.skills_match.matched_skills.map((s, i) => (
        <span key={i} className="skill green">{s}</span>
      ))}

      <h4>Missing Skills</h4>
      {result.skills_match.missing_skills.map((s, i) => (
        <span key={i} className="skill red">{s}</span>
      ))}

      <h4>Experience</h4>
      <p>{result.experience_years} years</p>

      <h4>Suggestions</h4>
      <ul>
        {result.suggestions.map((s, i) => (
          <li key={i}>{s}</li>
        ))}
      </ul>
    </div>
  )}
</div>
  );
}

export default App;
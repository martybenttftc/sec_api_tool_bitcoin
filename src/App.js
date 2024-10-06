import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [accessionNumber, setAccessionNumber] = useState('');
  const [filingData, setFilingData] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5001/filing/${accessionNumber}`);
      setFilingData(response.data);
      setError(null);
    } catch (err) {
      setFilingData(null);
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  return (
    <div className="App">
      <h1>SEC Filing Search</h1>
      <div>
        <input
          type="text"
          value={accessionNumber}
          onChange={(e) => setAccessionNumber(e.target.value)}
          placeholder="Enter Accession Number"
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      {error && <p className="error">{error}</p>}
      {filingData && (
        <div className="filing-data">
          <h2>Filing Information</h2>
          <p><strong>Accession Number:</strong> {filingData.accession_number}</p>
          <p><strong>Company Name:</strong> {filingData.company_name}</p>
          <p><strong>Form Type:</strong> {filingData.form_type}</p>
          <p><strong>Filed At:</strong> {filingData.filed_at}</p>
          <p><strong>File URL:</strong> <a href={filingData.file_url} target="_blank" rel="noopener noreferrer">{filingData.file_url}</a></p>
        </div>
      )}
    </div>
  );
}

export default App;
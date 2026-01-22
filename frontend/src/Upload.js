import React, { useState } from 'react';

export default function Upload({ onNext }) {
  const [docType, setDocType] = useState('');
  const [files, setFiles] = useState([]);

  const handleFiles = (e) => {
    setFiles([...files, ...Array.from(e.target.files)]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setFiles([...files, ...Array.from(e.dataTransfer.files)]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  return (
    <div className="container">
      <h2>📄 Upload Identity Documents</h2>
      <p>Upload your Aadhaar, PAN, Passport, or other ID documents to extract information</p>

      <div className="form-group">
        <label>Document Type *</label>
        <select value={docType} onChange={(e) => setDocType(e.target.value)}>
          <option value="">Select document type...</option>
          <option value="Aadhaar">🆔 Aadhaar Card</option>
          <option value="PAN">💳 PAN Card</option>
          <option value="Passport">🛂 Passport</option>
          <option value="Driving License">🚗 Driving License</option>
          <option value="Voter ID">🗳️ Voter ID</option>
          <option value="Other">📋 Other ID</option>
        </select>
      </div>

      <div 
        className="upload-zone" 
        onClick={() => document.getElementById('file').click()}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        <div className="upload-icon">⬆️</div>
        <div style={{fontSize: '1.1rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem'}}>
          Drop files here or click to upload
        </div>
        <small style={{color:'#9ca3af'}}>Supports PDF, JPG, PNG (Max 10MB per file)</small>
        <input 
          id="file" 
          type="file" 
          multiple 
          accept=".pdf,.jpg,.jpeg,.png" 
          onChange={handleFiles} 
          style={{display:'none'}} 
        />
      </div>

      {files.length > 0 && (
        <div className="files">
          <h3 style={{marginBottom: '1rem', color: '#374151'}}>
            📂 Uploaded Documents ({files.length})
          </h3>
          {files.map((f, i) => (
            <div key={i} className="file">
              <div className="file-icon">📄</div>
              <div className="file-info">
                <div className="file-name">{f.name}</div>
                <div className="file-type">{docType} • {(f.size / 1024).toFixed(1)} KB</div>
              </div>
              <span style={{color:'#10b981', fontSize: '1.5rem'}}>✓</span>
              <button 
                onClick={() => removeFile(i)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#ef4444',
                  cursor: 'pointer',
                  fontSize: '1.2rem',
                  padding: '0.5rem'
                }}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="buttons">
        <button 
          className="btn btn-primary" 
          onClick={() => onNext({files, documentType: docType})} 
          disabled={!docType || files.length === 0}
        >
          Continue to Extract →
        </button>
      </div>
    </div>
  );
}
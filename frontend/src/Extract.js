import React, { useState, useEffect } from 'react';
import { uploadDocuments } from './api';

export default function Extract({ docs, onNext, onBack }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(false);
  const [editedData, setEditedData] = useState({});

  useEffect(() => {
    extract();
  }, []);

  const extract = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Sending files to backend:', docs.files);
      
      const result = await uploadDocuments(docs.files, docs.documentType);
      console.log('Backend response:', result);
      
      if (result.success) {
        setData(result.extractedData);
        setEditedData(result.extractedData);
      } else {
        setError('Failed to extract data from documents');
      }
    } catch (err) {
      console.error('Extraction error:', err);
      setError('Error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (field, value) => {
    setEditedData({
      ...editedData,
      [field]: value
    });
  };

  const handleSave = () => {
    setData(editedData);
    setEditing(false);
  };

  const handleCancel = () => {
    setEditedData(data);
    setEditing(false);
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>🔍 Extracting data from your documents...</p>
          <p style={{ fontSize: '0.9rem', color: '#6b7280', marginTop: '0.5rem' }}>
            This may take a few seconds...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>⚠️</div>
          <div>{error}</div>
        </div>
        <div style={{ marginTop: '1.5rem', padding: '1rem', background: '#f9fafb', borderRadius: '8px', fontSize: '0.9rem' }}>
          <strong>Troubleshooting tips:</strong>
          <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
            <li>Make sure your backend server is running</li>
            <li>Check if the document is clear and readable</li>
            <li>Try uploading a different image or PDF</li>
            <li>Check the browser console (F12) for more details</li>
          </ul>
        </div>
        <div className="buttons">
          <button className="btn btn-secondary" onClick={onBack}>← Back</button>
          <button className="btn btn-primary" onClick={extract}>🔄 Retry Extraction</button>
        </div>
      </div>
    );
  }

  const labels = {
    name: 'Full Name',
    fatherName: "Father's Name",
    dateOfBirth: 'Date of Birth',
    gender: 'Gender',
    address: 'Address',
    city: 'City',
    state: 'State',
    pincode: 'Pincode',
    phone: 'Phone Number',
    email: 'Email Address',
    idNumber: 'ID Number (Aadhaar/PAN)'
  };

  const filledCount = Object.values(editedData || {}).filter(v => v && v.trim()).length;
  const totalFields = Object.keys(labels).length;

  return (
    <div className="container">
      <h2>✅ Data Extracted Successfully</h2>
      <p>Review and edit the information extracted from your documents</p>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="success" style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🎉</span>
          <span>Extracted {filledCount} out of {totalFields} fields</span>
        </div>
        {!editing && filledCount < totalFields && (
          <div style={{ 
            padding: '1rem', 
            background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
            border: '2px solid #fbbf24',
            borderRadius: '10px',
            fontSize: '0.85rem',
            color: '#92400e'
          }}>
            💡 Tip: You can manually add missing information
          </div>
        )}
      </div>

      {!editing ? (
        <>
          <div className="data-preview">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0 }}>📋 Personal Information</h3>
              <button 
                onClick={() => setEditing(true)}
                style={{
                  padding: '0.5rem 1rem',
                  background: '#6366f1',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: '600'
                }}
              >
                ✏️ Edit Data
              </button>
            </div>
            
            {Object.entries(labels).map(([key, label]) => {
              const value = editedData[key];
              const isEmpty = !value || !value.trim();
              
              return (
                <div key={key} className="data-field">
                  <span className="field-label">{label}</span>
                  <span 
                    className="field-value" 
                    style={{
                      color: isEmpty ? '#9ca3af' : '#1f2937',
                      fontStyle: isEmpty ? 'italic' : 'normal'
                    }}
                  >
                    {isEmpty ? 'Not found' : value}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="buttons">
            <button className="btn btn-secondary" onClick={onBack}>← Back</button>
            <button className="btn btn-primary" onClick={() => onNext(editedData)}>
              Continue to Select Form →
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="data-preview">
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0, marginBottom: '0.5rem' }}>✏️ Edit Information</h3>
              <p style={{ color: '#6b7280', fontSize: '0.9rem', margin: 0 }}>
                Update any incorrect or missing fields
              </p>
            </div>
            
            {Object.entries(labels).map(([key, label]) => (
              <div key={key} style={{ marginBottom: '1.5rem' }}>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  fontWeight: '600', 
                  color: '#374151',
                  fontSize: '0.9rem'
                }}>
                  {label}
                </label>
                {key === 'address' ? (
                  <textarea
                    value={editedData[key] || ''}
                    onChange={(e) => handleEdit(key, e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #d1d5db',
                      borderRadius: '8px',
                      fontSize: '0.95rem',
                      fontFamily: 'inherit',
                      resize: 'vertical'
                    }}
                    placeholder={`Enter ${label.toLowerCase()}`}
                  />
                ) : (
                  <input
                    type="text"
                    value={editedData[key] || ''}
                    onChange={(e) => handleEdit(key, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #d1d5db',
                      borderRadius: '8px',
                      fontSize: '0.95rem'
                    }}
                    placeholder={`Enter ${label.toLowerCase()}`}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="buttons">
            <button className="btn btn-secondary" onClick={handleCancel}>
              ✕ Cancel
            </button>
            <button className="btn btn-primary" onClick={handleSave}>
              ✓ Save Changes
            </button>
          </div>
        </>
      )}
    </div>
  );
}
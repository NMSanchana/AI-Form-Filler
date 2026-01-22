import React, { useState } from 'react';

export default function Review({ data, onNext, onBack }) {
  const [edit, setEdit] = useState(false);
  const [review, setReview] = useState({ ...data });

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
    idNumber: 'ID Number'
  };

  const icons = {
    name: '👤',
    fatherName: '👨',
    dateOfBirth: '📅',
    gender: '⚧',
    address: '🏠',
    city: '🏙️',
    state: '📍',
    pincode: '📮',
    phone: '📱',
    email: '📧',
    idNumber: '🆔'
  };

  return (
    <div className="container">
      <h2>👁️ Review Information</h2>
      <p>Final review of all information before filling the form</p>

      <div style={{
        display: 'flex', 
        justifyContent: 'space-between', 
        marginBottom: '2rem',
        padding: '1.5rem',
        background: 'linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)',
        borderRadius: '12px',
        border: '2px solid #e5e7eb'
      }}>
        <div>
          <div style={{fontSize: '1.2rem', fontWeight: '700', color: '#1f2937'}}>
            ✅ {Object.values(review).filter(v => v && v.trim()).length} Fields Ready
          </div>
          <div style={{fontSize: '0.9rem', color: '#6b7280', marginTop: '0.25rem'}}>
            All information will be filled into the form
          </div>
        </div>
        <button 
          className={`btn ${edit ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setEdit(!edit)}
        >
          {edit ? '✓ Done Editing' : '✏️ Edit Fields'}
        </button>
      </div>

      {edit ? (
        <div style={{display: 'grid', gap: '1.5rem'}}>
          {Object.keys(labels).map(k => (
            <div key={k} className="form-group">
              <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                <span style={{fontSize: '1.2rem'}}>{icons[k]}</span>
                <span>{labels[k]}</span>
              </label>
              {k === 'address' ? (
                <textarea 
                  value={review[k] || ''} 
                  onChange={(e) => setReview({ ...review, [k]: e.target.value })} 
                  rows="3"
                />
              ) : k === 'gender' ? (
                <select 
                  value={review[k] || ''} 
                  onChange={(e) => setReview({ ...review, [k]: e.target.value })}
                >
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              ) : (
                <input 
                  type={k === 'dateOfBirth' ? 'date' : k === 'email' ? 'email' : k === 'phone' ? 'tel' : 'text'}
                  value={review[k] || ''} 
                  onChange={(e) => setReview({ ...review, [k]: e.target.value })} 
                />
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="data-preview">
          <h3>📋 Final Data Summary</h3>
          {Object.entries(labels).map(([k, l]) => (
            <div key={k} className="data-field">
              <span className="field-label" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                <span>{icons[k]}</span>
                <span>{l}</span>
              </span>
              <span className="field-value" style={{
                color: review[k] ? '#1f2937' : '#9ca3af',
                fontWeight: review[k] ? '600' : '400'
              }}>
                {review[k] || 'Not provided'}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="buttons">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn btn-primary" onClick={() => onNext(review)}>
          Continue to Export →
        </button>
      </div>
    </div>
  );
}
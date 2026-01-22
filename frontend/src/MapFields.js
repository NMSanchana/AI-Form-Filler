import React, { useState, useEffect } from 'react';

export default function MapFields({ data, form, onNext, onBack }) {
  const [mapped, setMapped] = useState({});

  useEffect(() => {
    setMapped({ ...data });
  }, [data]);

  const fields = [
    { key: 'name', label: 'Full Name', type: 'text', icon: '👤' },
    { key: 'fatherName', label: "Father's Name", type: 'text', icon: '👨' },
    { key: 'dateOfBirth', label: 'Date of Birth', type: 'date', icon: '📅' },
    { key: 'gender', label: 'Gender', type: 'select', options: ['Male', 'Female', 'Other'], icon: '⚧' },
    { key: 'address', label: 'Address', type: 'textarea', icon: '🏠' },
    { key: 'city', label: 'City', type: 'text', icon: '🏙️' },
    { key: 'state', label: 'State', type: 'text', icon: '📍' },
    { key: 'pincode', label: 'Pincode', type: 'text', icon: '📮' },
    { key: 'phone', label: 'Phone Number', type: 'tel', icon: '📱' },
    { key: 'email', label: 'Email Address', type: 'email', icon: '📧' },
    { key: 'idNumber', label: 'ID Number', type: 'text', icon: '🆔' }
  ];

  const change = (k, v) => setMapped({ ...mapped, [k]: v });

  const filledCount = fields.filter(f => mapped[f.key] && mapped[f.key].trim()).length;

  return (
    <div className="container">
      <h2>🔗 Map Fields</h2>
      <p>Review and edit the auto-mapped fields for <strong>{form?.name}</strong></p>

      <div style={{
        background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
        padding: '1.5rem',
        borderRadius: '12px',
        marginBottom: '2rem',
        border: '2px solid #c7d2fe'
      }}>
        <div style={{display: 'flex', justifyContent: 'center', gap: '3rem'}}>
          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: '2rem', fontWeight: '700', color: '#6366f1'}}>
              {filledCount}/{fields.length}
            </div>
            <div style={{fontSize: '0.85rem', color: '#6b7280', fontWeight: '600'}}>
              Fields Filled
            </div>
          </div>
        </div>
      </div>

      <div style={{display: 'grid', gap: '1.5rem'}}>
        {fields.map(f => (
          <div key={f.key} className="form-group">
            <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <span style={{fontSize: '1.2rem'}}>{f.icon}</span>
              <span>{f.label}</span>
            </label>
            {f.type === 'select' ? (
              <select value={mapped[f.key] || ''} onChange={(e) => change(f.key, e.target.value)}>
                <option value="">Select {f.label}</option>
                {f.options.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            ) : f.type === 'textarea' ? (
              <textarea 
                value={mapped[f.key] || ''} 
                onChange={(e) => change(f.key, e.target.value)} 
                rows="3"
                style={{resize: 'vertical'}}
              />
            ) : (
              <input 
                type={f.type} 
                value={mapped[f.key] || ''} 
                onChange={(e) => change(f.key, e.target.value)} 
                placeholder={`Enter ${f.label}`}
              />
            )}
          </div>
        ))}
      </div>

      <div className="buttons">
        <button className="btn btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn btn-primary" onClick={() => onNext(mapped)}>
          Continue to Review →
        </button>
      </div>
    </div>
  );
}
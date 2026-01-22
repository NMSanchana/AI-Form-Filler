import React, { useState } from 'react';
import { fillPDF, fillURL } from './api';

export default function Export({ data, form, onBack }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleExport = async () => {
    setLoading(true);
    setError(null);

    try {
      if (form.type === 'url') {
        const res = await fillURL(form.url, data);
        console.log('Fill URL Response:', res); // Debug log
        
        if (res.success) {
          setResult({ 
            type: 'url', 
            message: res.message,
            filled_count: res.filled_count || 0,
            total_fields: res.total_fields || Object.keys(data).length,
            failed_fields: res.failed_fields || []
          });
        }
      } else {
        const res = await fillPDF(form.path, data);
        if (res.success) {
          setResult({ type: 'pdf', url: res.downloadUrl });
        }
      }
    } catch (err) {
      console.error('Export error:', err);
      setError('Error: ' + (err.response?.data?.detail?.message || err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>⚙️ {form.type === 'url' ? 'Opening browser and filling form...' : 'Generating your filled PDF...'}</p>
          {form.type === 'url' && (
            <p style={{fontSize: '0.9rem', color: '#6b7280', marginTop: '1rem'}}>
              Browser will stay open for 60 seconds for you to review
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>🚀 Export Form</h2>
      <p>Fill and download your completed form</p>

      {error && <div className="error">⚠️ {error}</div>}

      {result ? (
        <div>
          <div className="success">
            ✅ Form filled successfully!
          </div>

          {result.type === 'pdf' && (
            <div style={{
              textAlign: 'center',
              padding: '3rem 2rem',
              background: 'linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)',
              borderRadius: '12px',
              border: '2px solid #e5e7eb'
            }}>
              <div style={{fontSize: '4rem', marginBottom: '1.5rem'}}>📄</div>
              <h3 style={{marginBottom: '1rem', color: '#1f2937', fontSize: '1.5rem'}}>
                Your filled form is ready!
              </h3>
              <p style={{marginBottom: '2rem', color: '#6b7280'}}>
                Click the button below to download your completed form
              </p>
              <a 
                href={result.url} 
                className="btn btn-primary"
                download
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  textDecoration: 'none',
                  fontSize: '1.1rem',
                  padding: '1rem 2rem'
                }}
              >
                <span>⬇️</span>
                <span>Download Filled Form</span>
              </a>
            </div>
          )}

          {result.type === 'url' && (
            <div style={{
              textAlign: 'center',
              padding: '3rem 2rem',
              background: 'linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)',
              borderRadius: '12px',
              border: '2px solid #e5e7eb'
            }}>
              <div style={{fontSize: '4rem', marginBottom: '1.5rem'}}>🌐</div>
              <h3 style={{marginBottom: '1rem', color: '#1f2937', fontSize: '1.5rem'}}>
                Online form filled!
              </h3>
              
              {/* FILLED COUNT DISPLAY */}
              <div style={{
                display: 'inline-block',
                padding: '1rem 2rem',
                background: result.filled_count > 0 ? '#dcfce7' : '#fee2e2',
                border: `2px solid ${result.filled_count > 0 ? '#86efac' : '#fca5a5'}`,
                borderRadius: '10px',
                marginBottom: '1.5rem'
              }}>
                <div style={{
                  fontSize: '2rem', 
                  fontWeight: '700',
                  color: result.filled_count > 0 ? '#166534' : '#991b1b'
                }}>
                  Filled {result.filled_count}/{result.total_fields} fields successfully
                </div>
              </div>

              <p style={{color: '#6b7280', marginBottom: '1rem', fontSize: '0.95rem'}}>
                {result.message}
              </p>

              {/* Show failed fields if any */}
              {result.failed_fields && result.failed_fields.length > 0 && (
                <div style={{
                  padding: '1rem',
                  background: '#fef3c7',
                  border: '2px solid #fcd34d',
                  borderRadius: '8px',
                  marginTop: '1rem',
                  textAlign: 'left'
                }}>
                  <strong style={{color: '#92400e'}}>⚠️ Could not fill these fields:</strong>
                  <div style={{marginTop: '0.5rem', fontSize: '0.9rem', color: '#78350f'}}>
                    {result.failed_fields.join(', ')}
                  </div>
                </div>
              )}

              <div style={{
                padding: '1.25rem',
                background: '#e0e7ff',
                border: '2px solid #c7d2fe',
                borderRadius: '10px',
                marginTop: '1.5rem'
              }}>
                <p style={{fontSize: '0.95rem', color: '#3730a3', margin: 0}}>
                  <strong>⚠️ Note:</strong> The browser window remained open for 60 seconds 
                  for you to review. Please submit the form manually if needed.
                </p>
              </div>
            </div>
          )}

          <div style={{
            marginTop: '2rem',
            padding: '1.5rem',
            background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
            borderRadius: '12px',
            border: '2px solid #c7d2fe'
          }}>
            <h4 style={{fontSize: '1rem', color: '#4338ca', marginBottom: '0.75rem', fontWeight: '700'}}>
              🎉 Success! What's next?
            </h4>
            <ul style={{
              fontSize: '0.95rem',
              color: '#6b7280',
              marginLeft: '1.75rem',
              lineHeight: '1.8'
            }}>
              {result.type === 'pdf' ? (
                <>
                  <li>Review the downloaded PDF carefully</li>
                  <li>Print or email the form as needed</li>
                  <li>Submit to the relevant authority</li>
                </>
              ) : (
                <>
                  <li>Review all filled fields in the browser</li>
                  <li>Make any final adjustments if needed</li>
                  <li>Submit the form online</li>
                </>
              )}
            </ul>
          </div>

          <div className="buttons" style={{marginTop: '2rem'}}>
            <button className="btn btn-secondary" onClick={() => {
              setResult(null);
              setError(null);
            }}>
              ← Fill Another Form
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="data-preview">
            <h3>📋 Export Details</h3>
            <div className="data-field">
              <span className="field-label">Form Name</span>
              <span className="field-value">{form.name}</span>
            </div>
            <div className="data-field">
              <span className="field-label">Form Type</span>
              <span className="field-value">
                {form.type === 'url' ? '🌐 Online Form' : '📄 PDF Form'}
              </span>
            </div>
            <div className="data-field">
              <span className="field-label">Total Fields</span>
              <span className="field-value">
                {Object.keys(data).filter(k => data[k] && data[k].trim()).length} fields
              </span>
            </div>
          </div>

          {form.type === 'url' && (
            <div style={{
              marginTop: '1.5rem',
              padding: '1.25rem',
              background: '#fef3c7',
              border: '2px solid #fcd34d',
              borderRadius: '10px'
            }}>
              <p style={{fontSize: '0.95rem', color: '#92400e', margin: 0}}>
                <strong>⚠️ Important:</strong> For online forms, a browser window will open automatically. 
                The form will be auto-filled but NOT submitted. Please review and submit manually.
              </p>
            </div>
          )}

          <div className="buttons">
            <button className="btn btn-secondary" onClick={onBack}>← Back</button>
            <button className="btn btn-primary" onClick={handleExport}>
              <span style={{fontSize: '1.2rem', marginRight: '0.5rem'}}>🚀</span>
              Fill Form Now
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
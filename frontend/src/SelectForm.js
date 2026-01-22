import React, { useState, useEffect } from 'react';
import { getSampleForms, uploadForm } from './api';

export default function SelectForm({ onNext, onBack }) {
  const [type, setType] = useState('');
  const [selected, setSelected] = useState(null);
  const [samples, setSamples] = useState([]);
  const [uploaded, setUploaded] = useState(null);
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSampleForms().then(r => r.success && setSamples(r.forms));
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
      const result = await uploadForm(file);
      if (result.success) {
        const f = {
          name: file.name,
          path: result.formPath,
          type: 'uploaded'
        };
        setUploaded(f);
        setSelected(f);
      }
    } catch (err) {
      alert('Error uploading form: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    let form = null;

    if (type === 'sample' && selected) form = selected;
    else if (type === 'upload' && uploaded) form = uploaded;
    else if (type === 'url' && url)
      form = { type: 'url', url, name: 'Online Form' };

    if (form) onNext(form);
  };

  return (
    <div className="container">
      <h2>📝 Select Form</h2>
      <p>Choose a form to fill with your extracted data</p>

      <div className="form-group">
        <label>Form Type *</label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="">Select form type...</option>
          <option value="sample">📚 Sample Forms</option>
          <option value="upload">📤 Upload PDF Form</option>
          <option value="url">🌐 Online Form (URL)</option>
        </select>
      </div>

      {/* SAMPLE FORMS */}
      {type === 'sample' && (
        <div>
          {samples.length > 0 ? (
            <div className="form-options">
              {samples.map((f) => (
                <div
                  key={f.id}
                  className={`form-option ${
                    selected?.id === f.id ? 'selected' : ''
                  }`}
                  onClick={() => setSelected(f)}
                >
                  <h4>📋 {f.name}</h4>
                  <p>Type: {f.type}</p>
                </div>
              ))}
            </div>
          ) : (
            <div
              style={{
                padding: '2rem',
                textAlign: 'center',
                background: '#f9fafb',
                borderRadius: '12px',
                border: '2px dashed #d1d5db'
              }}
            >
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📂</div>
              <p
                style={{
                  color: '#6b7280',
                  marginBottom: '0.5rem',
                  fontWeight: '600'
                }}
              >
                No sample forms available
              </p>
              <p
                style={{
                  color: '#9ca3af',
                  fontSize: '0.9rem',
                  margin: 0
                }}
              >
                Place PDF forms in backend/sample-forms/ folder
              </p>
            </div>
          )}
        </div>
      )}

      {/* UPLOAD FORM */}
      {type === 'upload' && (
        <div>
          <div
            className="upload-zone"
            onClick={() =>
              !loading && document.getElementById('form').click()
            }
            style={{
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1
            }}
          >
            <div className="upload-icon">📋</div>
            <div
              style={{
                fontSize: '1.1rem',
                fontWeight: '600',
                color: '#374151'
              }}
            >
              {loading ? '⏳ Processing...' : 'Click to upload form'}
            </div>
            <small style={{ color: '#9ca3af' }}>
              Supports PDF files (Max 10MB)
            </small>

            <input
              id="form"
              type="file"
              accept=".pdf"
              onChange={handleUpload}
              style={{ display: 'none' }}
              disabled={loading}
            />
          </div>

          {uploaded && (
            <div className="files">
              <div className="file">
                <div className="file-icon">📋</div>
                <div className="file-info">
                  <div className="file-name">{uploaded.name}</div>
                  <div className="file-type">Uploaded Form</div>
                </div>
                <span style={{ color: '#10b981', fontSize: '1.5rem' }}>
                  ✓
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* URL FORM */}
      {type === 'url' && (
        <div>
          <div className="form-group">
            <label>Form URL *</label>
            <input
              type="url"
              placeholder="https://example.com/form"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>

          {url && (
            <div
              style={{
                padding: '1rem',
                background: '#fef3c7',
                border: '2px solid #fcd34d',
                borderRadius: '10px',
                marginTop: '1rem'
              }}
            >
              <p
                style={{
                  fontSize: '0.9rem',
                  color: '#92400e',
                  margin: 0
                }}
              >
                <strong>⚠️ Note:</strong> Browser will open and auto-fill the
                form. It will remain open for 30 seconds for review.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ACTION BUTTONS */}
      <div className="buttons">
        <button className="btn btn-secondary" onClick={onBack}>
          ← Back
        </button>

        <button
          className="btn btn-primary"
          onClick={handleNext}
          disabled={
            !type ||
            (type === 'sample' && !selected) ||
            (type === 'upload' && !uploaded) ||
            (type === 'url' && !url) ||
            loading
          }
        >
          Continue to Map Fields →
        </button>
      </div>
    </div>
  );
}

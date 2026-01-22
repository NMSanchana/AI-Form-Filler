import React, { useState } from 'react';
import './App.css';
import Upload from './Upload';
import Extract from './Extract';
import SelectForm from './SelectForm';
import MapFields from './MapFields';
import Review from './Review';
import Export from './Export';

function App() {
  const [step, setStep] = useState(1);
  const [docs, setDocs] = useState([]);
  const [extracted, setExtracted] = useState({});
  const [form, setForm] = useState(null);
  const [mapped, setMapped] = useState({});

  const steps = ['Upload', 'Extract', 'Select Form', 'Map Fields', 'Review', 'Export'];

  const reset = () => {
    setStep(1);
    setDocs([]);
    setExtracted({});
    setForm(null);
    setMapped({});
  };

  return (
    <div className="app">
      <header>
        <button onClick={reset}>← Home</button>
        <h1>🤖 AI Form Filler</h1>
        <button onClick={reset}>↻ Reset</button>
      </header>

      <div className="progress">
        {steps.map((s, i) => (
          <div key={i} className={`step ${step >= i + 1 ? 'active' : ''}`}>
            <div className="circle">{i + 1}</div>
            <span>{s}</span>
          </div>
        ))}
      </div>

      <main>
        {step === 1 && <Upload onNext={(d) => { setDocs(d); setStep(2); }} />}
        {step === 2 && <Extract docs={docs} onNext={(e) => { setExtracted(e); setStep(3); }} onBack={() => setStep(1)} />}
        {step === 3 && <SelectForm onNext={(f) => { setForm(f); setStep(4); }} onBack={() => setStep(2)} />}
        {step === 4 && <MapFields data={extracted} form={form} onNext={(m) => { setMapped(m); setStep(5); }} onBack={() => setStep(3)} />}
        {step === 5 && <Review data={mapped} onNext={(r) => { setMapped(r); setStep(6); }} onBack={() => setStep(4)} />}
        {step === 6 && <Export data={mapped} form={form} onBack={() => setStep(5)} />}
      </main>
    </div>
  );
}

export default App;
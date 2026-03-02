import { useState } from 'react';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [minVal, setMinVal] = useState<number>(-1.0);
  const [maxVal, setMaxVal] = useState<number>(1.5);
  const [result, setResult] = useState<{ pressure: number; angle: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("min_val", minVal.toString());
    formData.append("max_val", maxVal.toString());

    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        setError(data.error || "Failed to process image.");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Network error. Make sure the FastAPI backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', fontFamily: 'system-ui', textAlign: 'center', color: '#333' }}>
      <h1>Gauge Vision AI</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
      </div>

      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'center', gap: '20px' }}>
        <div>
          <label>Min Value: </label>
          <input type="number" value={minVal} onChange={(e) => setMinVal(Number(e.target.value))} style={{ width: '60px' }} />
        </div>
        <div>
          <label>Max Value: </label>
          <input type="number" value={maxVal} onChange={(e) => setMaxVal(Number(e.target.value))} style={{ width: '60px' }} />
        </div>
      </div>

      {preview && (
        <div style={{ marginBottom: '20px' }}>
          <img src={preview} alt="Preview" style={{ maxWidth: '100%', maxHeight: '350px', borderRadius: '8px' }} />
        </div>
      )}

      <button 
        onClick={handleUpload} 
        disabled={!selectedFile || loading}
        style={{ padding: '12px 24px', fontSize: '16px', cursor: selectedFile ? 'pointer' : 'not-allowed', backgroundColor: selectedFile ? '#007BFF' : '#ccc', color: 'white', border: 'none', borderRadius: '5px' }}
      >
        {loading ? "Analyzing..." : "Read Pressure"}
      </button>

      {error && <div style={{ marginTop: '20px', color: 'red' }}>{error}</div>}

      {result && (
        <div style={{ marginTop: '30px', padding: '20px', border: '2px solid #28A745', borderRadius: '8px', backgroundColor: '#EAF8ED' }}>
          <h2 style={{ margin: '0 0 10px 0', color: '#28A745' }}>Reading: {result.pressure} Units</h2>
          <p style={{ margin: 0, color: '#555' }}>Calculated Angle: {result.angle}°</p>
        </div>
      )}
    </div>
  );
}

export default App;
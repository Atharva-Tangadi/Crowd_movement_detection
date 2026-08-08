import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Camera, StopCircle, Upload, AlertTriangle, Activity, Users } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [status, setStatus] = useState('Stopped');
  const [stats, setStats] = useState({
    crowd: { count: 0, peak: 0, status: 'LOW' },
    movement: { dominant: 'Mixed/None', counts: {} },
    fps: 0,
    alert: null
  });
  const [alerts, setAlerts] = useState([]);
  
  const [videoSrc, setVideoSrc] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;

    const connectWebSocket = () => {
      ws = new WebSocket('ws://localhost:8000/api/ws/stats');
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.status) {
          setStatus(data.status);
          if (data.status === 'Stopped') {
            setVideoSrc(null);
          }
        }
        setStats({
          crowd: data.crowd || { count: 0, peak: 0, status: 'LOW' },
          movement: data.movement || { dominant: 'Mixed/None', counts: {} },
          fps: data.fps || 0
        });
        
        if (data.alert) {
          setAlerts(prev => {
            if (!prev.find(a => a.timestamp === data.alert.timestamp)) {
               return [data.alert, ...prev].slice(0, 10);
            }
            return prev;
          });
        }
      };
      
      ws.onclose = () => {
        setStatus('Error (Backend Disconnected)');
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = () => {
        // Suppress websocket connection errors
      };
    };

    connectWebSocket();
    
    return () => {
      clearTimeout(reconnectTimeout);
      if (ws) {
        ws.onclose = null;
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        } else if (ws.readyState === WebSocket.CONNECTING) {
          ws.onopen = () => ws.close();
        }
      }
    };
  }, []);

  const handleStartCamera = async () => {
    setErrorMessage('');
    try {
      if (status === 'Running') {
        await axios.post(`${API_URL}/process/stop`);
      }
      setStatus('Loading...');
      await axios.post(`${API_URL}/process/start/camera`);
      setStatus('Running');
      setVideoSrc(`${API_URL}/video/stream?t=${new Date().getTime()}`);
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.message || 'Failed to start camera. Make sure webcam is connected.';
      setErrorMessage(msg);
      setStatus('Stopped');
      setVideoSrc(null);
    }
  };

  const handleStop = async () => {
    try {
      await axios.post(`${API_URL}/process/stop`);
      setStatus('Stopped');
      setVideoSrc(null);
      setErrorMessage('');
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setErrorMessage('');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      if (status === 'Running') {
        await axios.post(`${API_URL}/process/stop`);
      }
      setStatus('Loading...');
      await axios.post(`${API_URL}/process/start/video`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus('Running');
      setVideoSrc(`${API_URL}/video/stream?t=${new Date().getTime()}`);
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.message || 'Failed to process uploaded video.';
      setErrorMessage(msg);
      setStatus('Stopped');
      setVideoSrc(null);
    }
  };

  // Format data for Recharts
  const directionData = Object.keys(stats.movement.counts || {}).map(dir => ({
    name: dir,
    count: stats.movement.counts[dir]
  })).filter(d => d.name !== 'Stationary' && d.name !== 'Unknown');

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>Crowd Movement Detection & Direction Analysis</h1>
        <div className="status-indicator">
          <div className={`status-dot ${status.toLowerCase()}`}></div>
          {status}
        </div>
      </header>

      <main className="main-content">
        {/* Left Column: Video & Controls */}
        <div className="video-section">
          <div className="video-container">
            {status === 'Running' && videoSrc ? (
              <img src={videoSrc} className="video-feed" alt="Video Stream" />
            ) : (
              <div className="no-video-placeholder">
                <Camera size={48} />
                <p>{status === 'Loading...' ? 'Initializing stream...' : 'No active video feed'}</p>
              </div>
            )}
          </div>
          
          {errorMessage && (
            <div style={{ backgroundColor: 'rgba(239,68,68,0.2)', border: '1px solid #ef4444', color: '#f8fafc', padding: '0.75rem', borderRadius: '8px', fontSize: '0.9rem' }}>
              ⚠️ {errorMessage}
            </div>
          )}
          
          <div className="controls">
            <button className="btn btn-primary" onClick={handleStartCamera} disabled={status === 'Loading...'}>
              <Camera size={20} />
              Start Camera
            </button>
            <div className="file-input-wrapper">
              <button className="btn btn-primary" disabled={status === 'Loading...'}>
                <Upload size={20} />
                Upload Video
              </button>
              <input type="file" accept="video/*" onChange={handleFileUpload} disabled={status === 'Loading...'} />
            </div>
            <button className="btn btn-danger" onClick={handleStop} disabled={status === 'Stopped'}>
              <StopCircle size={20} />
              Stop Processing
            </button>
          </div>
        </div>

        {/* Right Column: Telemetry & Alerts */}
        <div className="side-panel">
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-title"><Users size={16} style={{display:'inline', marginRight: '5px'}}/> Count</span>
              <span className="stat-value">{stats.crowd.count}</span>
            </div>
            <div className="stat-card">
              <span className="stat-title">Peak Count</span>
              <span className="stat-value">{stats.crowd.peak}</span>
            </div>
            <div className="stat-card">
              <span className="stat-title">Density</span>
              <span className={`stat-value value-${stats.crowd.status.toLowerCase()}`}>
                {stats.crowd.status}
              </span>
            </div>
            <div className="stat-card">
              <span className="stat-title"><Activity size={16} style={{display:'inline', marginRight: '5px'}}/> FPS</span>
              <span className="stat-value">{stats.fps}</span>
            </div>
          </div>
          
          <div className="chart-section">
            <div className="section-title">Dominant Direction: {stats.movement.dominant}</div>
            <div style={{ width: '100%', height: 150 }}>
              <ResponsiveContainer>
                <BarChart data={directionData}>
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                  <Tooltip cursor={{fill: 'rgba(255,255,255,0.1)'}} contentStyle={{backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff'}} />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="alerts-section" style={{flex: 1, display: 'flex', flexDirection: 'column'}}>
            <div className="section-title">Recent Alerts</div>
            <div className="alerts-list" style={{overflowY: 'auto', flex: 1}}>
              {alerts.length === 0 ? (
                <div style={{color: 'var(--text-muted)', textAlign: 'center', marginTop: '1rem'}}>No active alerts</div>
              ) : (
                alerts.map((alert, index) => (
                  <div key={index} className={`alert-item alert-${alert.severity}`}>
                    <div className="alert-header">
                      <div className="alert-type">
                        <AlertTriangle size={14} style={{display:'inline', marginRight: '4px', verticalAlign: 'middle'}}/>
                        {alert.type}
                      </div>
                      <div className="alert-time">{new Date(alert.timestamp).toLocaleTimeString()}</div>
                    </div>
                    <div className="alert-desc">{alert.description}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

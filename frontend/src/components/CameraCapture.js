// /Users/kuldeepkhalotiya/Face/frontend/src/components/CameraCapture.js

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

// Helper function to convert the callback-based `canvas.toBlob` into a Promise.
// This allows us to use async/await for cleaner, more readable code.
const getCanvasBlob = (canvas) => {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error('Canvas is empty. Failed to create blob.'));
      }
    }, 'image/jpeg', 0.95); // Use a quality setting of 95%
  });
};

const CameraCapture = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [attendanceResult, setAttendanceResult] = useState(null);
  const [statusMessage, setStatusMessage] = useState('Initializing webcam...');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mediaStream = null; // Initialize to null
    const startWebcam = async () => {
      // No need to check for `stream` state here, the empty dependency array handles it.
      setError('');
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
        setStream(mediaStream); // Still set state to use the stream in other component logic
        setStatusMessage('Webcam started. Click "Mark Attendance" to proceed.');
      } catch (err) {
        console.error('Error accessing webcam:', err);
        setError('Could not access webcam. Please allow webcam permissions and try again.');
        setStatusMessage('');
      }
    };
 
    startWebcam();
 
    return () => {
      // This cleanup function has a closure over the `mediaStream` variable.
      // It will stop the correct stream when the component unmounts.
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const captureAndRecognize = async (event) => {
    if (!videoRef.current || !canvasRef.current || !stream) return;
    event.preventDefault(); // Prevent default form submission behavior

    setError('');
    setAttendanceResult(null);
    setLoading(true);
    setStatusMessage('Capturing and processing image...');

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    try {
      // 1. Get the image as a Blob from the canvas using our new helper
      const blob = await getCanvasBlob(canvas);

      // 2. Create a FormData object. This is the container for our file.
      const formData = new FormData();

      // 3. Append the blob to FormData.
      formData.append('file', blob, 'capture.jpg');

      // 4. Post the FormData to the backend.
      const apiUrl = process.env.REACT_APP_API_URL || '';
      // The original code had a fix comment about adding /api, which is correct.
      const response = await axios.post(`${apiUrl}/api/mark-attendance`, formData);

      setAttendanceResult(response.data);
      setStatusMessage(response.data.message || 'Attendance processing complete.');
    } catch (err) {
      // Log the full error object to the browser console for debugging.
      console.error('Error marking attendance:', err);

      // Extract the specific 'detail' message from the backend's JSON response.
      const errorMessage = err.response?.data?.detail || 'An error occurred while marking attendance.';
      setError(errorMessage);

      setStatusMessage('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <video
        ref={videoRef}
        width="640"
        height="480"
        autoPlay
        muted
      style={{
        borderWidth: '1px', borderStyle: 'solid', borderColor: '#ddd', borderRadius: '8px',
      }}
      />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <div style={{ marginTop: '1rem' }}>
        <button type="button" onClick={captureAndRecognize} disabled={!stream || loading} style={buttonStyle}>
          {loading ? 'Processing...' : 'Mark Attendance'}
        </button>
      </div>
      {statusMessage && !error && <p>{renderContent(statusMessage)}</p>}
      {error && <p style={{ color: 'red' }}>{renderContent(error)}</p>}
      {attendanceResult && (
        <div style={{ marginTop: '1rem', textAlign: 'left', display: 'inline-block' }}>
          <h3>Attendance Status</h3>
          {attendanceResult.name ? (
            <>
              <p><strong>Status:</strong> <span style={{color: 'green', fontWeight: 'bold'}}>Success</span></p>
              <p><strong>Name:</strong> {attendanceResult.name}</p>
              <p><strong>Emotion:</strong> {attendanceResult.emotion}</p>
              <p><strong>Timestamp:</strong> {new Date(attendanceResult.timestamp).toLocaleString()}</p>
            </>
          ) : <p><strong>Status:</strong> {attendanceResult.message}</p>
          }
        </div>
      )}
    </div>
  );
};

const renderContent = (content) => {
  if (typeof content === 'string' || typeof content === 'number') {
    return content;
  }
  if (typeof content === 'object' && content !== null) {
    return <pre>{JSON.stringify(content, null, 2)}</pre>;
  }
  return null;
};

const buttonStyle = {
  padding: '10px 20px',
  backgroundColor: '#007bff',
  borderWidth: 0,
  borderStyle: 'none',
  color: 'white',
  fontWeight: 'bold',
  borderRadius: '5px',
  cursor: 'pointer',
};

export default CameraCapture;

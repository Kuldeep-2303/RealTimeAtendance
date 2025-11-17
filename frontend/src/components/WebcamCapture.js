import React, { useState, useRef, useEffect } from 'react';
import axios from "axios";

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
    }, 'image/jpeg', 0.95);
  });
};

const cameraStyles = {
  container: { textAlign: 'center', padding: '20px' },
  video: {
    width: '100%',
    maxWidth: '500px',
    border: '1px solid #ccc',
    borderRadius: '10px',
    marginBottom: '1rem',
  },
  buttonContainer: { marginTop: '20px' },
  button: { marginRight: '10px', padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' },
  error: { color: 'red', marginTop: '20px' },
  resultContainer: { marginTop: '20px' },
  resultHeading: { fontSize: '1.5em', fontWeight: 'bold', marginBottom: '10px' },
  resultText: { fontSize: '1.1em', marginBottom: '5px' },
  attendanceContainer: { marginTop: '20px' },
  attendanceHeading: { fontSize: '1.5em', fontWeight: 'bold', marginBottom: '10px' },
  attendanceSubText: { fontSize: '1.1em', marginBottom: '5px' },
  attendanceText: { fontSize: '1.1em', marginBottom: '5px' },
};

const WebcamCapture = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [attendanceResult, setAttendanceResult] = useState(null);

  useEffect(() => {
    const startWebcam = async () => {
      if (stream) return;
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
        setStream(mediaStream);
      } catch (err) {
        console.error('Error accessing webcam:', err);
        setError('Could not access webcam. Please allow webcam permissions and try again.');
      }
    };

    startWebcam();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const captureFrame = async () => {
    setError("");
    setAttendanceResult(null);
    setLoading(true);

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || !stream) {
      setError("Webcam is not ready.");
      setLoading(false);
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);

    try {
      const blob = await getCanvasBlob(canvas);

      const formData = new FormData();
      formData.append('file', blob, 'attendance_capture.jpg');

      // Fallback to an empty string if the environment variable is not set
      const apiUrl = process.env.REACT_APP_API_URL || '';
      const response = await axios.post(`${apiUrl}/mark-attendance`, formData);
      setAttendanceResult(response.data);

    } catch (err) {
      // Log the full error to the console for debugging
      console.error("Error marking attendance:", err);
      // Set a user-friendly error message from the backend response
      setError("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={cameraStyles.container}>
      <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap' }}>
        <video ref={videoRef} style={cameraStyles.video} autoPlay muted />
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>
      <div style={cameraStyles.buttonContainer}>
        <button onClick={captureFrame} style={cameraStyles.button} disabled={!stream || loading}>
          {loading ? 'Processing...' : 'Mark Attendance'}
        </button>
      </div>
      {error && <p style={cameraStyles.error}>{renderContent(error)}</p>}
      {attendanceResult && (
        <div style={cameraStyles.attendanceContainer}>
          <h2 style={cameraStyles.attendanceHeading}>Attendance Status</h2>
          {attendanceResult.name ? (
            <div>
              <p style={{ ...cameraStyles.attendanceText, color: 'green', fontWeight: 'bold' }}>
                Attendance marked for: {attendanceResult.name}
              </p>
              <p style={cameraStyles.attendanceSubText}>
                Timestamp: {new Date(attendanceResult.timestamp).toLocaleString()}
              </p>
              <p style={cameraStyles.attendanceSubText}>Emotion: {attendanceResult.emotion}</p>
            </div>
          ) : <p style={cameraStyles.attendanceText}>{renderContent(attendanceResult.message)}</p>}
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

export default WebcamCapture;

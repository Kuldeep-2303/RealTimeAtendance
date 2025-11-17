import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

// Helper function to convert canvas.toBlob into a Promise
const getCanvasBlob = (canvas) => {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error('Canvas is empty'));
      }
    }, 'image/jpeg', 0.95);
  });
};

const WebcamUploader = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadResponse, setUploadResponse] = useState(null);

  // 1. Initialize webcam stream
  useEffect(() => {
    let mediaStream;
    const startWebcam = async () => {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (err) {
        console.error("Error accessing webcam:", err);
        setError("Could not access webcam. Please grant permission and refresh.");
      }
    };
    startWebcam();

    // 2. Cleanup stream on unmount
    return () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Capture frame & upload
  const handleCaptureAndUpload = async (event) => {
    event.preventDefault(); // Prevent default form submission behavior
    if (!videoRef.current || !canvasRef.current || !stream) {
      setError("Webcam components are not ready.");
      return;
    }

    setLoading(true);
    setError(null);
    setUploadResponse(null);

    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    try {
      const blob = await getCanvasBlob(canvas);

      const formData = new FormData();
      formData.append('file', blob, 'webcam-capture.jpg');

      // Use environment variable for the API URL for consistency
      const apiUrl = process.env.REACT_APP_API_URL || '';
      const response = await axios.post(`${apiUrl}/api/upload-image`, formData);

      setUploadResponse(response.data);
      console.log("Upload successful:", response.data);
    } catch (err) {
      console.error("Upload failed:", err);
      const errorMessage = err.response?.data?.detail || "An error occurred during the upload.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', fontFamily: 'sans-serif' }}>
      <h2>Webcam Image Uploader</h2>
      <div style={{ position: 'relative', width: '640px', margin: '0 auto' }}>
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          style={{
            width: "100%",
            borderRadius: "8px",
            borderWidth: "2px",
            borderStyle: "solid",
            borderColor: "#ddd",
          }}
        />
        {!stream && <p>Requesting webcam access...</p>}
      </div>

      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <button
        type="button" // Explicitly set type to prevent form submission
        onClick={handleCaptureAndUpload}
        disabled={!stream || loading}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          cursor: 'pointer',
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
        borderWidth: 0,
        borderStyle: 'none',
          borderRadius: '5px',
          margin: '20px 0',
        }}
      >
        {loading ? 'Uploading...' : 'Capture & Upload Image'}
      </button>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {uploadResponse && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#e8f5e9', borderRadius: '5px' }}>
          <p style={{ color: 'green', fontWeight: 'bold' }}>Upload Successful!</p>
          <pre style={{ textAlign: 'left', display: 'inline-block' }}>
            {JSON.stringify(uploadResponse, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default WebcamUploader;

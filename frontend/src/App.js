import React, { useState } from "react";
import CameraCapture from "./components/CameraCapture";
import WebcamUploader from "./components/WebcamUploader";
import RegisterForm from "./components/RegisterFrom";


const appStyle = {
  container: {
    maxWidth: 800,
    margin: "40px auto",
    padding: 20,
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    textAlign: "center",
  },
  heading: {
    fontSize: "2.5rem",
    fontWeight: "bold",
    color: "#222",
    marginBottom: 30,
  },
  nav: {
    marginBottom: "2rem",
    borderBottom: "2px solid #eee",
    paddingBottom: "1rem",
  },
  button: {
    padding: "10px 20px",
    margin: "0 10px",
    fontSize: "1rem",
    cursor: "pointer",
    border: "1px solid #ccc",
    borderRadius: "5px",
    backgroundColor: "white",
    transition: "all 0.2s ease-in-out",
  },
  activeButton: {
    backgroundColor: "#007bff",
    color: "white",
    borderColor: "#007bff",
  },
};

function App() {
  const [activeComponent, setActiveComponent] = useState("recognize");

  return (
    <div style={appStyle.container}>
      <h1 style={appStyle.heading}>Smart Attendance System</h1>
      <nav style={appStyle.nav}>
        <button
          style={{
            ...appStyle.button,
            ...(activeComponent === "recognize" ? appStyle.activeButton : {}),
          }}
          onClick={() => setActiveComponent("recognize")}
        >
          Recognize Face
        </button>
        <button
          style={{
            ...appStyle.button,
            ...(activeComponent === "upload" ? appStyle.activeButton : {}),
          }}
          onClick={() => setActiveComponent("upload")}
        >
          Upload Image
        </button>
        <button
          style={{
            ...appStyle.button,
            ...(activeComponent === "register" ? appStyle.activeButton : {}),
          }}
          onClick={() => setActiveComponent("register")}
        >
          Register User
        </button>
      </nav>

      {activeComponent === "recognize" && <CameraCapture />}
      {activeComponent === "upload" && <WebcamUploader />}
      {activeComponent === "register" && <RegisterForm />}
    </div>
  );
}

export default App;

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// React 18 strict mode with createRoot API
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

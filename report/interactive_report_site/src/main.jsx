import React from 'react';
import { createRoot } from 'react-dom/client';
import ReportApp from './ReportApp';
import './index.css';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ReportApp />
  </React.StrictMode>
);

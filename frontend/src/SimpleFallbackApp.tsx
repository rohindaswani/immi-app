import React from 'react';

const SimpleFallbackApp: React.FC = () => {
  return (
    <div style={{
      padding: '40px',
      maxWidth: '800px',
      margin: '40px auto',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      borderRadius: '8px',
      backgroundColor: 'white'
    }}>
      <h1 style={{ color: '#1976d2' }}>Immigration Advisor App</h1>
      
      <p>
        Welcome to the Immigration Advisor application. This is a simple fallback
        page to ensure the React application is running properly.
      </p>
      
      <div style={{
        padding: '20px',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>Debug Information</h2>
        <ul>
          <li>React is loading correctly</li>
          <li>This component is rendering successfully</li>
        </ul>
      </div>
      
      <div style={{ marginTop: '40px' }}>
        <button 
          onClick={() => window.location.href = '/'}
          style={{
            padding: '10px 20px',
            backgroundColor: '#1976d2',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginRight: '10px'
          }}
        >
          Go to Home
        </button>
        
        <button 
          onClick={() => window.location.href = '/login'}
          style={{
            padding: '10px 20px',
            backgroundColor: '#2e7d32',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Go to Login
        </button>
      </div>
    </div>
  );
};

export default SimpleFallbackApp;
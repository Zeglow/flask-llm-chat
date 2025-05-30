import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Chat from './pages/Chat';
import History from './pages/History';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-sky-50">
      <div className="container mx-auto px-4 py-8">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </BrowserRouter>
      </div>
    </div>
  );
}

export default App
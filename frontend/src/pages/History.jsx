import { useEffect, useState } from 'react';
import axios from '../api/axios';

function History() {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const fetchHistory = async () => {
            const res = await axios.get('/api/history');
            setHistory(res.data);
        };
        fetchHistory();
    }, []);

    return (
      <div>
        <h2>Conversation History</h2>
        {history.length === 0 ? <p>No history</p> : (
          history.map((item, index) => (
            <div key={index}>
                <strong>You:</strong> {item.prompt}<br />
                <strong>GPT:</strong> {item.response}<br />
                <small>{item.timestamp}</small>
                <hr />
            </div>
        ))
      )}
    </div>
    );
}

export default History;
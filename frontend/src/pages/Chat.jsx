import { useState } from 'react';
import axios from '../api/axios';

function Chat(){
    const [input, setInput] = useState('');
    const [response, setResponse] = useState('');
    const [history, setHistory] = useState([]);

    const handleChat = async () => {
        try {
            const res = await axios.post('/chat', { prompt: input});
            setResponse(res.data.resonse);
            setHistory([{ prompt: input, response: res.data.response }, ...history]);
            setInput('');
        }catch(err){
            setResponse('Error sending message');
        }
    };

    return (
      <div>
        <h2>Chat</h2>
        <textarea value={input} onChange={(e) => setInput(e.target.value)} />
        <button onClick={handleChat}>Send</button>
        <h3>GPT Response</h3>
        <p>{response}</p>
        <hr />
        <h3>History(this session)</h3>
        {history.map((item,index) =>(
            <div key={index}>
                <strong>You:</strong>{item.prompt}<br />
                <strong>GPT:</strong>{items.response}
            </div>
        ))}
      </div>

    );
}

export default Chat;
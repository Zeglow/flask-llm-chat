import { useEffect, useState } from 'react';
import axios from '../api/axios';

function History() {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const fetchHistory = async () => {
            const res = await axios.get('/history');
            setHistory(res.data);
        };
        
    }

    );
}
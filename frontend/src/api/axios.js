import axios from 'axios';

const instance = axios.create({
    baseURL: 'http://localhost:5001',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Add request interceptor
instance.interceptors.request.use(
    config => {
        // You can add any request modifications here
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// Add response interceptor
instance.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export default instance;

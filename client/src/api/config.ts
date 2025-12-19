// API Configuration
export const API_CONFIG = {
    BASE_URL: typeof window !== 'undefined' && window.location.hostname === 'localhost'
        ? 'https://bearcart.onrender.com'
        : 'https://bearcart.onrender.com',

    ENDPOINTS: {
    },

    DEFAULT_HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
};

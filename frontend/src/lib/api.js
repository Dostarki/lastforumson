import axios from 'axios';

export const api = axios.create({ baseURL: `${process.env.REACT_APP_BACKEND_URL}/api`, timeout: 15000 });
export const errorMessage = (error) => {
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail[0]?.msg?.replace('Value error, ', '') || 'Please check your details.';
  return 'The signal was interrupted. Please try again.';
};
export const numberLabel = (number) => number ? `#${String(number).padStart(5, '0')}` : '#-----';
// The backend builds the full composer URL: share text + the like link only.
export const shareUrl = (config) => config.share_url;
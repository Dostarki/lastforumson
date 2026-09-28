import axios from 'axios';

export const api = axios.create({ baseURL: `${process.env.REACT_APP_BACKEND_URL}/api`, timeout: 15000 });
export const errorMessage = (error) => {
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail[0]?.msg?.replace('Value error, ', '') || 'Please check your details.';
  return 'The signal was interrupted. Please try again.';
};
export const numberLabel = (number) => number ? `#${String(number).padStart(5, '0')}` : '#-----';
export const shareUrl = (config, agent) => {
  const url = new URL(config.share_url);
  url.searchParams.set('text', `${config.share_text}\n\n${config.public_url}/agent/${agent.ref_code}\n\n${config.public_url}/?ref=${agent.ref_code}`);
  return url.toString();
};
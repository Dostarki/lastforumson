import axios from 'axios';

export const adminApi = axios.create({
  baseURL: `${process.env.REACT_APP_BACKEND_URL}/api/admin`,
  timeout: 15000,
  withCredentials: true,
});

// Tokens are HttpOnly cookies, never stored in browser storage or React state.
export const adminRequest = async (method, url, data) => {
  try { return await adminApi.request({ method, url, data }); }
  catch (error) {
    if (error.response?.status !== 401) throw error;
    await adminApi.post('/refresh');
    return adminApi.request({ method, url, data });
  }
};

export const adminError = (error) => {
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    if (detail.some(item => item.type === 'string_too_short')) return 'Tüm alanları doldurun; yalnızca boşluk kullanılamaz.';
    return detail[0]?.msg?.replace('Value error, ', '') || 'Lütfen girdiğiniz bilgileri kontrol edin.';
  }
  return 'Sunucuya ulaşılamadı. Değişiklikler kaydedilmedi; lütfen tekrar deneyin.';
};
const API_BASE = process.env.REACT_APP_API_URL;

export const checkToken = () =>
  fetch(`${API_BASE}/token`).then(res => res.status === 200);

export const loginUrl = () => `${API_BASE}/login`;

export const logout = () =>
  fetch(`${API_BASE}/logout`, { method: "POST" });

export const uploadVideo = (formData) =>
  fetch(`${API_BASE}/upload_video`, {
    method: "POST",
    body: formData
  }).then(res => res.json());

export const triggerProcessing = () =>
  fetch(`${API_BASE}/process_latest`, {
    method: "POST"
  }).then(res => res.json());

export const pollStatus = () =>
  fetch(`${API_BASE}/status_check`).then(res => res.json());

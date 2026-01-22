import axios from 'axios';

const API = 'http://localhost:8000/api';

export const uploadDocuments = async (files, docType) => {
  const form = new FormData();
  files.forEach(f => form.append('documents', f));
  form.append('documentType', docType);
  return (await axios.post(`${API}/upload-documents`, form)).data;
};

export const uploadForm = async (file) => {
  const form = new FormData();
  form.append('form', file);
  return (await axios.post(`${API}/upload-form`, form)).data;
};

export const fillPDF = async (path, data) => {
  return (await axios.post(`${API}/fill-pdf`, { formPath: path, data })).data;
};

export const fillURL = async (url, data) => {
  return (await axios.post(`${API}/fill-url`, { url, data })).data;
};

export const getSampleForms = async () => {
  return (await axios.get(`${API}/sample-forms`)).data;
};
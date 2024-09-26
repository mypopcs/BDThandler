import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export async function analyzeData({ data, config }) {
  try {
    const response = await axios.post(`${API_URL}/analyze`, { data, config });
    return response.data;
  } catch (error) {
    console.error('Error analyzing data:', error);
    throw error;
  }
}


export async function saveData(data) {
  try {
    const response = await axios.post(`${API_URL}/save`, { data });
    return response.data;
  } catch (error) {
    console.error('Error saving data:', error);
    throw error;
  }
}

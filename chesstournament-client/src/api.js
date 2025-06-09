import axios from 'axios';
import { ref } from 'vue';

const myURL = import.meta.env.VITE_DJANGOURL;

export async function getCurrentUser() {

  const token = localStorage.getItem('authToken');

  if (token) {
    const response = await axios.get(myURL + 'users/me/', {
      headers: {
        'Authorization': 'Token ' + token,
      }
    });
  
    return response.data;
  }
  
  return null;
}

export const tournaments = ref([]);
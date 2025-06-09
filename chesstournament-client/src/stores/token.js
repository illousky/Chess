import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const myURL = import.meta.env.VITE_DJANGOURL;

// guardar el authToken en el localStorage
export const useAuthStore = defineStore('auth', () => {
  const authToken = ref(localStorage.getItem('authToken') || null)

  function setAuthToken(token) {
    authToken.value = token
    localStorage.setItem('authToken', token)
  }
  
  function clearAuthToken() {
    authToken.value = null
    localStorage.removeItem('authToken')
  }
  
  const isAuthenticated = computed(() => {
    return authToken.value !== null
  });

  function getAuthToken() {
    return authToken.value
  }

  // me obliga a que sea async
  async function getCurrentUser() {
    const token = localStorage.getItem('authToken')
    if (token) {
      try{
        const response = await axios.get(myURL + 'users/me/', {
          headers: {
            'Authorization': 'Token ' + token,
          }
        });
        console.log('Current user:', response.data);
        return response.data;
      } catch (error) {
        console.error('Error fetching current user:', error);
        return null;
      }
    }else {
      return null;
    }
  }
  return { authToken, setAuthToken, clearAuthToken, isAuthenticated, getAuthToken, getCurrentUser }
})
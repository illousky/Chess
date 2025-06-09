<template>
  <div id="app" data-v-app>
    <!-- Modern navbar with glass effect -->
    <header class="glass-navbar">
      <div class="container">
        <RouterLink to="/" class="brand">
          <span class="logo-icon">♟</span>
          <span class="logo-text">Chess-T-DB</span>
        </RouterLink>
        
        <button class="mobile-menu-btn" @click="mobileMenuOpen = !mobileMenuOpen">
          <span></span><span></span><span></span>
        </button>
        
        <nav class="main-nav" :class="{ 'active': mobileMenuOpen }">
          <RouterLink to="/" class="nav-item" @click="mobileMenuOpen = false">
            Home
            <span class="nav-highlight"></span>
          </RouterLink>
          <RouterLink
            to="/login"
            class="nav-item"
            :class="{ disabled: authStore.isAuthenticated }"
            data-cy="login-cypress-test"
            @click="mobileMenuOpen = false"
          >
            Admin Log-In
            <span class="nav-highlight"></span>
          </RouterLink>
          <RouterLink
            to="/logout"
            class="nav-item"
            :class="{ disabled: !authStore.isAuthenticated }"
            data-cy="logout-cypress-test"
            @click="mobileMenuOpen = false"
          >
            Log-Out
            <span class="nav-highlight"></span>
          </RouterLink>
          <RouterLink to="/faq" class="nav-item" @click="mobileMenuOpen = false">
            FAQ
            <span class="nav-highlight"></span>
          </RouterLink>
        </nav>
      </div>
    </header>

    <!-- Main content with subtle pattern -->
    <main class="main-content">
      <div class="content-wrapper">
        <RouterView v-slot="{ Component }">
          <component 
            :is="Component" 
            :tournaments="tournaments"
            :torneos-buscados="torneosBuscados"
            @searchTournament="searchTournament"
            @create-tournament="createTournament" 
          />
        </RouterView>
      </div>
    </main>

    <footer class="modern-footer">
      <div class="container">
        <p>© Copyright: I. Vidal e I. Gonzalez</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
  import { RouterLink, RouterView } from 'vue-router'
  import {ref, onMounted} from 'vue';
  import { useAuthStore } from '@/stores/token.js';
  import { useRouter, useRoute } from 'vue-router';
  import { tournaments } from '@/api.js';

  const router = useRouter();
  const route = useRoute();
  defineOptions({
    name: 'App'
  });

  const mobileMenuOpen = ref(false);
  const torneosBuscados = ref([]);
  const myURL = import.meta.env.VITE_DJANGOURL;
  const authStore = useAuthStore();

  const listadoTorneos = async () => {
    try {
      let allTournaments = [];
      let page = 1;
      let moreDataAvailable = true;

      while (moreDataAvailable) {
        const response = await fetch(`${myURL}tournaments/?page=${page}`);
        const data = await response.json();
        
        allTournaments = [...allTournaments, ...data.results];

        moreDataAvailable = data.next !== null;
        page++;
      }

      tournaments.value = allTournaments;

    } catch (error) {
      console.error(error);
    }
  };

  const searchTournament = async (nombre) => {
    try {
      const response = await fetch(myURL + 'searchTournaments/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ search_string: nombre }),
      });

      const data = await response.json();
      torneosBuscados.value = data;
      console.log('Torneos encontrados:', torneosBuscados.value);
    } catch (error) {
      console.error(error);
    }
  };

  onMounted(() => {
    listadoTorneos();
  });
  
</script>

<style scoped>
  @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

  :root {
    --primary: #3a6ea5;
    --accent: #ff6b6b;
    --text: #333;
    --text-light: #6c757d;
    --bg-light: #f8f9fa;
    --card-bg: #ffffff;
    --nav-bg: rgba(255, 255, 255, 0.8);
    --footer-bg: #004e92;
    --gradient-start: #004e92;
    --gradient-end: #000428;
    --border-radius: 12px;
    --spacing: 1rem;
    --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body, html {
    width: 100%;
    height: 100%;
    font-family: 'Quicksand', sans-serif;
    background-color: var(--bg-light);
    color: var(--text);
    overflow-x: hidden;
  }

  #app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    width: 100%;
    background-image: 
      radial-gradient(#e3e3e3 1px, transparent 1px),
      radial-gradient(#e3e3e3 1px, transparent 1px);
    background-size: 30px 30px;
    background-position: 0 0, 15px 15px;
  }

  .container {
    width: 100%;
    max-width: 1400px;
    min-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing);
  }

  .glass-navbar {
    position: sticky;
    top: 0;
    width: 100%;
    z-index: 1000;
    backdrop-filter: blur(10px);
    background-color: var(--nav-bg);
    box-shadow: var(--shadow);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }

  .glass-navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 70px;
  }

  .brand {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: var(--primary);
    font-weight: 700;
    font-size: 1.5rem;
  }

  .logo-icon {
    font-size: 1.8rem;
    margin-right: 10px;
  }

  .mobile-menu-btn {
    display: none;
  }

  .main-nav {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .nav-item {
    position: relative;
    padding: 0.5rem 1.2rem;
    color: var(--text);
    text-decoration: none;
    font-weight: 600;
    font-size: 1rem;
    transition: color 0.3s ease;
    overflow: hidden;
  }

  .nav-item:hover {
    color: var(--accent);
  }

  .nav-highlight {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background-color: var(--accent);
    transform: scaleX(0);
    transform-origin: center;
    transition: transform 0.3s ease;
  }

  .nav-item:hover .nav-highlight,
  .nav-item.router-link-active .nav-highlight {
    transform: scaleX(1);
  }

  .nav-item.disabled {
    color: var(--text-light);
    pointer-events: none;
    opacity: 0.6;
  }

  .main-content {
    flex: 1;
    width: 100%;
    padding: var(--spacing) 0;
  }

  .content-wrapper {
    background-color: var(--card-bg);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    padding: calc(var(--spacing) * 2);
    margin: 0 auto;
    width: 90%;
    min-width: 1200px;
    max-width: 1600px;
  }

  .modern-footer {
    background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
    color: rgb(17, 85, 231);
    padding: calc(var(--spacing) * 1.5) 0;
    text-align: center;
    width: 100%;
  }

  @media (max-width: 1200px) {
    .container, .content-wrapper {
      min-width: 900px;
      width: 95%;
    }
  }

  @media (max-width: 992px) {
    .container, .content-wrapper {
      min-width: 768px;
      width: 95%;
    }
  }

  @media (max-width: 768px) {
    .glass-navbar .container {
      padding-top: 1rem;
      padding-bottom: 1rem;
      height: auto;
      flex-wrap: wrap;
      min-width: auto;
    }
    
    .mobile-menu-btn {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      width: 30px;
      height: 21px;
      background: transparent;
      border: none;
      cursor: pointer;
    }
    
    .mobile-menu-btn span {
      display: block;
      width: 100%;
      height: 3px;
      background-color: var(--primary);
      border-radius: 3px;
      transition: all 0.3s ease;
    }
    
    .main-nav {
      flex-direction: column;
      width: 100%;
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.5s ease;
      align-items: flex-start;
      margin-top: 1rem;
    }
    
    .main-nav.active {
      max-height: 300px;
    }
    
    .nav-item {
      width: 100%;
      padding: 1rem 0;
    }
    
    .content-wrapper {
      width: 100%;
      min-width: auto;
      border-radius: 0;
      box-shadow: none;
    }
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .content-wrapper {
    animation: fadeIn 0.5s ease-out;
  }
</style>
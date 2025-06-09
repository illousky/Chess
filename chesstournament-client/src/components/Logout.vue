<template>
  <div class="container my-4" data-cy="logoutPage">
      <div class="py-5"></div>
      <div class="vertical-center text-center">
          <div class="container">
              <div class="row">
                  <div class="col-md-3"></div>
                  <div class="col-md-6 shadow p-3 mb-5 bg-white rounded align-middle">
                      <h2>Log Out</h2>
                      <div>You will be redirected to home in 5 seconds</div>
                  </div>
              </div>
          </div>
      </div>
      <div class="py-2"></div>
  </div>
</template>
    
<script setup>

  import { onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '@/stores/token.js';
  const router = useRouter();
  const authStore = useAuthStore();
  const myURL = import.meta.env.VITE_DJANGOURL;

  onMounted(async () => {

    const user = await authStore.getCurrentUser();

    if (!user){
      alert('You have to be loged to logout');
      router.push({ name: 'Home' })
    }

    setTimeout(() => {
      router.push('/');
    }, 5000);

    if (authStore.isAuthenticated) {
      const token = authStore.getAuthToken();

      try {
        const response = await fetch(myURL + 'token/logout/', {
          method: 'POST',
          headers: {
            'Authorization': 'Token ' + token,
          },
        });

        if (response.ok) {
          console.log('Logout successful');
          authStore.clearAuthToken();
        } else {
          console.error('Logout failed');
        }
      } catch (error) {
        console.error('Error during logout:', error);
      }
    } else {
      console.log('User is not logged in');
    }

  });

</script>

<style scoped>

  .vertical-center {
    min-height: 60vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .col-md-6.shadow {
    background-color: #ffffff;
    border-radius: 1.5rem;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
  }

  .col-md-6.shadow {
    animation: fadeInScale 0.6s ease-in-out;
  }

  @keyframes fadeInScale {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

</style>
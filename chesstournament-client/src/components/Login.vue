<template>
    <div class="container my-4">
        <div class="py-5"></div>
        <form @submit.prevent="submitForm">
            <div data-v-45f5edd7 class="vertical-center text-center">
                <div data-v-45f5edd7 class="container">
                    <div data-v-45f5edd7 class="row">
                        <div data-v-45f5edd7 class="col-md-3"></div>
                        <div data-v-45f5edd7 class="col-md-6 shadow p-3 mb-5 bg-white rounded align-middle">
                            <h2 data-v-45f5edd7>Login</h2>
                                <div v-if="loginError">
                                    <p style="color:rgba(255,0,0,0.5);" data-cy="error-message">Error: Invalid username or password</p>     
                                </div>
                                <div data-v-45f5edd7 class="mb-3">
                                    <input 
                                        data-v-45f5edd7 
                                        v-model="user.username"
                                        @input="error = false"
                                        :class="{'is-invalid': error && nombreInvalid}"
                                        name="user.username" 
                                        type="text" 
                                        placeholder="username" 
                                        required 
                                        autofocus 
                                        data-cy="username" 
                                        class="form-control rounded-pill border-0 shadow-sm px-4">
                                </div>
                                <div data-v-45f5edd7 class="mb-3">
                                    <input 
                                        data-v-45f5edd7 
                                        v-model="user.password"
                                        @input="error = false"
                                        :class="{'is-invalid': error && passwordInvalid}"
                                        name="user.password" 
                                        type="password" 
                                        placeholder="Password" 
                                        required 
                                        data-cy="password" 
                                        class="form-control rounded-pill border-0 shadow-sm px-4 text-primary">
                                </div>
                                <div data-v-45f5edd7 class="d-grid gap-2 mt-2">
                                    <button data-v-45f5edd7 
                                        type="submit" 
                                        data-cy="login-button" 
                                        class="btn btn-primary btn-block text-uppercase mb-2 rounded-pill shadow-sm">LOG in</button>
                                </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        <div class="py-2"></div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/token.js';

const router = useRouter();
const myURL = import.meta.env.VITE_DJANGOURL;

const error = ref(false);
const loginError = ref(false);

const user = ref({
    username: '',
    password: ''
});

const nombreInvalid = computed(() => user.value.username.length < 1);
const passwordInvalid = computed(() => user.value.password.length < 1);

const login = async (username, password) => {
    resetEstado();

    if (!username || !password) {
        loginError.value = true;
        error.value = true;
        return;
    }

    try {
        const response = await fetch(myURL + 'token/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
            headers: { 'Content-Type': 'application/json; charset=UTF-8' },
        });

        if (!response.ok) {
            loginError.value = true;
            const errorText = await response.text();
            console.error('Error en la respuesta del servidor:', errorText);
            throw new Error('Login incorrecto.');
        }

        const data = await response.json();
        console.log('Token recibido:', data.auth_token);
        useAuthStore().setAuthToken(data.auth_token);

        router.push({ name: 'Home' });

    } catch (error) {
        loginError.value = true;
        console.error(error);
    }
};

const submitForm = () => {
    login(user.value.username, user.value.password);
};

const resetEstado = () => {
    error.value = false;
    loginError.value = false;
};
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

    .form-control:focus {
    border-color: #86b7fe;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
    transition: all 0.2s ease-in-out;
    }

    button.btn-primary {
    background-color: #0d6efd;
    border-color: #0d6efd;
    transition: background-color 0.3s ease, transform 0.2s ease;
    }

    button.btn-primary:hover {
    background-color: #0b5ed7;
    transform: scale(1.02);
    }

    p[data-cy="error-message"] {
    font-weight: bold;
    margin-top: 0.5rem;
    }

</style>

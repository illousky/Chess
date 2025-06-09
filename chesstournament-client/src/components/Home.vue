<template>
  <div class="container my-4 mt-5">
    <div class="p-2 mb-4 bg-body-tertiary rounded-3">
      <div class="col-md-12 fs-5 btn-outline-light">
        <div data-cy="player-log">
          <div v-if="!isAdmin">
            <p>
              Welcome to the Chess Tournament Database. This database features the
              unique ability for players to update the results of their games. To create
              tournaments, an administrative account is required. However, any player can
              enter the result of a game.
            </p>
            <p>
              You can use the search button to find tournaments by name. For further
              information, please refer to the <RouterLink to="/faq">FAQ</RouterLink> section.
            </p>
          </div>
          <div v-else data-cy="admin-log">
            <p>
              Hello, you are logged in as an administrator. Remember, with great power comes great responsibility.
            </p>
            <p>
              As an administrator, you can create tournaments and edit or update the results of games, rounds
              and tournaments.
            </p>
            <p>
              To create a new tournament, press the <strong>"Create Tournament"</strong> button. To edit or update
              games, rounds or tournaments, select the desired tournament.
            </p>
            <div class="button text-center mb-3">
              <RouterLink to="/createtournament" class="btn btn-primary" data-cy="create-Tournament-button">Create Tournament</RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-5 align-items-md-stretch">
      <div class="col-md-6">
        <div class="h-100 p-2 bg-white rounded-3 shadow-lg">
          <h3 class="text-primary">Tournaments</h3>
          <table class="table table-striped table-hover table-sm">
            <thead>
              <tr>
                <th>Name</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tournament in paginatedTournaments" :key="tournament.id">
                <td>
                  <RouterLink :to="'/tournamentdetail/' + tournament.id + '/' + tournament.name + '/' + tournament.board_type + '/' + tournament.tournament_type" :data-cy="tournament.name">{{ tournament.name }}</RouterLink>
                </td>
                <td>{{ dayjs(tournament.start_date).format('YYYY-MM-DD') }}</td>
              </tr>
            </tbody>
          </table>
          <div class="pagination">
            <button @click="previousPage" :disabled="currentPage === 1" class="btn btn-outline-primary mr-4" data-cy="previous-button">Previous</button>
            <button @click="nextPage" :disabled="currentPage * itemsPerPage >= tournaments.length" class="btn btn-outline-primary" data-cy="next-button">Next</button>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="h-100 p-2 bg-light border rounded-3 shadow-lg">
          <form class="d-flex" role="search" @submit.prevent="searchTournament">
            <input placeholder="Tournament" ref="nombre" v-model="torneo.nombre" type="text" class="form-control" data-cy="input-search" :class="{'is-invalid': mostrarErrores && nombreInvalido}"/>
            <button class="btn btn-outline-success" type="submit" data-cy="submit-search">Search</button>
          </form>
          <div class="py-2"></div>
          <table class="table table-striped table-hover table-sm">
            <thead>
              <tr>
                <th>Name</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tournament in torneosBuscados" :key="tournament.id">
                <td>
                  <RouterLink :to="'/tournamentdetail/' + tournament.id + '/' + tournament.name + '/' + tournament.board_type + '/' + tournament.tournament_type" :data-cy="`search-${tournament.name}`">{{ tournament.name }}</RouterLink>
                </td>
                <td>{{ dayjs(tournament.start_date).format('YYYY-MM-DD') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import dayjs from 'dayjs';
  import { onMounted } from 'vue';
  import { ref, computed } from 'vue';
  import { useAuthStore } from '@/stores/token.js';
  import { tournaments } from '@/api.js';
  import { RouterLink } from 'vue-router';

  const nombreInvalido = computed(() => torneo.value.nombre.length < 1);
  const nombre = ref(null);
  const mostrarErrores = ref(false);
  const isAdmin = ref(false);

  const currentPage = ref(1);
  const itemsPerPage = ref(5);

  defineOptions({
    name: 'Home',
  });

  onMounted(async () => {

    try {
      const user = await useAuthStore().getCurrentUser();
      console.log(user);

      if (useAuthStore().isAuthenticated) {
        console.log(user);
        isAdmin.value = user.is_staff || user.is_superuser;
      } else {
        isAdmin.value = false;
      }

    } catch (error) {
      console.error('Error al obtener el usuario:', error);
    }

  });

  const props = defineProps({
    tournaments: {type: Array, default: () => []},
    paginatedTournaments: {type: Array, default: () => []},
    torneosBuscados: {type: Array, default: () => []},
  });

  const torneo = ref({
    nombre: '',
  });

  const emit = defineEmits(['searchTournament']);

  const searchTournament = () => {
    if (nombreInvalido.value) {
      mostrarErrores.value = true;
      return;
    }

    mostrarErrores.value = false;
    emit('searchTournament', torneo.value.nombre);
  };

  const paginatedTournaments = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value;
    const end = start + itemsPerPage.value;
    return props.tournaments.slice(start, end);
  });

  const nextPage = () => {
    if (currentPage.value * itemsPerPage.value < props.tournaments.length) {
      currentPage.value++;
    }
  };

  const previousPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--;
    }
  };
</script>

<style scoped>
  .container {
    width: 100%;
    padding: 0;
    margin: 0;
  }

  .row {
    margin: 0;
  }

  .col-md-6 {
    padding: 10px;
  }

  .table {
    background-color: var(--card-bg);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
  }

  .pagination {
    display: flex;
    justify-content: center;
    gap: 10px;
  }

  .pagination button {
    background-color: var(--bg-light);
    color: var(--text-dark);
    border-radius: var(--border-radius);
    border: 1px solid var(--primary);
    padding: 5px 15px;
    transition: background-color 0.3s ease, transform 0.3s ease;
  }

  /* Efecto de hover */
  .pagination button:hover {
    background-color: var(--primary);
    color: rgb(17, 85, 231);
    transform: scale(1.1);
  }

  .pagination button:disabled {
    background-color: var(--text-light);
    color: var(--bg-light);
    cursor: not-allowed;
    border: 1px solid var(--text-light);
  }

  .btn-outline-primary {
    border-color: var(--primary);
    color: var(--primary);
  }

  .btn-outline-primary:hover {
    background-color: var(--primary);
    color: white;
  }

  .btn-outline-success {
    border-color: var(--accent);
    color: var(--accent);
  }

  .btn-outline-success:hover {
    background-color: var(--accent);
    color: white;
  }
</style>



<template>
    <div class="container mt-5">
        <h1 class="text-center">Create Tournament</h1>
        <form @submit.prevent="submitForm">
            <div class="mb-4 mt-4">
                <label for="name" class="form-label fw-bold">Tournament Name</label>
                <input type="tournament_name" placeholder='"My tournament name"' ref="tournamentName" v-model="tournament.name" class="form-control" data-cy="name-cypress-test"/> 
                <div class="form-text">Tournament full name</div>
            </div>

            <div class="mb-4 mt-4">
                <input class="form-check-input" type="checkbox" v-model="tournament.only_administrative" id="adminOnly" data-cy="only_administrative-cypress-test"/> 
                <label class="form-check-label fw-bold" for="adminOnly">Only administrator can update games</label>
                <div class="form-text">Set to false if user can update games. Otherwise only administrator can input the game results.</div>
            </div>

            <div class="mb-4 mt-4">
                <label for="Pairing System" class="form-label fw-bold">Pairing System</label>
                <select class="form-select" v-model="tournament.tournament_type" id="pairingSystem" data-cy="single_round_robin-cypress-test">
                    <option value="SR">Round Robin</option>
                    <option value="SW">Swiss</option>
                </select>
                <label class="form-text">Select the pairing system (swiss, round robin, etc)</label>
            </div>

            <div class="mb-4 mt-4">
                <label for="boardType" class="form-label fw-bold">Board Type</label>
                <select class="form-select" v-model="tournament.boardType" id="boardType" data-cy="boardtype-cypress-test">
                    <option value="LIC">Lichess</option>
                    <option value="OTB">OTB</option>
                </select>
            </div>

            <div class="row mt-4 mb-4 align-items-md-stretch">
                <div class="col-md-6">
                    <label for="Points" class="form-label fw-bold">Provide points awarded to player if:</label>
                    <div class="d-flex mt-2 mb-2 ms-5 align-items-md-stretch">
                        <label for="wins points" class="form-label mt-1">Points for win:</label>
                        <div class="col-4">
                            <input type="wins point" placeholder="1.0" v-model="tournament.win_points" ref="winsPoints" class="form-control ms-2 text-center" data-cy="wins-points"/>
                        </div>
                    </div>
                    <div class="d-flex mt-2 mb-2 ms-5 align-items-md-stretch">
                        <label for="draw points" class="form-label mt-1">Points for draw:</label>
                        <div class="col-4">
                            <input type="draw point" placeholder="0.5" v-model="tournament.draw_points" ref="drawPoints" class="form-control ms-2 text-center" data-cy="draw-points"/>
                        </div>
                    </div>
                    <div class="d-flex mt-2 mb-2 ms-5 align-items-md-stretch">
                        <label for="lose points" class="form-label mt-1">Points for lose:</label>
                        <div class="col-4">
                            <input type="lose point" placeholder="0.0" v-model="tournament.lose_points" ref="losePoints" class="form-control ms-2 text-center" data-cy="lose-points"/>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <label for="rankingMethod" class="form-label fw-bold">Ranking method used in the tournament</label>
                    <div class="form-text">Select ranking methods in the order in which should be applied</div>

                    <div v-for="method in rankingMethods" :key="method.value" class="form-check mt-2 mb-2 ms-5">
                        <input
                        class="form-check-input"
                        type="checkbox"
                        :id="method.id"
                        :value="method.value"
                        v-model="selectedRankingMethods"
                        />
                        <label class="form-check-label" :for="method.value">
                        {{ method.label }}
                        </label>
                    </div>
                </div>
            </div>

            <div class="mb-4 mt-4">
                <label for="Tournament category" class="form-label fw-bold">Tournament category (rapid, classical, etc)</label>
                <select class="form-select" v-model="tournament.category" id="tournamentCategory" data-cy="tournament_speed-cypress-test">
                    <option value="BL">Blitz</option>
                    <option value="BU">Bullet</option>
                    <option value="CL">Classical</option>
                    <option value="RA">Rapid</option>
                </select>
                <div class="form-text">Select the tournament category (blitz, bullet, classical, rapid)</div>
            </div>

            <div class="mb-4 mt-4">
                <label for="Players" class="form-label fw-bold">Players</label>
                <textarea type="text" id="input_9" placeholder="Introduce players using the CVS format (see FAQ for details). Do NOT add trailing spaces" v-model="tournament.players" ref="players" class="form-control" data-cy="players"/>
                <div class="form-text">List of players participating in the tournament</div>
            </div>

            <div v-if="tournamentPlayersInvalid" class="text-danger" data-cy="error-message">
                "Error: can not add players to tournament if the input does not start with 'name, email\n' or 'lichess_username\n'"
            </div>
            <div v-if="invalid_player" class="text-danger" data-cy="error-message">
                "Error: can not add players to tournament"
            </div>

            <div class="mb-4 mt-4">
                <button type="submit" class="btn btn-primary" data-cy="create-tournament">Create Tournament</button>
                <RouterLink to="/" type="cancel" class="btn btn-secondary ms-2" data-cy="cancel-tournament">Cancel</RouterLink>
            </div>
        </form>
    </div>
</template>

<script setup>

import { ref, computed, watch, reactive, onMounted } from 'vue';
import { useAuthStore } from '@/stores/token.js';
import { RouterLink, useRouter } from 'vue-router';
import { tournaments } from '@/api.js';

defineOptions({
  name: 'CreateTournamentComponent',
});

const emit = defineEmits(['create-tournament']);
const selectedRankingMethods = ref([]);
const authStore = useAuthStore();
const router = useRouter();
const isAdmin = ref(false);
const myURL = import.meta.env.VITE_DJANGOURL;
const invalid_player = ref(false);

onMounted(async () => {
  const user = await authStore.getCurrentUser();

  console.log("usuario llegante", user)

  if (user === null){
    alert('You have to be admin user to create a tournament');
    router.push({ name: 'Home' })
  }

  if (useAuthStore().isAuthenticated && user.is_superuser) {
    console.log(user);
    isAdmin.value = user.is_staff || user.is_superuser;
  } else {
    isAdmin.value = false;
    alert('You have to be admin user to create a tournament');
    router.push({ name: 'Home' })
  }
})

const rankingMethods = ref([
  { label: 'Buchholz (BU)', value: 'BU', id: 'ranking-option-bu' },
  { label: 'Buchholz cut 1 (BC)', value: 'BC', id: 'ranking-option-bc' },
  { label: 'Buchholz average (BA)', value: 'BA', id: 'ranking-option-ba' },
  { label: 'Sonneborn-Berger (SB)', value: 'SB', id: 'ranking-option-sb' },
  { label: 'Plain score (PS)', value: 'PS', id: 'ranking-option-ps' },
  { label: 'Wins (WI)', value: 'WI', id: 'ranking-option-wi' },
  { label: 'Black times (BT)', value: 'BT', id: 'ranking-option-bt' }
]);

const pairingSystemMapping = ref([
  { label: 'Round Robin', value: 'SR' },
  { label: 'Swiss', value: 'SW' }
]);

const boardTypeMapping = ref([
  { label: 'Lichess', value: 'LIC' },
  { label: 'OTB', value: 'OTB' }
]);

const tournament = ref({
  name: '',
  only_administrative: false,
  tournament_type: '',
  boardType: '',
  win_points: 1.0,
  draw_points: 0.5,
  lose_points: 0.0,
  rankingMethod: [],
  category: '',
  players: ''
});

watch(selectedRankingMethods, (newMethods) => {
  tournament.value.rankingMethod = newMethods;
});

console.log('Ranking methods:', rankingMethods.value);

const tournamentNameInvalid = computed(() => tournament.value.name.length < 1);
const tournamentpairingSystemInvalid = computed(() => tournament.value.tournament_type.length < 1);
const tournamentBoardTypeInvalid = computed(() => tournament.value.boardType.length < 1);
const tournamentWinsPointsInvalid = computed(() => tournament.value.win_points < 0);
const tournamentDrawPointsInvalid = computed(() => tournament.value.draw_points < 0);
const tournamentLosePointsInvalid = computed(() => tournament.value.lose_points < 0);
const tournamentRankingMethodInvalid = computed(() => tournament.value.rankingMethod.length < 1);
const tournamentCategoryInvalid = computed(() => tournament.value.category.length < 1);
const tournamentPlayersInvalid = ref(false);

const createTournament = async () => {
  console.log('Tournament data:', tournament.value);

  const isValidPlayersFormat =
    tournament.value.players.startsWith('name, email\n') ||
    tournament.value.players.startsWith('lichess_username\n');

  tournamentPlayersInvalid.value = !isValidPlayersFormat;

  if (tournamentPlayersInvalid.value) {
    return;
  }

  if (tournamentNameInvalid.value || tournamentpairingSystemInvalid.value || tournamentBoardTypeInvalid.value ||
      tournamentWinsPointsInvalid.value || tournamentDrawPointsInvalid.value || tournamentLosePointsInvalid.value ||
      tournamentRankingMethodInvalid.value || tournamentCategoryInvalid.value) {
    return;
  }

  const categoryMapping = {
    Bullet: 'BU',
    Blitz: 'BL',
    Classical: 'CL',
    Rapid: 'RA'
  };

  const adaptedTournament = {
    ...tournament.value,
    tournament_speed: tournament.value.category,
    board_type: tournament.value.boardType,
    rankingList: tournament.value.rankingMethod
  };

  console.log('Adapted Tournament:', adaptedTournament);

  try{
    const response = await fetch(myURL + 'tournament_create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${authStore.getAuthToken()}`,
        },
        body: JSON.stringify(adaptedTournament),
      });

      console.log('Response:', response);

      if (!response.ok) {
        if (response.status === 404){
          invalid_player.value = true;
        }
        throw new Error('Error al crear el torneo');
      }

      const data = await response.json();
      tournaments.value.push(data);

      const response2 = await fetch(myURL + 'create_round/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${authStore.getAuthToken()}`,
        },
        body: JSON.stringify({ tournament_id: data.id }),
      });
      if (!response2.ok) {
        throw new Error('Error al crear la ronda');
      }
      const data2 = await response2.json();
      console.log('Ronda creada:', data2);
      console.log('Torneo creado:', data);

      router.push({
        name: 'TournamentDetail',
        params: {
          id: data.id,
          name: data.name,
          boardType: data.board_type,
          tournamentType: data.tournament_type
        }
      });

  } catch (error) {
    console.error(error.message);
  }
  
};

const submitForm = () => {
  createTournament();
};

</script>


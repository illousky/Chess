<template>
  <div>
    <h1>Tournament: <i><B data-cy="tournament-title">{{tournamentName}}</B></i></h1>
    <div>
      <button type="button" class="btn btn-primary">Refresh page</button>
    </div>
    Click to expand
    <div class="accordion-container">
      <button class="accordion" :class="{ active: activePanel === 'standing' }" @click="togglePanel('standing')" data-cy="standing-accordion-button">Standing</button>
      <div v-if="activePanel === 'standing'" class="panel">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Name</th>
              <th>Score</th>
              <th>BT</th>
              <th>WI</th>
            </tr>
        </thead>
        <tbody>
          <tr v-for="(player, key) in ranking" :key="key" :data-cy="`ranking-${key+1}`">
            <td :data-cy="`ranking-${index + 1}-rank`">{{ player.rank }}</td>
            <td :data-cy="`ranking-${index + 1}-name`">{{ player.name }}</td>
            <td :data-cy="`ranking-${index + 1}-points`">{{ player.score }}</td>
            <td :data-cy="`ranking-${index + 1}-black`">{{ parseFloat(player['BT']).toFixed(2) }}</td>
            <td :data-cy="`ranking-${index + 1}-wins`">{{ parseFloat(player['WI']).toFixed(2) }}</td>
            <!-- <td v-for="system in tournamentRankingSystem" :key="system">
              <td v-if="system !== 'score'">
                {{ player[system] }}
              </td>
            </td> -->
          </tr>
        </tbody>
        </table>
      </div>
    </div>
    <div class="accordion-container">    
      <button class="accordion" :class="{ active: activePanel === 'results' }" @click="togglePanel('results')">Pairing/Results</button>
      <div v-if="activePanel === 'results'" class="panel">
        <div>
          <h2 v-if="isOTB">OTB</h2>
          <h2 v-else>LICHESS</h2>
          <div v-if="isOTB">The abbreviations used in the "result" column are explained at the end of the page.</div>
          <br>
          <div>Press UPDATE
            <i class="bi bi-arrow-right"></i>
            to update the game result. See the
            <RouterLink class="" to="/faq#collapseTwo">FAQ</RouterLink>
            for more information.
          </div>
          <br>
          <div v-for="(round, key2) in rounds" :key="key2" class="round-block">
            <h4 :data-cy="`round_${key2+1}`">round_00{{ key2+1 }}</h4>
            <table>
              <thead>
                <tr>
                  <th>Table</th>
                  <th>White</th>
                  <th>Result</th>
                  <th>Black</th>
                  <th v-if="isAdmin">Update Result (Admin)</th>
                  <th v-else>Update Result</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(game, key) in round.games" :key="key" index="key" :data-cy="`game_${key2+1}_${key+1}`">
                  <td>{{ key + 1 }}</td>
                  <td>{{ game.white_name ?? '-' }}</td>
                  <td v-if="isOTB"> 
                    <div v-if="game.result && game.result !== '*'" :data-cy="`input-${key2 + 1}-${key+1}`">
                      {{ formatResult(game.result) }}
                    </div>
                    <div v-else>
                      <div v-if="isAdmin" class="d-flex align-items-center">
                        <div class="input-group input-group-sm me-2">
                          <select v-model="newResult2[game.id]" class="col-md-8" :data-cy="`select-${key2 + 1}-${key+1}`">
                            <option v-for="result in posibleResults" :key="result.code" :value="result.code">{{ result.description }}</option>
                          </select>
                          <button class="btn btn-primary btn-sm px-2 py-1" @click="updateGameResultAdmin(game)" :data-cy="`button-${key2 + 1}-${key+1}`">Update</button>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td v-else>
                    <td v-if="licResult[game.id]" :data-cy="`input-${key2 + 1}-${key+1}`">
                      {{ formatResult(licResult[game.id]) }}
                    </td>
                    <td v-else>
                      <div class="d-flex align-items-center">
                        <input v-model="licID[game.id]" placeholder="Type game ID" class="form-control form-control-sm py-1" :data-cy="`input-${key2 + 1}-${key+1}`"/>
                        <button class="btn btn-primary btn-sm px-2 py-1" @click="searchLichessResult(game, licID[game.id])" :data-cy="`button-${key2 + 1}-${key+1}`">Search</button>
                      </div>
                    </td>
                  </td>
                  <td>{{ game.black_name ?? '-'}}</td>
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="input-group input-group-sm me-2">
                        <select v-if="isOTB || isAdmin" v-model="newResult[game.id]" :data-cy="`select-admin-${key2 + 1}-${key+1}`">
                          <option v-for="result in posibleResults" :key="result.code" :value="result.code">{{ result.description }}</option>
                        </select>
                        <div v-if="isAdmin">
                          <button @click="updateGameResultAdmin(game)" :data-cy="`button-admin-${key2 + 1}-${key+1}`">Update</button>
                        </div>
                        <div v-else-if="isOTB">
                          <button @click="updateGameResultOtb(game)" :data-cy="`button-admin-${key2 + 1}-${key+1}`">Update</button>
                        </div>
                        <div v-else>
                          <p>You can't update lichess game unless you are an admin user</p>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue';
import { RouterLink, useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/token.js';

const activePanel = ref('results')
const route = useRoute()
const tournamentId = route.params.id
const tournamentName = route.params.name
// puede ser OTB o LIC
const boardType = route.params.boardType
const tournamentType = route.params.tournamentType
const tournamentRankingSystem = ref({});
const myURL = import.meta.env.VITE_DJANGOURL
const ranking = ref([])
const players = ref([])
const isOTB = ref(false)
const rounds = ref([])
const isAdmin = ref(false);
const newResult = reactive({});
const newResult2 = reactive({});
const authStore = useAuthStore();
const licResult = reactive({});
const licID = ref({});
const router = useRouter();

const posibleResults = [
  { code: '0', description: 'Choose result'},
  { code: 'White wins (1-0)', description: 'White wins (1-0)' },
  { code: 'Black wins (0-1)', description: 'Black wins (0-1)' },
  { code: 'Draw (1/2-1/2)', description: 'Draw (1/2-1/2)' },
  { code: '*', description: 'Result Unknown (*)' }
]

onMounted(async () => {

  const user = await authStore.getCurrentUser();

  if (!user){
    alert('You have to be loged to view tournaments details');
    router.push({ name: 'Home' })
  }

  try {
    console.log('route params:', route.params)

    const response = await fetch(myURL+'get_players/'+tournamentId+'/')
    const response_ranking = await fetch(myURL+'get_ranking/'+tournamentId+'/')
    const user = await authStore.getCurrentUser();
    const response_tournament = await fetch(myURL+'searchTournaments/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        search_string: tournamentName,
      }),
    })

    if (authStore.isAuthenticated) {
      console.log("user", user);
      isAdmin.value = user.is_staff || user.is_superuser;
    } else {
      isAdmin.value = false;
    }

    console.log('route params:', route.params)
    console.log('tournamentRankingSystem:', tournamentRankingSystem)

    if (!response.ok) {
      throw new Error('Network response was not ok')
    }
    const data = await response.json()
    const data_ranking = await response_ranking.json()
    const data_tournament = await response_tournament.json()
    console.log('Tournament:', data_tournament)

    tournamentRankingSystem.value = data_tournament[0].rankingList
    console.log('Tournament Ranking System:', tournamentRankingSystem.value)

    players.value = Object.values(data)
    ranking.value = Object.values(data_ranking)

    console.log('Players:', players.value)
    console.log('Ranking:', ranking.value)

    console.log('boardType:', boardType)

    if (boardType === 'OTB') {
      console.log('OTB')
      console.log('boardType:', boardType)
      isOTB.value = true
    }
    else if (boardType === 'LIC') {
      console.log('LIC')
      console.log('boardType:', boardType)
      isOTB.value = false
    } 

    // obtenemos las rondas del torneo
    const response2 = await fetch(myURL+'get_round_results/'+tournamentId+'/')
    if (!response2.ok) {
      throw new Error('Network response was not ok')
    }
    const data2 = await response2.json()
    rounds.value = Object.values(data2)
    console.log('Rounds:', rounds.value)

    rounds.value = Object.values(data2).map(round => ({
      ...round,
      games: Object.values(round.games)  // ahora sí es un array
    }));
    
    rounds.value.forEach(round => {
      Object.values(round.games).forEach(game => {
        console.log('id del game', game.id);
        if (!(game.id in newResult)) {
          newResult[game.id] = '0';
          newResult2[game.id] = '0';
        }
      });
    });

  } catch (error) {
    console.error('Error fetching ranking:', error)
  }
})

const updateGameResultAdmin = async (game) => {
  let result = reverseFormatResult(newResult[game.id])
  const result2 = reverseFormatResult(newResult2[game.id])
  const gameToUpdate = game.id
  console.log('Updating game:', gameToUpdate, 'with result:', result, 'and result2:', result2)
  console.log('game', game)
  console.log('newResult', newResult[game.id])
  console.log('newResult2', newResult2[game.id])

  if (!result){
    result = result2
  }

  if (result === '0') {
    alert('Please select a result')
    return
  }

  try {
    const response = await fetch(myURL+'admin_update_game/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authStore.getAuthToken()}`,
      },
      body: JSON.stringify({
        game_id: gameToUpdate,
        otb_result: result,
      }),
    })
    if (!response.ok) {
      throw new Error('Network response was not ok')
    }
    const data = await response.json()
    console.log('Game updated:', data)
    let output_res2 = 0
    
    if (isOTB.value){
      game.result = newResult[game.id]
      output_res2 = newResult2[game.id]
    }
    else{
      licResult[game.id] = reverseFormatResult(newResult[game.id])
    }

    if (game.result === '0') {
      game.result = output_res2
    }

    game.result = formatResult(reverseFormatResult(game.result))

    console.log('Game result:', game.result)

    await fetchRanking();

  } catch (error) {
    console.error('Error updating game result:', error)
  }
}

const updateGameResultOtb = async (game) => {
  const result = reverseFormatResult(newResult[game.id])
  const gameToUpdate = game.id
  
  const email = prompt('Please enter your email address:')?.trim()
  if (!email) {
    alert('Email is required')
    return
  }

  const player = players.value.find(player => player.email?.trim() === email)
  if (!player) {
    alert('Player not found')
    return
  }

  try {
    const response = await fetch(myURL+'update_otb_game/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authStore.getAuthToken()}`,
      },
      body: JSON.stringify({
        game_id: gameToUpdate,
        otb_result: result,
        email: email,
      }),
    })

    const data = await response.json()

    if (!data.result) {
      alert('Error: ' + data.message)
      throw new Error('Network response was not ok')
    }

    game.result = newResult[game.id]

    game.result = reverseFormatResult(game.result)

    await fetchRanking();

  } catch (error) {
    console.error('Error updating game result:', error)
  }
}

const searchLichessResult = async (game, gameID) => {

  const gameToUpdate = game.id
  console.log("juego a actualizar", gameToUpdate)

  try{
    const response = await fetch(myURL + 'update_lichess_game/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authStore.getAuthToken()}`,
      },
      body: JSON.stringify({
        game_id: gameToUpdate,
        lichess_game_id: gameID,
      }),
    })

    const data = await response.json()
    console.log("data", data)

    if (!data.result){
      alert('Error: ' + data.message)
      throw new Error('Network response was not ok')
    }

    console.log("resultado del game", game)

    console.log("resultado lichess", licResult[game.id])

    licResult[game.id] = game.result

    await fetchRanking();

    const updatedRounds = await fetch(myURL + 'get_round_results/' + tournamentId + '/');
    const data2 = await updatedRounds.json();

    const updatedGame = Object.values(data2)
      .flatMap(round => Object.values(round.games))
      .find(g => g.id === game.id);

    if (updatedGame) {
      licResult[game.id] = updatedGame.result;
    }

  } catch(error){
    console.log('error searching lichess game'+ error)
  }
}

const fetchRanking = async () => {
  try {
    const response_ranking = await fetch(myURL + 'get_ranking/' + tournamentId + '/');
    if (!response_ranking.ok) throw new Error('Error fetching ranking');
    const data_ranking = await response_ranking.json();
    ranking.value = Object.values(data_ranking);
    console.log('Ranking updated:', ranking.value);
  } catch (error) {
    console.error('Error fetching updated ranking:', error);
  }
};

function formatResult(code) {
  switch (code) {
    case 'w': return '1-0'
    case 'b': return '0-1'
    case '=': return '½-½'
    case '+': return 'Forfeit Win'
    case '-': return 'Forfeit Loss'
    case 'U': return 'Unpaired'
    case 'H': return 'Bye'
    default: return code
  }
}

function formatResultSelect(code) {
  switch (code) {
    case 'w': return 'White wins (1-0)'
    case 'b': return 'Black wins (0-1)'
    case '=': return 'Draw (1/2-1/2)'
    case '*': return 'Result Unknown (*)'
    case '+': return 'Forfeit Win'
    case '-': return 'Forfeit Loss'
    case 'U': return 'Unpaired'
    case 'H': return 'Bye'
    default: return code
  }
}

function reverseFormatResult(code) {
  switch (code) {
    case 'White wins (1-0)': return 'w'
    case 'Black wins (0-1)': return 'b'
    case 'Draw (1/2-1/2)': return '='
    case 'Result Unknown (*)': return '*'
  }
}

function togglePanel(panelName) {
  if (activePanel.value === panelName) {
    activePanel.value = null 
  } else {
    activePanel.value = panelName 
  }
}

</script>

<style scoped>
button{
  background-color: #007bff; 
  color: white;
  padding: 10px 12px; 
  border: none; 
  border-radius: 5px; 
  cursor: pointer; 
  font-size: 16px;
  transition: background-color 0.3s;
  margin-bottom: 5px;
}

button:hover{
  background-color: #0056b3;
}

.accordion-container {
  margin-top: 10px;
  width: 100%;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.accordion {
  background-color: #eee;
  color: #444;
  cursor: pointer;
  padding: 18px;
  width: 100%;
  text-align: left;
  border: none;
  outline: none;
  transition: 0.4s;
  border-bottom: 1px solid #ccc; /* línea entre botón y panel */
}

.active, .accordion:hover {
  background-color: #ccc;
}

.accordion:after {
  content: '\02795';
  font-size: 13px;
  color: #777;
  float: right;
  margin-left: 5px;
}

.active:after {
  content: "\2796";
}

.panel {
  background-color: white;
  padding: 10px;
  display: block;
}

.round-block {
  margin-bottom: 40px;
  padding: 0 10px;
}

.round-block h4 {
  font-size: 1.3rem;
  margin-bottom: 8px;
  color: #333;
}

table {
  width: auto;
  border-collapse: collapse;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  overflow: hidden;
}

thead {
  background-color: #007bff;
  color: white;
}

th, td {
  padding: 10px 12px;
  text-align: left;
}

tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

tbody tr:nth-child(odd) {
  background-color: #fff;
}

tbody tr:hover {
  background-color: #eef;
}

td {
  color: #333;
}

td[colspan] {
  text-align: center;
  font-style: italic;
}

table th:first-child {
  border-top-left-radius: 6px;
}
table th:last-child {
  border-top-right-radius: 6px;
}

select {
  padding: 5px;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-right: 10px;
}

</style>
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../components/Home.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../components/Login.vue')
    },
    {
      path: '/logout',
      name: 'logout',
      component: () => import('../components/Logout.vue')
    },
    {
      path: '/createTournament',
      name: 'createTournamentComponent',
      component: () => import('../components/CreateTournament.vue')
    },
    {
      path: '/faq',
      name: 'faq',
      component: () => import('../components/FAQ.vue')
    },
    {
      path: '/tournamentdetail/:id/:name/:boardType/:tournamentType',
      name: 'TournamentDetail',
      component: () => import('../components/TournamentDetail.vue')
    }
  ]
})

export default router

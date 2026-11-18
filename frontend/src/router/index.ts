import { createRouter, createWebHistory } from 'vue-router'
import { installGuards } from '@/router/guards'
import BackofficeLayout from '@/layouts/BackofficeLayout.vue'
import MerchantLayout from '@/layouts/MerchantLayout.vue'
import TechLoginView from '@/modules/auth/views/TechLoginView.vue'
import MerchantLoginView from '@/modules/auth/views/MerchantLoginView.vue'
import SessionClosedView from '@/modules/auth/views/SessionClosedView.vue'
import TicketsListView from '@/modules/tech/tickets/views/TicketsListView.vue'
import TicketDetailView from '@/modules/tech/tickets/views/TicketDetailView.vue'
import MerchantsListView from '@/modules/tech/merchants/views/MerchantsListView.vue'
import MerchantsRestrictedView from '@/modules/tech/merchants/views/MerchantsRestrictedView.vue'
import MerchantCreateView from '@/modules/tech/merchants/views/MerchantCreateView.vue'
import TecnicosListView from '@/modules/tech/technicians/views/TecnicosListView.vue'
import ProfileView from '@/modules/profile/views/ProfileView.vue'
import MerchantHomeView from '@/modules/merchant/home/views/MerchantHomeView.vue'
import PaymentsListView from '@/modules/merchant/payments/views/PaymentsListView.vue'
import PaymentDetailView from '@/modules/merchant/payments/views/PaymentDetailView.vue'
import BalanceView from '@/modules/merchant/balance/views/BalanceView.vue'
import RefundsListView from '@/modules/merchant/refunds/views/RefundsListView.vue'
import SupportListView from '@/modules/merchant/tickets/views/SupportListView.vue'
import SupportDetailView from '@/modules/merchant/tickets/views/SupportDetailView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      redirect: '/acceso-tecnico',
    },
    {
      path: '/acceso-tecnico',
      name: 'tech-login',
      component: TechLoginView,
      meta: { guestOnly: true, portal: 'tecnico', title: 'Acceso técnicos' },
    },
    {
      path: '/acceso-comercio',
      name: 'merchant-login',
      component: MerchantLoginView,
      meta: { guestOnly: true, portal: 'comercio', title: 'Acceso comercios' },
    },
    {
      path: '/sesion-cerrada',
      name: 'session-closed',
      component: SessionClosedView,
      meta: { title: 'Sesión cerrada' },
    },
    {
      path: '/tecnico',
      component: BackofficeLayout,
      meta: { requiresAuth: true, portal: 'tecnico' },
      children: [
        { path: '', redirect: '/tecnico/tickets' },
        {
          path: 'tickets',
          name: 'tech-tickets',
          component: TicketsListView,
          meta: { title: 'Tickets de soporte', portal: 'tecnico' },
        },
        {
          path: 'tickets/:id',
          name: 'tech-ticket-detail',
          component: TicketDetailView,
          meta: { title: 'Detalle del ticket', portal: 'tecnico' },
        },
        {
          path: 'comercios',
          name: 'tech-merchants',
          component: MerchantsListView,
          meta: { title: 'Comercios', portal: 'tecnico', roles: ['admin'] },
        },
        {
          path: 'comercios/nuevo',
          name: 'tech-merchant-create',
          component: MerchantCreateView,
          meta: { title: 'Nuevo comercio', portal: 'tecnico', roles: ['admin'] },
        },
        {
          path: 'comercios/restringido',
          name: 'tech-access-restricted',
          component: MerchantsRestrictedView,
          meta: { title: 'Comercios', portal: 'tecnico' },
        },
        {
          path: 'tecnicos',
          name: 'tech-technicians',
          component: TecnicosListView,
          meta: { title: 'Técnicos', portal: 'tecnico', roles: ['admin'] },
        },
        {
          path: 'perfil',
          name: 'tech-profile',
          component: ProfileView,
          meta: { title: 'Mi perfil', portal: 'tecnico' },
        },
      ],
    },
    {
      path: '/comercio',
      component: MerchantLayout,
      meta: { requiresAuth: true, portal: 'comercio' },
      children: [
        { path: '', redirect: '/comercio/inicio' },
        {
          path: 'inicio',
          name: 'merchant-home',
          component: MerchantHomeView,
          meta: { title: 'Inicio', portal: 'comercio' },
        },
        {
          path: 'pagos',
          name: 'merchant-payments',
          component: PaymentsListView,
          meta: { title: 'Pagos recibidos', portal: 'comercio' },
        },
        {
          path: 'pagos/:id',
          name: 'merchant-payment-detail',
          component: PaymentDetailView,
          meta: { title: 'Detalle de pago', portal: 'comercio' },
        },
        {
          path: 'saldo',
          name: 'merchant-balance',
          component: BalanceView,
          meta: { title: 'Saldo y retiradas', portal: 'comercio' },
        },
        {
          path: 'devoluciones',
          name: 'merchant-refunds',
          component: RefundsListView,
          meta: { title: 'Devoluciones', portal: 'comercio' },
        },
        {
          path: 'tickets',
          name: 'merchant-tickets',
          component: SupportListView,
          meta: { title: 'Soporte', portal: 'comercio' },
        },
        {
          path: 'tickets/:id',
          name: 'merchant-ticket-detail',
          component: SupportDetailView,
          meta: { title: 'Detalle del ticket', portal: 'comercio' },
        },
        {
          path: 'perfil',
          name: 'merchant-profile',
          component: ProfileView,
          meta: { title: 'Mi perfil', portal: 'comercio' },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
      meta: { title: 'Página no encontrada' },
    },
  ],
})

installGuards(router)

export default router

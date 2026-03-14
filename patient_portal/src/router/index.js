import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Dashboard from '../views/Dashboard.vue'
import PatientRegistration from '../views/PatientRegistration.vue'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home,
        meta: { requiresAuth: true }
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { requiresAuth: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: PatientRegistration,
        meta: { allowGuest: true, hideLayout: true }
    },
    {
        path: '/history',
        name: 'MedicalHistory',
        component: () => import('../views/MedicalHistory.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/history/print',
        name: 'PrintMedicalHistory',
        component: () => import('../views/PrintMedicalHistory.vue'),
        meta: { requiresAuth: true, hideLayout: true }
    },
    {
        path: '/payment/:id',
        name: 'PaymentStatus',
        component: () => import('../views/PaymentStatus.vue'),
        meta: { requiresAuth: true }
    },
    // Add a catch-all route if needed
    {
        path: '/:pathMatch(.*)*',
        redirect: '/'
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// Helper function to check if user is authenticated
function isUserAuthenticated() {
    // Check frappe_boot first (set by our HTML template)
    if (window.frappe_boot && typeof window.frappe_boot.is_guest === 'boolean') {
        return !window.frappe_boot.is_guest
    }

    // Fallback: check if user_info has a valid email (not Guest)
    if (window.frappe_boot?.user_info?.email) {
        return true
    }

    // Check if we're on the main patient_portal page (server already validated auth)
    // If server let them through to patient_portal, they're authenticated
    if (window.location.pathname.includes('/patient_portal') &&
        !window.location.pathname.includes('/patient_registration')) {
        return true  // Server-side auth already passed
    }

    return false
}

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
    // If on registration page, default strict '/' to '/register' to avoid auth redirect
    if (window.is_registration_page && to.path === '/') {
        next({ name: 'Register' })
        return
    }

    const isAuthenticated = isUserAuthenticated()

    // Debug logging (remove in production)
    console.log('[Router Guard]', {
        to: to.path,
        isAuthenticated,
        frappe_boot: window.frappe_boot,
        pathname: window.location.pathname
    })

    // If route requires auth and user is NOT authenticated, redirect to login
    if (to.meta.requiresAuth && !isAuthenticated) {
        window.location.href = '/login?redirect-to=/patient_portal'
        return
    }

    next()
})

export default router

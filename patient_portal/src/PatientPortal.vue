<template>
	<!-- Standardized Slate-50 Background for a quiet feel -->
	<div class="h-screen flex flex-col bg-slate-50 font-sans antialiased text-slate-600">
		
		<!-- Compact Studio Header - Hidden on registration page -->
		<header v-if="!hideLayout" class="sticky top-0 w-full z-[100] bg-white/70 backdrop-blur-md border-b border-slate-200/60 px-4 md:px-6 lg:px-10 py-2.5">
			<div class="max-w-[1400px] mx-auto flex items-center justify-between">
				
				<!-- Brand Identity -->
				<div class="flex items-center gap-3 group cursor-pointer" @click="router.push('/')">
					<img 
						:src="clinicLogo" 
						alt="Clinic Logo" 
						class="h-9 w-auto object-contain transition-transform group-hover:scale-105"
					/>
				</div>

				<!-- Slim Capsule Nav (Desktop only) -->
				<nav class="hidden lg:flex items-center gap-1 p-0.5 bg-slate-100/80 rounded-xl border border-slate-200/50">
					<router-link 
						v-for="nav in [{label: 'Home', path: '/'}, {label: 'Dashboard', path: '/dashboard'}]" 
						:key="nav.path"
						:to="nav.path" 
						class="px-5 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all"
						:class="route.path === nav.path 
							? 'bg-white text-slate-900 shadow-sm' 
							: 'text-slate-400 hover:text-slate-600'"
					>
						{{ nav.label }}
					</router-link>
				</nav>

				<!-- User & Actions -->
				<div class="flex items-center gap-2 md:gap-4">
					
					<!-- Subtle Registration Link (desktop) -->
					<button
						v-if="!isGuest && !patient"
						@click="goToRegistration"
						class="hidden md:block text-[10px] font-bold text-slate-400 uppercase tracking-widest hover:text-brand-orange transition-colors"
					>
						Register Patient
					</button>

					<!-- Compact User Dropdown -->
					<div v-if="!isGuest" class="flex items-center">
						<Dropdown :options="userMenuOptions">
							<template #default="{ open }">
								<button class="flex items-center gap-1.5 group p-1 pr-2 rounded-xl hover:bg-slate-100/80 transition-all">
									<Avatar
										:image="userInfo.image"
										:label="userInfo.full_name || 'User'"
										size="md"
										class="rounded-xl ring-2 ring-slate-100 group-hover:ring-brand-orange/30 transition-all shadow-sm"
									/>
									<ChevronDownIcon class="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 transition-colors hidden sm:block" />
								</button>
							</template>
						</Dropdown>
					</div>

					<!-- Compact Login -->
					<button
						v-if="isGuest"
						@click="goToLogin"
						class="px-4 md:px-6 py-2 rounded-lg bg-slate-900 text-white text-[10px] font-bold uppercase tracking-widest hover:bg-slate-800 transition-all shadow-sm"
					>
						Login
					</button>

					<!-- Hamburger (Mobile/Tablet only) -->
					<button
						v-if="!isGuest"
						@click="showMobileMenu = !showMobileMenu"
						class="lg:hidden flex items-center justify-center w-9 h-9 rounded-xl bg-slate-100 text-slate-500 hover:bg-slate-200 transition-all"
					>
						<svg v-if="!showMobileMenu" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
						</svg>
						<svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
			</div>

			<!-- Mobile Nav Dropdown -->
			<transition name="slide-down">
				<div v-if="showMobileMenu && !isGuest" class="lg:hidden border-t border-slate-100 mt-2.5 py-3 space-y-1">
					<router-link 
						v-for="nav in [{label: 'Home', path: '/'}, {label: 'Dashboard', path: '/dashboard'}]"
						:key="nav.path"
						:to="nav.path"
						@click="showMobileMenu = false"
						class="flex items-center px-3 py-2.5 rounded-xl text-sm font-bold uppercase tracking-widest transition-all"
						:class="route.path === nav.path 
							? 'bg-slate-900 text-white' 
							: 'text-slate-500 hover:bg-slate-100'"
					>
						{{ nav.label }}
					</router-link>
					<button
						v-if="!patient"
						@click="goToRegistration(); showMobileMenu = false"
						class="w-full text-left flex items-center px-3 py-2.5 rounded-xl text-sm font-bold uppercase tracking-widest text-slate-500 hover:bg-slate-100 transition-all"
					>
						Register Patient
					</button>
				</div>
			</transition>
		</header>

		<!-- Main content handles the page-level scrolling -->
		<main class="flex-1 overflow-y-auto custom-scrollbar">
			<div :class="hideLayout ? 'h-full' : 'max-w-[1400px] mx-auto w-full min-h-full'">
				<router-view v-slot="{ Component }">
					<transition 
						name="page-fade" 
						mode="out-in" 
						appear
					>
						<component :is="Component" />
					</transition>
				</router-view>
			</div>
		</main>

		<!-- Minimalist Utility Footer - Hidden on registration page -->
		<footer v-if="!hideLayout" class="px-4 md:px-10 py-4 bg-white border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-2">
			<div class="flex items-center gap-1.5">
				<div class="w-1 h-1 rounded-full bg-slate-300"></div>
				<p class="text-[9px] font-bold text-slate-300 uppercase tracking-[0.2em]">© 2026 Patient Portal</p>
			</div>
			<div class="flex gap-5">
				<a href="#" class="text-[9px] font-bold text-slate-300 uppercase tracking-widest hover:text-slate-600">Privacy</a>
				<a href="#" class="text-[9px] font-bold text-slate-300 uppercase tracking-widest hover:text-slate-600">Support</a>
			</div>
		</footer>
	</div>

	<!-- Alert Dialog -->
	<Teleport to="body">
		<Dialog :options="{
			title: dialog_title,
			message: dialog_message,
			size: 'sm',
			icon: { name: 'alert-circle', appearance: 'warning' },
			actions: [{ label: 'OK', variant: 'solid', theme: 'gray' }]
		}" v-model="alert_dialog" />
	</Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ChevronDownIcon } from 'lucide-vue-next'
import {
	createResource,
	Dialog,
	Avatar,
	Dropdown
} from 'frappe-ui'

const clinicLogo = '/assets/healthcare/images/zan-center-for-women-logo.png'
const router = useRouter()
const route = useRoute()

const alert_dialog = ref(false)
const dialog_title = ref("")
const dialog_message = ref("")
const showMobileMenu = ref(false)

// Authentication & Patient Data Logic
const bootData = window.frappe_boot || {}
const isGuest = computed(() => bootData.is_guest)
const userInfo = computed(() => bootData.user_info || {})
const hideLayout = computed(() => route.meta?.hideLayout === true)
const patient = ref(JSON.parse(localStorage.getItem("patient")))

const handleLogout = async () => {
	try {
		await fetch('/api/method/logout', {
			method: 'POST',
			headers: {
				'X-Frappe-CSRF-Token': window.csrf_token || window.frappe?.csrf_token
			}
		})
	} catch (e) {
		// Ignore network errors during logout
	}
	localStorage.removeItem('patient')
	window.location.href = '/login'
}

const userMenuOptions = [
	{ label: 'Portal Home', onClick: () => router.push('/'), icon: 'home' },
	{ label: 'Appointments', onClick: () => router.push('/dashboard'), icon: 'calendar' },
	{ label: 'Logout', onClick: handleLogout, icon: 'log-out' }
]

const get_logged_in_patient = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_logged_in_patient",
	method: 'GET',
	onSuccess(response) {
		if (response) {
			patient.value = response
			localStorage.setItem("patient", JSON.stringify(response))
		}
	}
})

onMounted(() => {
	if (!isGuest.value) get_logged_in_patient.fetch()
})

const goToLogin = () => window.location.href = '/login?redirect-to=/patient_portal'
const goToRegistration = () => window.location.href = '/patient-registration'
</script>

<style>
/* Refined Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
	width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
	background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
	background: #e2e8f0;
	border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
	background: #cbd5e1;
}

/* Minimal Smooth Transitions */
.page-fade-enter-active, .page-fade-leave-active {
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-fade-enter-from {
	opacity: 0;
	transform: translateY(4px);
}
.page-fade-leave-to {
	opacity: 0;
	transform: translateY(-4px);
}

/* Mobile nav slide-down animation */
.slide-down-enter-active,
.slide-down-leave-active {
	transition: all 0.2s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
	opacity: 0;
	transform: translateY(-8px);
}

/* Base resets to avoid scaling issues */
html, body, #app {
	height: 100%;
	font-size: 14px;
}

/* Ensure Dialogs don't feel oversized */
.frappe-dialog {
	--dialog-border-radius: 12px;
}
</style>
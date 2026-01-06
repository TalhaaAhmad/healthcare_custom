<template>
	<!-- Standardized Slate-50 Background for a quiet feel -->
	<div class="h-screen flex flex-col bg-slate-50 font-sans antialiased text-slate-600">
		
		<!-- Compact Studio Header (Slimmer py-2.5) - Hidden on registration page -->
		<header v-if="!hideLayout" class="sticky top-0 w-full z-[100] bg-white/70 backdrop-blur-md border-b border-slate-200/60 px-6 lg:px-10 py-2.5">
			<div class="max-w-[1400px] mx-auto flex items-center justify-between">
				
				<!-- Precise Brand Identity -->
				<div class="flex items-center gap-3.5 group cursor-pointer" @click="router.push('/')">
					<div class="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center shadow-md transition-transform group-hover:scale-105">
						<ActivityIcon class="w-4 h-4 text-white" />
					</div>
					<div class="hidden xs:block">
						<h1 class="text-xs font-black text-slate-900 uppercase tracking-tighter">Portal</h1>
						<p class="text-[8px] font-bold text-slate-400 uppercase tracking-[0.2em]">Medical</p>
					</div>
				</div>

				<!-- Slim Capsule Nav -->
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
				<div class="flex items-center gap-4">
					
					<!-- Subtle Registration Link -->
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
							<template #target>
								<button class="flex items-center gap-2 group">
									<Avatar
										:image="userInfo.image"
										:label="userInfo.full_name"
										size="sm"
										class="rounded-lg border border-slate-100 shadow-sm"
									/>
									<ChevronDownIcon class="w-3 h-3 text-slate-300 group-hover:text-slate-600 transition-colors" />
								</button>
							</template>
						</Dropdown>
					</div>

					<!-- Compact Login -->
					<button
						v-if="isGuest"
						@click="goToLogin"
						class="px-6 py-2 rounded-lg bg-slate-900 text-white text-[10px] font-bold uppercase tracking-widest hover:bg-slate-800 transition-all shadow-sm"
					>
						Login
					</button>
				</div>
			</div>
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
		<footer v-if="!hideLayout" class="px-10 py-4 bg-white border-t border-slate-100 flex items-center justify-between">
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
import { ActivityIcon, ChevronDownIcon } from 'lucide-vue-next'
import {
	createResource,
	Dialog,
	Avatar,
	Dropdown
} from 'frappe-ui'

const router = useRouter()
const route = useRoute()

const alert_dialog = ref(false)
const dialog_title = ref("")
const dialog_message = ref("")

// Authentication & Patient Data Logic
const bootData = window.frappe_boot || {}
const isGuest = computed(() => bootData.is_guest)
const userInfo = computed(() => bootData.user_info || {})
const hideLayout = computed(() => route.meta?.hideLayout === true)
const patient = ref(JSON.parse(localStorage.getItem("patient")))

const userMenuOptions = [
	{ label: 'Portal Home', onClick: () => router.push('/'), icon: 'home' },
	{ label: 'Appointments', onClick: () => router.push('/dashboard'), icon: 'calendar' },
	{ label: 'Logout', onClick: () => window.location.href = '/api/method/logout', icon: 'log-out' }
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

/* Base resets to avoid scaling issues */
html, body, #app {
	height: 100%;
	font-size: 14px; /* Standard base font size */
}

/* Ensure Dialogs don't feel oversized */
.frappe-dialog {
	--dialog-border-radius: 12px;
}
</style>
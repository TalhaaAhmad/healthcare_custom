<template>
	<div class="h-screen flex flex-col bg-gray-50">
		<!-- Header -->
		<header class="flex items-center justify-between px-6 py-4 bg-white border-b shadow-sm shrink-0">
			<div class="flex items-center gap-4">
				<h1 class="text-xl font-bold text-gray-900">Patient Portal</h1>
			</div>

			<div class="flex items-center gap-4">
				<!-- Registration CTA for logged in users who are NOT patients -->
				<Button
					v-if="!isGuest && !patient"
					variant="outline"
					@click="goToRegistration"
				>
					Register as Patient
				</Button>

				<Dropdown
					v-if="!isGuest"
					:options="userMenuOptions"
				>
					<template #target>
						<div class="flex items-center gap-3 cursor-pointer group">
							<div class="text-right hidden sm:block">
								<p class="text-sm font-medium text-gray-900">{{ userInfo.full_name }}</p>
								<p class="text-xs text-gray-500">{{ userInfo.email }}</p>
							</div>
							<Avatar
								:image="userInfo.image"
								:label="userInfo.full_name"
								size="lg"
								class="border group-hover:border-gray-300 transition-colors"
							/>
						</div>
					</template>
				</Dropdown>

				<Button
					v-if="isGuest"
					variant="solid"
					@click="goToLogin"
				>
					Login
				</Button>
			</div>
		</header>

		<!-- Breadcrumbs -->
		<nav class="flex px-6 py-2 bg-white border-b overflow-x-auto whitespace-nowrap shrink-0" aria-label="Breadcrumb">
			<ol class="inline-flex items-center space-x-2">
				<li class="inline-flex items-center">
					<a href="/me" class="inline-flex items-center text-xs font-medium text-gray-500 hover:text-gray-900 transition-colors">
						<FeatherIcon name="home" class="w-3.5 h-3.5 mr-1.5" />
						Home
					</a>
				</li>
				<li v-for="(tab, index) in tabs" :key="tab.label" v-show="portal_tabs === index">
					<div class="flex items-center">
						<FeatherIcon name="chevron-right" class="w-4 h-4 text-gray-400" />
						<span class="ml-1.5 text-xs font-semibold text-gray-900 capitalize">{{ tab.label }}</span>
					</div>
				</li>
			</ol>
		</nav>

		<!-- Main Content -->
		<main class="flex-1 overflow-y-auto p-6 bg-gray-50/50">
			<div class="max-w-6xl mx-auto">
				<Tabs as="div" v-model="portal_tabs" :tabs="tabs">
					<template #tab-panel="{ tab }">
						<div v-if="tab.label == 'Appointments'" class="py-4">
							<AppointmentModel />
						</div>
						<div v-else-if="tab.label == 'Diagnostics'" class="py-4">
							<DiagnosticModel />
						</div>
					</template>
				</Tabs>
			</div>
		</main>
	</div>

	<Dialog :options="{
		title: dialog_title,
		message: dialog_message,
		size: 'xl',
		icon: {
			name: 'alert-triangle',
			appearance: 'warning',
		},
		actions: [
			{
				label: 'OK',
				variant: 'solid',
			},
		],
	}" v-model="alert_dialog" @click="alert_dialog = false" />
</template>

<script setup>
import { ref, computed } from 'vue'
import AppointmentModel from '@/components/AppointmentModel.vue'
import DiagnosticModel from '@/components/DiagnosticModel.vue'

import {
	createResource,
	Tabs,
	Dialog,
	Button,
	Avatar,
	Dropdown,
} from 'frappe-ui'

const alert_dialog = ref(false);
const portal_tabs = ref(0);
const dialog_title = ref("");
const dialog_message = ref("");

const healthcareSettings = ref({});
const patient = ref(JSON.parse(localStorage.getItem("patient")));

// Boot data from window
const bootData = window.frappe_boot || {};
const isGuest = computed(() => bootData.is_guest);
const userInfo = computed(() => bootData.user_info || {});

const userMenuOptions = [
	{
		label: 'Logout',
		onClick: () => {
			window.location.href = '/api/method/logout';
		},
		icon: 'log-out'
	}
]

const getHealthcareSettings = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_settings",
	method: "GET",
	onSuccess(response) {
		if (response) {
			healthcareSettings.value = response
		}
	},
});
getHealthcareSettings.fetch();

const tabs = computed(() => {
	let baseTabs = [{ label: 'Appointments' }]
	if (healthcareSettings.value.show_diagnostics_tab) {
		baseTabs.push({ label: 'Diagnostics' })
	}
	return baseTabs
})

const get_logged_in_patient = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_logged_in_patient",
	method: "GET",
	onSuccess(response) {
		if (response) {
			patient.value = response;
			localStorage.setItem("patient", JSON.stringify(response));
		} else {
			patient.value = null;
			localStorage.removeItem("patient");
		}
	},
	onError(error) {
		console.error("Failed to load patient info", error);
	}
});

if (!isGuest.value) {
	get_logged_in_patient.fetch();
}

const goToLogin = () => {
	window.location.href = '/login?redirect-to=/patient_portal';
}

const goToRegistration = () => {
	window.location.href = '/patient-registration';
}

</script>

<style scoped>
/* Ensure the app takes full height */
:deep(body), :deep(html), #app {
	height: 100%;
	margin: 0;
	padding: 0;
}
</style>

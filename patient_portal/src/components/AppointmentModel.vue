<template>
	<!-- 1. Moved the Dialogs OUTSIDE the animated wrapper to prevent stacking issues -->
	<div class="appointment-model-wrapper">
		<div class="animate-fade-in max-w-7xl mx-auto px-4 py-2">
			<div class="min-h-[60vh] flex flex-col">
				<!-- Appointment Grid -->
				<div v-if="paginatedAppointments.length" class="flex-1">
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						<div
							v-for="item in paginatedAppointments"
							:key="item.name"
							class="bg-white rounded-[24px] p-6 cursor-pointer border border-slate-100 hover:border-brand-orange/20 hover:shadow-xl hover:shadow-slate-200/50 transition-all duration-300 group relative overflow-hidden"
							@click="appointmentDetails(item)"
						>
							<!-- Top Section -->
							<div class="flex items-center justify-between mb-5">
								<span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest bg-slate-50 px-2 py-1 rounded-md">
									{{ item.name }}
								</span>
								<div class="px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-tight border shadow-sm"
									:class="getStatusClasses(item.status)">
									{{ item.status }}
								</div>
							</div>

							<!-- Mid Section -->
							<div class="flex items-center gap-4 mb-6">
								<div class="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center group-hover:bg-brand-orange/10 transition-colors">
									<ActivityIcon class="w-7 h-7 text-slate-400 group-hover:text-brand-orange transition-colors" />
								</div>
								<div class="overflow-hidden">
									<h3 class="font-bold text-slate-900 text-lg leading-tight truncate">
										{{ item.title }}
									</h3>
									<p class="text-slate-400 text-sm font-medium">Practitioner</p>
								</div>
							</div>

							<!-- Schedule Section -->
							<div class="space-y-3 p-4 bg-slate-50/50 rounded-2xl border border-slate-50">
								<div class="flex items-center text-sm font-semibold text-slate-700">
									<CalendarIcon class="w-4 h-4 mr-3 text-brand-orange" />
									{{ formatDate(item.appointment_date) }}
								</div>
								<div class="flex items-center text-sm font-semibold text-slate-700">
									<ClockIcon class="w-4 h-4 mr-3 text-brand-orange" />
									{{ item.appointment_time }}
									<span class="mx-2 text-slate-300">•</span>
									<span class="text-slate-400 font-medium text-xs">{{ item.duration }} mins</span>
								</div>
							</div>
							
							<div class="mt-5 flex items-center justify-between pt-2">
								<span class="text-xs font-bold text-slate-400 group-hover:text-brand-orange transition-colors uppercase tracking-widest">View Details</span>
								<ChevronRightIcon class="w-5 h-5 text-slate-300 group-hover:text-brand-orange group-hover:translate-x-1 transition-all" />
							</div>
						</div>
					</div>
				</div>

				<!-- Empty State -->
				<div v-else class="flex flex-col items-center justify-center flex-grow text-center p-12 bg-white rounded-[32px] border-2 border-dashed border-slate-100 shadow-inner">
					<div class="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mb-6 shadow-sm">
						<CalendarXIcon class="w-12 h-12 text-slate-200" />
					</div>
					<h2 class="text-2xl font-bold text-slate-900 mb-2">No Appointments Found</h2>
					<button @click="make_appointment_dialog = true" class="bg-slate-900 text-white px-8 py-3 rounded-2xl font-bold hover:bg-slate-800 transition-all">
						Schedule First Appointment
					</button>
				</div>

				<!-- Pagination -->
				<div v-if="paginatedAppointments.length" class="flex items-center justify-center gap-6 mt-12 py-8 border-t border-slate-100">
					<button :disabled="currentPage === 1" @click="currentPage--" class="w-12 h-12 flex items-center justify-center rounded-2xl border border-slate-200 hover:border-brand-orange hover:text-brand-orange disabled:opacity-20 transition-all bg-white shadow-sm">
						<ChevronLeftIcon class="w-6 h-6" />
					</button>
					<div class="flex items-center gap-3 px-6 py-2 bg-white rounded-2xl border border-slate-200 shadow-sm">
						<span class="text-xs font-black text-slate-900">{{ currentPage }} / {{ totalPages }}</span>
					</div>
					<button :disabled="currentPage === totalPages" @click="currentPage++" class="w-12 h-12 flex items-center justify-center rounded-2xl border border-slate-200 hover:border-brand-orange hover:text-brand-orange disabled:opacity-20 transition-all bg-white shadow-sm">
						<ChevronRightIcon class="w-6 h-6" />
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- 2. TELEPORT TO BODY: This ensures the modal is on a higher layer than the list -->
	<Teleport to="body">
		<Dialog 
			v-model="appointment_details" 
			:options="{ size: '4xl' }"
			class="z-[9999]"
		>
			<!-- Using proper slots fixes the 'overlap' issue -->
			<template #body-title>
				<div v-if="selectedAppointment" class="flex flex-col md:flex-row md:items-center justify-between gap-4 w-full">
					<div>
						<h2 class="text-2xl font-bold text-slate-900">Appointment Details</h2>
						<p class="text-slate-500 text-xs mt-1 font-bold uppercase tracking-widest">Ref: # {{ selectedAppointment.name }}</p>
					</div>
					<Badge
						variant="solid"
						size="lg"
						class="rounded-xl px-4 py-1.5 text-xs font-black uppercase tracking-widest"
						:theme="getStatusColor(selectedAppointment.status)">
						{{ selectedAppointment.status }}
					</Badge>
				</div>
			</template>

			<template #body-content>
				<div v-if="selectedAppointment" class="mt-4 space-y-6">
					<!-- Identity Grid -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<!-- Patient -->
						<div class="p-5 bg-slate-50 rounded-3xl border border-slate-100 flex items-center gap-4">
							<div v-if="selectedAppointment.patient_image" class="w-14 h-14 rounded-2xl overflow-hidden shadow-sm">
								<img :src="selectedAppointment.patient_image" class="w-full h-full object-cover" />
							</div>
							<div v-else class="w-14 h-14 rounded-2xl bg-brand-orange/10 flex items-center justify-center text-brand-orange text-xl font-bold">
								{{ selectedAppointment.patient_name?.charAt(0) }}
							</div>
							<div>
								<p class="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-0.5">Patient</p>
								<h4 class="text-base font-bold text-slate-900">{{ selectedAppointment.patient_name }}</h4>
							</div>
						</div>

						<!-- Practitioner -->
						<div class="p-5 bg-slate-50 rounded-3xl border border-slate-100 flex items-center gap-4">
							<div v-if="selectedAppointment.practitioner_image" class="w-14 h-14 rounded-2xl overflow-hidden shadow-sm">
								<img :src="selectedAppointment.practitioner_image" class="w-full h-full object-cover" />
							</div>
							<div v-else class="w-14 h-14 rounded-2xl bg-slate-900 text-white flex items-center justify-center text-xl font-bold">
								{{ selectedAppointment.practitioner_name?.charAt(0) }}
							</div>
							<div>
								<p class="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-0.5">Practitioner</p>
								<h4 class="text-base font-bold text-slate-900">{{ selectedAppointment.practitioner_name }}</h4>
							</div>
						</div>
					</div>

					<!-- Details Info Box -->
					<div class="bg-slate-900/5 p-8 rounded-[32px] grid grid-cols-1 md:grid-cols-2 gap-8">
						<div class="flex items-start gap-4">
							<div class="w-10 h-10 rounded-xl bg-white shadow-sm flex items-center justify-center shrink-0">
								<CalendarIcon class="w-5 h-5 text-slate-400" />
							</div>
							<div>
								<p class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Date & Time</p>
								<p class="font-bold text-slate-900">{{ formatDate(selectedAppointment.appointment_date) }}</p>
								<p class="text-sm font-medium text-slate-500">{{ selectedAppointment.appointment_time }}</p>
							</div>
						</div>

						<div class="flex items-center justify-between bg-white p-5 rounded-2xl border border-slate-100">
							<div class="flex items-center gap-3">
								<div class="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center text-slate-400 font-bold">$</div>
								<p class="text-xl font-black text-slate-900">{{ formatCurrency(selectedAppointment.paid_amount, selectedAppointment.default_currency) }}</p>
							</div>
							<Badge :variant="'subtle'" :theme="selectedAppointment.invoiced == 1 ? 'green' : 'red'">
								{{ selectedAppointment.invoiced ? 'Paid' : 'Unpaid' }}
							</Badge>
						</div>
					</div>

					<!-- Footer Actions (Styled within Dialog Content) -->
					<div v-if="['Scheduled', 'Open', 'Confirmed'].includes(selectedAppointment.status)" class="flex flex-col sm:flex-row items-center justify-end gap-3 pt-4">
						<button class="text-slate-400 hover:text-red-500 px-6 py-2 font-bold text-sm transition-colors" @click="confirmCancel(selectedAppointment)">
							{{ cancelling ? 'Processing...' : 'Cancel Appointment' }}
						</button>
						<button class="bg-slate-900 text-white px-8 py-3 rounded-2xl font-bold hover:bg-slate-800 transition-all flex items-center gap-2" @click="openReschedule(selectedAppointment)">
							<RotateCwIcon class="w-4 h-4" />
							Reschedule
						</button>
					</div>
				</div>
			</template>
		</Dialog>

		<!-- Other Dialogs -->
		<BookAppointmentModel v-if="make_appointment_dialog" v-model="make_appointment_dialog" @appointment_booked="get_appointments.reload()" />
		<BookAppointmentModel v-if="reschedule_dialog" v-model="reschedule_dialog" :reschedule_appointment="selectedAppointment" @appointment_booked="onRescheduled" />
	</Teleport>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import BookAppointmentModel from '@/components/BookAppointmentModel.vue'
import { formatCurrency } from "@/utils/formatters"
import {
	createResource,
	Button,
	Dialog,
	Badge,
	Tooltip,
	toast
} from 'frappe-ui'

import {
	PlusIcon,
	ActivityIcon,
	CalendarIcon,
	ClockIcon,
	ChevronRightIcon,
	CalendarXIcon,
	ChevronLeftIcon,
	TrashIcon,
	RotateCwIcon
} from 'lucide-vue-next'

const appointment_details = ref(false);
const make_appointment_dialog = ref(false);
const reschedule_dialog = ref(false);
const alert_dialog = ref(false);

const appointments = ref([]);
const currentPage = ref(1);
const pageSize = 9; // Grid of 3x3 looks good

const selectedAppointment = ref(null);
const dialog_title = ref("");
const dialog_message = ref("");

const get_appointments = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_appointments",
	method: "GET",
	onSuccess(response) {
		if (response) {
			appointments.value = response;
		}
	},
	onError(error) {
		dialog_message.value = error.messages?.[0] || error;
		dialog_title.value = "Failed to load appointments";
		alert_dialog.value = true;
	}
});

onMounted(() => {
	get_appointments.fetch();
})

function appointmentDetails(appointment) {
	selectedAppointment.value = appointment;
	appointment_details.value = true;
}

function formatDate(dateStr) {
	if (!dateStr) return '';
	return new Date(dateStr).toLocaleDateString("en-US", {
		weekday: "short",
		year: "numeric",
		month: "short",
		day: "numeric"
	});
}

const totalPages = computed(() =>
	Math.max(1, Math.ceil(appointments.value.length / pageSize))
);

const paginatedAppointments = computed(() => {
	const start = (currentPage.value - 1) * pageSize;
	return appointments.value.slice(start, start + pageSize);
});

const getStatusColor = (status) => {
	switch (status) {
		case "Confirmed":
			return "green"
		case "Open":
		case "Scheduled":
			return "orange"
		case "Cancelled":
			return "red"
		case "Checked In":
			return "blue"
		case "Checked Out":
			return "gray"
		default:
			return "gray"
	}
}

const getStatusClasses = (status) => {
	switch (status) {
		case "Confirmed":
			return "bg-green-50 text-green-600 border-green-100"
		case "Open":
		case "Scheduled":
			return "bg-orange-50 text-orange-600 border-orange-100"
		case "Cancelled":
			return "bg-red-50 text-red-600 border-red-100"
		case "Checked In":
			return "bg-blue-50 text-blue-600 border-blue-100"
		default:
			return "bg-slate-50 text-slate-500 border-slate-100"
	}
}

const cancelling = ref(false)
const confirmCancel = async (appointment) => {
	if (!confirm('Are you sure you want to cancel this appointment?')) return
	
	cancelling.value = true
	try {
		await frappe.call({
			method: 'healthcare.healthcare.api.patient_portal.cancel_appointment',
			args: {
				appointment_id: appointment.name
			}
		})
		
		get_appointments.fetch()
		// toast.success('Appointment cancelled successfully')
	} catch (e) {
		console.error(e)
		// toast.error(e.messages?.[0] || 'Cancellation failed')
	} finally {
		cancelling.value = false
		appointment_details.value = false
	}
}

const openReschedule = (appointment) => {
	selectedAppointment.value = appointment;
	reschedule_dialog.value = true;
}

const onRescheduled = () => {
	reschedule_dialog.value = false;
	appointment_details.value = false;
	get_appointments.reload();
}

function print(doctype, docname) {
	let get_print_format = createResource({
		url: "/api/method/healthcare.healthcare.api.patient_portal.get_print_format",
		method: "POST",
		makeParams() {
			return {
				doctype: doctype,
				name: docname
			}
		},
		onSuccess(response) {
			if (response) {
				const with_letterhead = response.letter_head ? 1 : 0;
				const print_format = response.print_format;
				const doc_names = JSON.stringify([docname,]);
				const letterhead = response.letter_head;

				let pdf_options = JSON.stringify({
					"page-size": "A4",
					"margin-top": "60mm",
					"margin-bottom": "60mm",
					"margin-left": "5mm",
					"margin-right": "5mm",
				});

				const w = window.open(
					"/api/method/frappe.utils.print_format.download_multi_pdf?" +
						"doctype=" +
						encodeURIComponent(doctype) +
						"&name=" +
						encodeURIComponent(doc_names) +
						"&format=" +
						encodeURIComponent(print_format) +
						"&no_letterhead=" +
						(with_letterhead ? "0" : "1") +
						"&letterhead=" +
						encodeURIComponent(letterhead) +
						"&options=" +
						encodeURIComponent(pdf_options)
				);

				if (!w) {
					alert("Please enable pop-ups");
					return;
				}
			}
		}
	});
	get_print_format.fetch();
}
</script>

<style>
/* 
 * CRITICAL: Fix for Dialog appearing behind appointment cards
 * frappe-ui Dialog uses HeadlessUI which creates portals
 */

/* Target the HeadlessUI portal root - this is what frappe-ui uses */
[id^="headlessui-portal-root"],
#headlessui-portal-root {
	position: fixed !important;
	z-index: 99999 !important;
}

/* Target any direct child divs of body that might be portals */
body > div:not(#app):not([data-v-app]) {
	z-index: 99999 !important;
}

/* The backdrop/overlay layer */
.fixed.inset-0.bg-black\/80,
.fixed.inset-0[style*="background"],
div[data-headlessui-state] + .fixed.inset-0,
.bg-black.bg-opacity-80.fixed.inset-0,
[data-headlessui-state] ~ .fixed {
	z-index: 99998 !important;
	position: fixed !important;
}

/* The dialog container and content */
[role="dialog"],
[data-headlessui-state][role="dialog"],
.relative.bg-white.rounded-xl {
	z-index: 99999 !important;
	position: relative !important;
}

/* Ensure the appointment wrapper doesn't create high stacking context */
.appointment-model-wrapper {
	position: relative;
	z-index: 1;
}

/* Teleported content should always be on top */
body > [data-teleported],
body > .fixed {
	z-index: 99999 !important;
}
</style>

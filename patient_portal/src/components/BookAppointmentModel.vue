<template>
	<Dialog v-if="show" v-model="show" :options="{
		size: '5xl',
		noPadding: true,
		title: 'Book Appointment',
	}" :disable-outside-click-to-close="true">
		<template #body-content>
			<div class="flex flex-col min-h-[60vh] md:min-h-[75vh] max-h-[90vh] md:max-h-[85vh] bg-white rounded-2xl overflow-hidden font-sans text-slate-600">
				
				<!-- Slim Utility Header -->
				<div class="px-4 md:px-6 h-auto min-h-[56px] border-b border-slate-100 flex flex-wrap items-center justify-between gap-2 py-2 shrink-0">
					<div class="flex items-center gap-3">
						<div class="w-1.5 h-1.5 rounded-full bg-indigo-600"></div>
						<h3 class="text-[10px] font-bold text-slate-900 uppercase tracking-[0.2em]">
							{{ success ? 'Confirmed' : booked ? 'Review & Pay' : 'Appointment Booking' }}
						</h3>
					</div>
					<!-- Compact Step Indicator -->
					<div v-if="!success" class="flex items-center gap-4">
						<div class="flex gap-1">
							<div v-for="step in intervalCount" :key="step" 
								class="h-1 rounded-full transition-all duration-500"
								:class="step <= currentStep ? 'w-4 bg-indigo-600' : 'w-1 bg-slate-100'"
							></div>
						</div>
						<span class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Step {{ currentStep }}/{{ intervalCount }}</span>
					</div>
				</div>

				<div class="flex-1 flex flex-col overflow-hidden relative">
					
					<!-- 1. Compact Specialty/Expert Selection -->
					<div v-if="!show_calendar && !booked && !success" class="flex-1 overflow-y-auto px-4 md:px-10 py-5 md:py-8 animate-fade-in custom-scrollbar">
						<div class="max-w-4xl mx-auto">
							<div class="mb-8">
								<h2 class="text-lg font-bold text-slate-900">{{ currentStep === 1 ? 'Select Specialty' : 'Choose Practitioner' }}</h2>
								<p class="text-xs text-slate-400 mt-1">Please select the appropriate department or doctor to continue.</p>
							</div>
							
							<DepartmentSelector v-if="currentStep === 1 && departments.length > 1"
								:items="paginatedDepartments" :selected="selectedDepartment"
								:page="deptPage" :totalPages="totalDeptPages"
								@update:selected="handleDepartmentSelection" @update:page="deptPage = $event"
							/>

							<PractitionerSelector v-else
								:items="paginatedPractitioners" :selected="selectedPractitioner"
								:page="practitionerPage" :totalPages="totalPractitionerPages"
								@update:page="practitionerPage = $event" @book="handlePractitionerSelection"
							/>
						</div>
					</div>

					<!-- 2. Integrated "Studio" Booking View -->
					<div v-if="show_calendar && !booked && !success" class="flex-1 flex flex-col lg:flex-row divide-y lg:divide-y-0 lg:divide-x divide-slate-100 overflow-y-auto lg:overflow-hidden animate-fade-in custom-scrollbar">
						
						<!-- Slim Left Sidebar: Practitioner & Patient -->
						<div class="w-full lg:w-64 bg-slate-50/50 flex flex-col p-4 md:p-6 shrink-0">
							<div class="flex items-center gap-3 mb-8">
								<img v-if="selectedPractitioner.image" :src="selectedPractitioner.image" class="w-10 h-10 rounded-lg object-cover shadow-sm" />
								<div v-else class="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center text-white text-xs font-bold">{{ selectedPractitioner.practitioner_name.charAt(0) }}</div>
								<div class="min-w-0">
									<h4 class="text-xs font-bold text-slate-900 truncate">{{ selectedPractitioner.practitioner_name }}</h4>
									<p class="text-[9px] font-bold text-indigo-600 uppercase tracking-widest mt-0.5">{{ selectedPractitioner.department }}</p>
								</div>
							</div>

							<div class="space-y-6">
								<div>
									<span class="text-[9px] font-bold text-slate-400 uppercase tracking-widest block mb-2">Patient Profile</span>
									<FormControl v-model="selectedPatient" type="autocomplete" :options="patientOptions" size="sm" class="compact-input" />
								</div>
								
								<!-- Minimalist Relative Details -->
								<div v-if="isNewPatient" class="space-y-3 pt-4 border-t border-slate-200 animate-slide-in">
									<div class="grid grid-cols-2 gap-2">
										<FormControl v-model="relativeDetails.first_name" label="First Name *" size="sm" />
										<FormControl v-model="relativeDetails.last_name" label="Last Name" size="sm" />
									</div>
									<div class="grid grid-cols-2 gap-2">
										<FormControl v-model="relativeDetails.sex" type="select" :options="['Male', 'Female', 'Other']" label="Gender" size="sm" />
										<FormControl v-model="relativeDetails.relation" type="select" :options="['Self', 'Family', 'Other']" label="Relation" size="sm" />
									</div>
									<FormControl v-model="relativeDetails.mobile_number" label="Mobile *" size="sm" />
									<FormControl v-model="relativeDetails.email" label="Email *" size="sm" />
								</div>
							</div>
						</div>

						<!-- Center: Precise Calendar -->
						<div class="flex-1 flex flex-col items-center justify-center p-4 md:p-8 bg-white">
							<div class="w-full max-w-sm">
								<span class="text-[9px] font-bold text-slate-300 uppercase tracking-[0.2em] block mb-8 text-center">Select Date</span>
								<Calendar v-model:selectedDate="selectedDate" size="sm" />
							</div>
						</div>

						<!-- Right: Compact Slots -->
						<div class="w-full lg:w-80 flex flex-col p-4 md:p-8 bg-white border-t lg:border-t-0 border-slate-100">
							<span class="text-[9px] font-bold text-slate-300 uppercase tracking-[0.2em] block mb-6">Available Time Slots</span>
							
							<div class="flex-1 overflow-y-auto custom-scrollbar">
								<div v-if="slots.length" class="space-y-6">
									<div v-for="(group, label) in groupedSlots" :key="label">
										<div v-if="group.length">
											<h5 class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-3">{{ label }}</h5>
											<div class="grid grid-cols-2 gap-2">
												<button v-for="slot in group" :key="slot.slot" @click="selectedSlot = slot"
													class="py-2.5 rounded-lg text-[10px] font-bold uppercase transition-all border"
													:class="selectedSlot?.slot === slot.slot 
														? 'bg-slate-900 border-slate-900 text-white shadow-md' 
														: 'bg-white border-slate-100 text-slate-400 hover:border-indigo-400 hover:text-indigo-600'"
												>
													{{ slot.formattedTime }}
												</button>
											</div>
										</div>
									</div>
								</div>
								<div v-else class="h-full flex flex-col items-center justify-center opacity-30 italic text-xs">
									<ClockIcon class="w-6 h-6 mb-2" />
									Select a date...
								</div>
							</div>

							<!-- Slim Selection Footer -->
							<div v-if="selectedSlot" class="mt-6 pt-6 border-t border-slate-50 animate-fade-up">
								<div class="flex items-center justify-between text-xs font-bold text-slate-900">
									<span class="text-slate-400 font-medium">Selected</span>
									<span>{{ selectedDate }} at {{ selectedSlot.formattedTime }}</span>
								</div>
							</div>
						</div>
					</div>

					<!-- 3. Final Step Views -->
					<div v-if="booked && !success" class="flex-1 flex flex-col items-center justify-center p-10 animate-fade-in">
						<div class="w-full max-w-sm">
							<Payment v-model:practitioner="selectedPractitioner.practitioner_name"
								v-model:consultationFee="consultationFee" v-model:currency="currency"
								@payment_success="() => success = true" />
						</div>
					</div>

					<div v-if="success" class="flex-1 flex flex-col items-center justify-center p-10 text-center animate-fade-in">
						<div class="w-16 h-16 rounded-2xl bg-green-50 flex items-center justify-center text-green-500 mb-6 border border-green-100 shadow-sm">
							<CheckCircleIcon class="w-8 h-8" />
						</div>
						<h2 class="text-lg font-bold text-slate-900">Session Confirmed</h2>
						<p class="text-xs text-slate-400 mt-2 max-w-[240px]">Appointment with {{ selectedPractitioner.practitioner_name }} is secured.</p>
						<button @click="reload_appointments" class="mt-8 px-8 py-3 bg-slate-900 rounded-xl text-white text-[10px] font-bold uppercase tracking-widest shadow-lg hover:bg-slate-800 transition-all">
							Finish
						</button>
					</div>
				</div>

				<!-- Floating Action Footer -->
				<div v-if="!success" class="px-4 md:px-6 h-16 border-t border-slate-50 flex justify-between items-center bg-white shrink-0">
					<Button v-if="currentStep > 1" variant="subtle" size="sm" class="!px-6 !text-[10px] font-bold uppercase" @click="goToPrevious()">
						Back
					</Button>
					<div class="flex-1"></div>
					<Button v-if="!show_calendar && !booked" :disabled="!((selectedDepartment && currentStep===1) || (selectedPractitioner && currentStep===2))"
						variant="solid" size="sm" class="!px-8 !bg-slate-900 !text-[10px] font-bold uppercase tracking-widest" @click="goToNext()">
						Continue
					</Button>
					<Button v-else-if="show_calendar && !booked" :disabled="!selectedSlot"
						variant="solid" size="sm" class="!px-8 !bg-indigo-600 !text-[10px] font-bold uppercase tracking-widest shadow-md shadow-indigo-100"
						:loading="bookingLoading" @click="bookSlot()">
						Book Slot
					</Button>
					<div v-else-if="booked" class="flex items-center gap-3">
						<Button variant="subtle" size="sm" class="!px-5 !text-[10px] font-bold uppercase tracking-widest text-slate-400" @click="payLater()">
							Pay Later
						</Button>
						<Button variant="solid" size="sm" class="!px-8 !bg-indigo-600 !text-[10px] font-bold uppercase tracking-widest" @click="generatePaymentLink()">
							Pay Now
						</Button>
					</div>
				</div>
			</div>
			<ErrorMessage v-if="error" class="p-4 mx-6 mb-6" :message="error" />
		</template>
	</Dialog>
</template>

<style scoped>
.compact-input :deep(input) {
	@apply text-xs h-9 bg-slate-50 border-none rounded-lg transition-all;
}
.compact-input :deep(input):focus {
	box-shadow: 0 0 0 2px #e0e7ff; /* indigo-100 ring approximation */
	outline: none;
}

.custom-scrollbar::-webkit-scrollbar {
	width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
	background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
	background: #f1f5f9;
	border-radius: 4px;
}
</style>

<script setup>
import {
	createResource,
	Button,
	Dialog,
	FormControl,
	ErrorMessage,
	toast,
} from 'frappe-ui'
import { computed, ref, watch, onMounted } from 'vue'
import DepartmentSelector from '@/components/DepartmentSelector.vue'
import PractitionerSelector from '@/components/PractitionerSelector.vue'
import Calendar from '@/components/Calendar.vue'
import Payment from '@/components/Payment.vue'
import { 
	ClockIcon, 
	CheckIcon, 
	CheckCircleIcon,
	CalendarIcon
} from 'lucide-vue-next'

const props = defineProps({
	practitioner: {
		type: Object,
		default: null
	},
	reschedule_appointment: {
		type: Object,
		default: null
	}
})

const show = defineModel();

let departments = ref([]);
let practitioners = ref([]);
let slots = ref([]);
const patientOptions = ref([])
const selectedPatient = ref(JSON.parse(localStorage.getItem("patient")) || {})
const selectedDepartment = ref(null);
const selectedPractitioner = ref(null);
const selectedDate = ref(null);
let selectedSlot = ref(null);

const isNewPatient = computed(() => {
	const val = selectedPatient.value?.value || selectedPatient.value;
	return val === 'new';
})

let appointment = ref(null);

const relativeDetails = ref({
	first_name: '',
	last_name: '',
	sex: '',
	dob: '',
	email: '',
	relation: '',
	mobile_number: ''
})

let alert_dialog = ref(false);
let show_calendar = ref(false);
let booked = ref(false);
let success = ref(false);
let bookingLoading = ref(false);

let dialog_title = ref("");
let dialog_message = ref("");
let error = ref("");

let currentStep = ref(1)
let intervalCount = ref(2);
const currency = ref("")

const fetchPatients = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_patients",
	method: "GET",
	onSuccess(response) {
		if (response && response.length > 0) {
			patientOptions.value = response;
			const storedPatient = JSON.parse(localStorage.getItem("patient"));
			if (storedPatient) {
				const match = response.find(p => p.value === storedPatient.value);
				if (match) selectedPatient.value = match;
			} else if (response.length === 1) {
				selectedPatient.value = response[0];
			}
		}
	},
});

onMounted(() => {
	error.value = null;
	fetchDepartments.fetch();
	fetchPatients.fetch();
	
	// Handle reschedule - skip to calendar directly
	if (props.reschedule_appointment) {
		initializeReschedule(props.reschedule_appointment);
	} else if (props.practitioner) {
		initializeDirectBooking(props.practitioner);
	}
});

watch(() => props.practitioner, (newPractitioner) => {
	if (newPractitioner) {
		initializeDirectBooking(newPractitioner);
	}
});

function initializeDirectBooking(practitioner) {
	selectedPractitioner.value = practitioner;
	selectedDepartment.value = practitioner.department;
	show_calendar.value = true;
	
	// Calculate current step based on entry point
	let steps = 2; // Practitioner -> Slot
	if (departments.value.length > 1) steps++; // Dept -> Practitioner -> Slot
	
	// If direct, we are at the "Calendar/Slots" step
	currentStep.value = steps;
}

// Initialize reschedule mode - skip directly to calendar/slot selection
function initializeReschedule(appointment) {
	// Create a practitioner-like object from the appointment data
	selectedPractitioner.value = {
		name: appointment.practitioner,
		practitioner_name: appointment.practitioner_name || appointment.title?.split(' with ')[1] || appointment.practitioner,
		department: appointment.department,
		designation: appointment.designation || 'Practitioner',
		image: appointment.practitioner_image || null
	};
	selectedDepartment.value = appointment.department;
	show_calendar.value = true;
	
	// For reschedule, we go directly to calendar step
	// Calculate step number (it should be the calendar step)
	let steps = 2;
	if (departments.value.length > 1) steps++;
	if (healthcareSettings.value.collect_payment) steps++;
	
	// Set to the calendar step (which is steps - 1 if payment exists, or just the last step before payment)
	currentStep.value = healthcareSettings.value.collect_payment ? steps - 1 : steps;
}

const deptPage = ref(1);
const practitionerPage = ref(1);
const itemsPerPage = 8;
const consultationFee = ref(0)
const registrationFee = ref(0)

let healthcareSettings = ref({});
let getHealthcareSettings = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_settings",
	method: "GET",
	onSuccess(response) {
		if (response) {
			healthcareSettings.value = response
		}
	},
});
getHealthcareSettings.fetch();

const totalDeptPages = computed(() => Math.ceil(departments.value.length / itemsPerPage));
const totalPractitionerPages = computed(() => Math.ceil(practitioners.value.length / itemsPerPage));

const paginatedDepartments = computed(() => {
	const start = (deptPage.value - 1) * itemsPerPage
	return departments.value.slice(start, start + itemsPerPage)
});

const paginatedPractitioners = computed(() => {
	const start = (practitionerPage.value - 1) * itemsPerPage
	return practitioners.value.slice(start, start + itemsPerPage)
});

let fetchDepartments = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_departments",
	method: "GET",
	onSuccess(response) {
		if (response) {
			departments.value = response;
			if (response.length === 1 && !selectedDepartment.value) {
				selectedDepartment.value = response[0].department
				fetchPractitioners(selectedDepartment.value);
			}
		}
	},
});

watch([() => departments.value.length, () => healthcareSettings.value.collect_payment], ([deptLength, collectPayment]) => {
	let steps = 2; // Practitioner -> Slot
	if (deptLength > 1) steps++; // Dept -> Practitioner -> Slot
	if (collectPayment) steps++; // ... -> Payment
	intervalCount.value = steps;
})

const progressCount = computed(() => (currentStep.value / intervalCount.value) * 100)

const handleDepartmentSelection = (dept) => {
	selectedDepartment.value = dept;
	fetchPractitioners(dept);
	goToNext();
}

const handlePractitionerSelection = (pract) => {
	selectedPractitioner.value = pract;
	show_calendar.value = true;
	goToNext();
}

function fetchPractitioners(deptName) {
	createResource({
		url: "/api/method/healthcare.healthcare.api.patient_portal.get_practitioners",
		method: "GET",
		makeParams() {
			return { department: deptName };
		},
		onSuccess(response) {
			if (response) practitioners.value = response;
		},
	}).fetch();
}

async function fetchSlots(date) {
	if (!selectedPractitioner.value) return;
	const slotResource = createResource({
		url: "/api/method/healthcare.healthcare.api.patient_portal.get_slots",
		method: "GET",
		makeParams() {
			return {
				practitioner: selectedPractitioner.value.name,
				date: date
			};
		},
		onSuccess(response) {
			if (date === selectedDate.value) slots.value = response || [];
		},
	});
	await slotResource.fetch();
}

function fetchFees(pract, date) {
	createResource({
		url: "/api/method/healthcare.healthcare.api.patient_portal.get_fees",
		method: "GET",
		makeParams() {
			return { practitioner: pract, date: date };
		},
		onSuccess(response) {
			if (response) {
				currency.value = response.default_currency;
				consultationFee.value = response?.details?.practitioner_charge || 0;
			}
		},
	}).fetch();
}

async function bookSlot() {
	error.value = null;
	if (isNewPatient.value) {
		const rd = relativeDetails.value;
		if (!rd.first_name || !rd.mobile_number || !rd.email) {
			toast.error("Please fill in all mandatory patient details (First Name, Mobile Number, and Email).");
			return;
		}
	}
	if (!selectedDate.value || !selectedSlot.value) {
		toast.error("Please select a date and time slot.");
		return;
	}

	try {
		bookingLoading.value = true;
		
		// Get CSRF token from window globals
		const csrfToken = window.csrf_token || window.frappe?.csrf_token || '';
		
		const patientValue = selectedPatient.value?.value || selectedPatient.value;
		const params = {
			practitioner: selectedPractitioner.value.name,
			patient: patientValue,
			date: selectedDate.value,
			slot: selectedSlot.value.slot,
			appointment_id: props.reschedule_appointment ? props.reschedule_appointment.name : null,
			relative_details: patientValue === 'new' ? relativeDetails.value : null
		};
		
		const response = await fetch('/api/method/healthcare.healthcare.api.patient_portal.make_appointment', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
				'X-Frappe-CSRF-Token': csrfToken
			},
			body: JSON.stringify(params)
		});
		
		const data = await response.json();
		
		if (!response.ok) {
			// Handle error response
			let errorMsg = 'Failed to book appointment';
			if (data._server_messages) {
				try {
					const messages = JSON.parse(data._server_messages);
					let msg = messages[0];
					if (typeof msg === 'string' && msg.startsWith('{')) {
						const parsedMsg = JSON.parse(msg);
						msg = parsedMsg.message || msg;
					}
					errorMsg = msg?.replace(/<[^>]*>/g, '') || errorMsg;
				} catch (e) {
					errorMsg = data._server_messages;
				}
			} else if (data.exception) {
				errorMsg = data.exception;
			} else if (data.message) {
				errorMsg = data.message;
			}
			const formattedError = typeof errorMsg === 'string' ? errorMsg.replace(/<[^>]*>/g, '') : errorMsg;
			toast.error(String(formattedError));
			return;
		}
		
		// Success - data.message contains the appointment doc
		if (data.message) {
			appointment.value = data.message;
			show_calendar.value = false;
			booked.value = true;
			currentStep.value = intervalCount.value;
			if (!healthcareSettings.value.collect_payment) success.value = true;
		}
	} catch (e) {
		console.error('Booking error:', e);
		toast.error('An unexpected error occurred. Please try again.');
	} finally {
		bookingLoading.value = false;
	}
}

function goToNext() {
	error.value = null;
	if (currentStep.value < intervalCount.value) {
		currentStep.value++;
	}
}

function goToPrevious() {
	error.value = null;
	if (booked.value) {
		booked.value = false;
		show_calendar.value = true;
		currentStep.value--;
	} else if (show_calendar.value) {
		// If direct booking, close dialog on back from calendar
		if (props.practitioner) {
			show.value = false;
		} else {
			show_calendar.value = false;
			currentStep.value--;
			selectedDate.value = null;
			selectedSlot.value = null;
		}
	} else {
		currentStep.value--;
	}
}

watch(selectedDate, async (date) => {
	selectedSlot.value = null;
	slots.value = [];
	if (date && selectedPractitioner.value) {
		await fetchSlots(date);
		fetchFees(selectedPractitioner.value?.name, date);
	}
});

const groupedSlots = computed(() => {
	const groups = { "Morning": [], "Afternoon": [], "Evening": [] }
	if (!slots.value.length) return groups;

	slots.value.forEach(slot => {
		const hour = parseInt(slot.split(':')[0]);
		const formattedTime = new Date(`2000-01-01T${slot}:00`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
		const slotObj = { formattedTime, slot };
		
		if (hour < 12) groups.Morning.push(slotObj);
		else if (hour < 17) groups.Afternoon.push(slotObj);
		else groups.Evening.push(slotObj);
	});
	return groups;
});

const emit = defineEmits(['appointment_booked'])

function reload_appointments() {
	show.value = false;
	emit('appointment_booked')
}

import { useRouter } from 'vue-router'
const router = useRouter()

function payLater() {
	// Appointment is already booked. Skip payment — patient pays at the clinic.
	success.value = true
	setTimeout(() => {
		show.value = false;
		router.push(`/payment/${appointment.value.name}`)
	}, 1500)
}

const generatePaymentLink = () => {
	createResource({
		url: 'healthcare.healthcare.api.patient_portal.get_payment_link',
		makeParams() {
			return {
				doctype: 'Patient Appointment',
				docname: appointment.value?.name,
				title: appointment.value?.title,
				amount: consultationFee.value + registrationFee.value,
				total_amount: consultationFee.value + registrationFee.value,
				currency: currency.value,
				patient: appointment.value?.patient,
				redirect_to: `/patient_portal#/payment/${appointment.value?.name}`,
			}
		},
		onSuccess(data) {
			if (data && data.includes('<form')) {
				const div = document.createElement('div')
				div.style.display = 'none'
				div.innerHTML = data
				document.body.appendChild(div)
				const form = div.querySelector('form')
				if (form) form.submit()
			} else if (data) {
				window.location.href = data
			}
		},
		onError(err) {
			toast.error(err.messages?.[0] || err)
		},
	}).submit();
}
</script>



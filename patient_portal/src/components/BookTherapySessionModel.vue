<template>
	<Dialog v-if="show" v-model="show" :options="{ size: '6xl', title: 'Book Therapy Session' }" :disable-outside-click-to-close="true">
		<template #body-content>
			<div class="flex flex-col min-h-[85vh] bg-white rounded-[32px] overflow-hidden">
				<div class="px-10 pt-10 pb-6 flex items-center justify-between">
					<div>
						<h3 class="text-2xl font-black text-slate-900 tracking-tight">Book Therapy Session</h3>
						<p class="text-slate-400 text-sm font-medium mt-1">Schedule your next therapy session</p>
					</div>
					<div v-if="!success" class="flex flex-col items-end gap-2">
						<span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">
							Step {{ currentStep }} / {{ totalSteps }}
						</span>
					</div>
				</div>

				<div class="flex-1 overflow-y-auto px-10 pb-10 custom-scrollbar">
					<!-- Step 1: Select Plan & Therapy Type -->
					<div v-if="currentStep === 1" class="animate-fade-in space-y-8">
						<div>
							<p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Select Therapy Plan</p>
							<div v-if="fetchPlans.loading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div v-for="i in 2" :key="i" class="h-32 bg-slate-50 animate-pulse rounded-2xl"></div>
							</div>
							<div v-else-if="therapyPlans.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div v-for="plan in therapyPlans" :key="plan.name"
									@click="selectPlan(plan)"
									class="p-6 rounded-2xl border-2 transition-all cursor-pointer"
									:class="[
										selectedPlan?.name === plan.name 
										? 'border-brand-orange bg-brand-orange/5' 
										: 'border-slate-100 hover:border-slate-200 bg-slate-50'
									]"
								>
									<div class="flex items-center justify-between mb-2">
										<h4 class="font-bold text-slate-900">{{ plan.therapy_plan_template || 'Custom Plan' }}</h4>
										<span class="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-white border border-slate-100">
											{{ plan.status }}
										</span>
									</div>
									<p class="text-xs text-slate-500 mb-4">{{ plan.name }}</p>
									<div class="flex items-center gap-4">
										<div class="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
											<div class="h-full bg-brand-orange transition-all duration-500" 
												:style="{ width: (plan.total_sessions_completed / plan.total_sessions * 100) + '%' }"></div>
										</div>
										<span class="text-[10px] font-bold text-slate-400">
											{{ plan.total_sessions_completed }}/{{ plan.total_sessions }}
										</span>
									</div>
								</div>
							</div>
							<div v-else class="text-center py-10 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-100">
								<p class="text-slate-400 font-bold">No active therapy plans found.</p>
							</div>
						</div>

						<div v-if="selectedPlan">
							<p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Select Therapy Type</p>
							<div class="grid grid-cols-2 md:grid-cols-3 gap-3">
								<button v-for="type in therapyTypes" :key="type.therapy_type"
									@click="selectedType = type.therapy_type"
									class="py-4 px-4 rounded-xl text-sm font-bold transition-all border text-center"
									:class="[
										selectedType === type.therapy_type 
										? 'bg-slate-900 text-white border-slate-900 shadow-lg shadow-slate-200' 
										: 'bg-white text-slate-600 border-slate-100 hover:border-brand-orange hover:text-brand-orange'
									]"
								>
									{{ type.therapy_type }}
									<div class="text-[10px] opacity-60 mt-1">
										{{ type.sessions_completed }}/{{ type.no_of_sessions }} sessions
									</div>
								</button>
							</div>
						</div>
					</div>

					<!-- Step 2: Select Date & Time -->
					<div v-if="currentStep === 2" class="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fade-in">
						<div>
							<p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6 text-center">Select Date</p>
							<Calendar v-model:selectedDate="selectedDate" />
						</div>
						<div class="flex flex-col h-full">
							<!-- Practitioner Selection First -->
							<p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 text-center">Select Practitioner</p>
							<FormControl
								v-model="selectedPractitioner"
								type="select"
								:options="practitionerOptions"
								class="!rounded-2xl mb-8"
								placeholder="Choose a therapist"
							/>

							<p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6 text-center">Available Time Slots</p>
							
							<div v-if="fetchSlots.loading" class="flex-1 flex items-center justify-center">
								<div class="animate-spin w-6 h-6 border-2 border-slate-200 border-t-slate-800 rounded-full"></div>
							</div>
							
							<div v-else-if="availableSlots.length" class="flex-1 overflow-y-auto custom-scrollbar pr-2">
								<div v-for="(group, label) in groupedSlots" :key="label" class="mb-6">
									<div v-if="group.length">
										<h5 class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-3 sticky top-0 bg-white py-1">{{ label }}</h5>
										<div class="grid grid-cols-2 gap-2">
											<button v-for="slot in group" :key="slot.period" @click="selectedSlot = slot"
												class="py-3 rounded-xl text-xs font-bold transition-all border"
												:class="selectedSlot?.period === slot.period 
													? 'bg-slate-900 border-slate-900 text-white shadow-lg shadow-slate-200 transform scale-105' 
													: 'bg-white border-slate-100 text-slate-500 hover:border-brand-orange hover:text-brand-orange'"
											>
												{{ slot.formattedTime }}
											</button>
										</div>
									</div>
								</div>
							</div>
							
							<div v-else class="flex-1 flex flex-col items-center justify-center text-center opacity-50">
								<ClockIcon class="w-8 h-8 mb-3 text-slate-300" />
								<p class="text-xs font-bold text-slate-400">
									{{ !selectedDate ? 'Select a date first' : !selectedPractitioner ? 'Select a practitioner' : 'No slots available' }}
								</p>
							</div>
						</div>
					</div>

					<!-- Step 3: Confirmation -->
					<div v-if="currentStep === 3" class="animate-fade-in flex flex-col items-center justify-center py-10 text-center">
						<div class="w-20 h-20 bg-brand-orange/10 rounded-[32px] flex items-center justify-center mb-8">
							<ActivityIcon class="w-10 h-10 text-brand-orange" />
						</div>
						<h2 class="text-3xl font-black text-slate-900 tracking-tight">Confirm Booking</h2>
						<p class="text-slate-500 font-medium mt-2">Please review your session details</p>

						<div class="mt-8 p-8 bg-slate-50 rounded-[32px] border border-slate-100 w-full max-w-md space-y-4">
							<div class="flex justify-between">
								<span class="text-xs font-bold text-slate-400 uppercase">Plan</span>
								<span class="text-sm font-black text-slate-900">{{ selectedPlan?.therapy_plan_template }}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-xs font-bold text-slate-400 uppercase">Therapy</span>
								<span class="text-sm font-black text-slate-900">{{ selectedType }}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-xs font-bold text-slate-400 uppercase">Schedule</span>
								<span class="text-sm font-black text-slate-900">{{ selectedDate }} at {{ selectedSlot?.formattedTime }}</span>
							</div>
							<div v-if="selectedPractitioner" class="flex justify-between">
								<span class="text-xs font-bold text-slate-400 uppercase">Therapist</span>
								<span class="text-sm font-black text-slate-900">{{ practitionerDisplayLabel }}</span>
							</div>
							<div v-if="sessionFee > 0" class="flex justify-between pt-4 border-t border-slate-200">
								<span class="text-xs font-bold text-slate-400 uppercase">Fee</span>
								<span class="text-sm font-black text-slate-900">{{ currency }} {{ sessionFee }}</span>
							</div>
						</div>
					</div>

					<!-- Step 4: Payment -->
					<div v-if="currentStep === 4 && !success" class="animate-fade-in">
						<Payment
							v-model:practitioner="practitionerDisplay"
							v-model:consultationFee="sessionFee"
							v-model:error="error"
							v-model:currency="currency"
						/>
					</div>

					<!-- Success -->
					<div v-if="success" class="flex flex-col items-center justify-center py-20 animate-fade-in text-center">
						<div class="w-24 h-24 bg-green-50 rounded-[40px] flex items-center justify-center shadow-2xl shadow-green-100 animate-bounce-in mb-8">
							<CheckCircleIcon class="w-12 h-12 text-green-500" />
						</div>
						<h2 class="text-4xl font-black text-slate-900 tracking-tight">Booking Confirmed</h2>
						<p class="text-slate-400 font-medium mt-2">Your therapy session has been scheduled.</p>
					</div>
				</div>

				<!-- Footer -->
				<div v-if="!success" class="px-10 py-8 border-t border-slate-50 bg-white flex justify-between items-center">
					<Button
						variant="subtle"
						class="!px-8 !rounded-2xl font-bold !text-slate-400"
						@click="currentStep > 1 ? currentStep-- : show = false"
					>
						{{ currentStep === 1 ? 'Cancel' : 'Back' }}
					</Button>
					
					<Button
						v-if="currentStep < 3"
						:disabled="!isNextDisabled"
						variant="solid"
						class="!px-10 !py-6 !rounded-2xl !bg-slate-900 font-black tracking-widest text-xs uppercase"
						@click="currentStep++"
					>
						Continue
					</Button>
					
					<Button
						v-else-if="currentStep === 3"
						variant="solid"
						class="!px-10 !py-6 !rounded-2xl !bg-brand-orange font-black tracking-widest text-xs uppercase shadow-xl shadow-brand-orange/20"
						:loading="bookingLoading"
						@click="bookSession"
					>
						{{ healthcareSettings.collect_payment && sessionFee > 0 ? 'Proceed to Payment' : 'Confirm Session' }}
					</Button>

					<Button
						v-else-if="currentStep === 4"
						variant="solid"
						class="!px-10 !py-6 !rounded-2xl !bg-brand-orange font-black tracking-widest text-xs uppercase shadow-xl shadow-brand-orange/20"
						@click="generatePaymentLink"
					>
						Pay Now
					</Button>
				</div>
				<div v-else class="px-10 py-8 flex justify-center">
					<Button
						variant="solid"
						class="!px-16 !py-6 !rounded-2xl !bg-slate-900 font-black tracking-widest text-xs uppercase"
						@click="closeSuccess"
					>
						Done
					</Button>
				</div>
			</div>
		</template>
	</Dialog>

	<Dialog v-if="showWarning" v-model="showWarning" :options="{ size: 'md', title: 'Plan Completed' }">
		<template #body-content>
			<div class="p-6 text-center">
				<div class="w-16 h-16 bg-orange-50 rounded-full flex items-center justify-center mx-auto mb-4">
					<ActivityIcon class="w-8 h-8 text-orange-500" />
				</div>
				<h3 class="text-lg font-bold text-slate-900 mb-2">Therapy Plan Completed</h3>
				<p class="text-slate-500 text-sm mb-6">
					This therapy plan has been completed. Kindly select another active plan or book a new plan.
				</p>
				<Button variant="solid" @click="showWarning = false" class="w-full">
					Okay, Got it
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { createResource, Button, Dialog, FormControl, toast } from 'frappe-ui'
import { ActivityIcon, CheckCircleIcon, ClockIcon } from 'lucide-vue-next'
import Calendar from '@/components/Calendar.vue'
import Payment from '@/components/Payment.vue'

const props = defineProps({
	plan: {
		type: Object,
		default: null
	}
})

const show = defineModel()
const currentStep = ref(1)
const bookingLoading = ref(false)
const success = ref(false)
const error = ref(null)
const showWarning = ref(false)

const selectedPlan = ref(null)
const selectedType = ref(null)
const selectedDate = ref(null)
const selectedSlot = ref(null)
const selectedPractitioner = ref(null)

const therapyPlans = ref([])
const therapyTypes = ref([])
const practitionerOptions = ref([])
const availableSlots = ref([])

const healthcareSettings = ref({})
const sessionFee = ref(0)
const currency = ref("")
const session = ref(null)

const practitionerDisplay = computed(() => {
    const selected = practitionerOptions.value.find(p => p.value === selectedPractitioner.value)
	return selected?.label || selectedPlan.value?.practitioner_name || 'Therapist'
})

const practitionerDisplayLabel = computed(() => {
    const selected = practitionerOptions.value.find(p => p.value === selectedPractitioner.value)
	return selected?.label
})

const totalSteps = computed(() => {
	if (healthcareSettings.value.collect_payment && sessionFee.value > 0) {
		return 4
	}
	return 3
})

onMounted(() => {
	fetchPlans.fetch()
	fetchPractitioners.fetch()
	fetchSettings.fetch()
})

const fetchSettings = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_settings",
	method: "GET",
	onSuccess(data) {
		healthcareSettings.value = data
	}
})

const fetchPlans = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_therapy_plans',
	method: 'GET',
	onSuccess(data) {
		therapyPlans.value = data
	}
})

const fetchPractitioners = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_practitioners',
	method: 'GET',
	onSuccess(data) {
		practitionerOptions.value = data.map(p => ({
			label: p.practitioner_name,
			value: p.name
		}))
	}
})

const fetchTypes = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_therapy_types_for_plan',
	method: 'GET',
	makeParams() {
		return { therapy_plan: selectedPlan.value?.name }
	},
	onSuccess(data) {
		therapyTypes.value = data
	}
})

const fetchSlots = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_slots',
	method: 'GET',
	makeParams() {
		return {
			practitioner: selectedPractitioner.value,
			date: selectedDate.value
		}
	},
	onSuccess(data) {
		availableSlots.value = data || []
	}
})

// Fetch fee when therapy type is selected
const fetchFee = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_therapy_type_fee',
	method: 'GET',
	makeParams() {
		return { therapy_type: selectedType.value }
	},
	onSuccess(data) {
		sessionFee.value = data.rate || 0
		currency.value = data.currency
	}
})

const selectPlan = (plan) => {
	console.log('Selected Plan:', plan.name, 'Status:', plan.status)
	if (plan.status && plan.status.trim().toLowerCase() === 'completed') {
		console.log('Triggering warning dialog...')
		showWarning.value = true
		return
	}
	console.log('Proceeding with plan selection...')
	selectedPlan.value = plan
	selectedType.value = null
	fetchTypes.fetch()
}

watch([selectedDate, selectedPractitioner], ([date, pract]) => {
	selectedSlot.value = null
	availableSlots.value = []
	if (date && pract) {
		fetchSlots.fetch()
	}
})

watch(selectedType, (val) => {
	if (val) {
		fetchFee.fetch()
	} else {
		sessionFee.value = 0
	}
})

const groupedSlots = computed(() => {
	const groups = { "Morning": [], "Afternoon": [], "Evening": [] }
	if (!availableSlots.value.length) return groups;

	availableSlots.value.forEach(slot => { // slot is time string e.g., "09:00:00"
		const timeStr = slot.split(':').slice(0, 2).join(':'); // Extract HH:MM
		const hour = parseInt(slot.split(':')[0]);
		const formattedTime = new Date(`2000-01-01T${slot}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
		const slotObj = { formattedTime, period: timeStr, full: slot };
		
		if (hour < 12) groups.Morning.push(slotObj);
		else if (hour < 17) groups.Afternoon.push(slotObj);
		else groups.Evening.push(slotObj);
	});
	return groups;
});

const isNextDisabled = computed(() => {
	if (currentStep.value === 1) return selectedPlan.value && selectedType.value
	if (currentStep.value === 2) return selectedDate.value && selectedPractitioner.value && selectedSlot.value
	return true
})

import { useRouter } from 'vue-router'
const router = useRouter()

const bookSession = async () => {
	bookingLoading.value = true
	try {
		const makeSession = createResource({
			url: 'healthcare.healthcare.api.patient_portal.make_therapy_session',
			method: 'POST',
			makeParams() {
				return {
					therapy_plan: selectedPlan.value.name,
					therapy_type: selectedType.value,
					start_date: selectedDate.value,
					start_time: selectedSlot.value.period,
					practitioner: selectedPractitioner.value
				}
			},
			onSuccess(data) {
				session.value = data
			}
		})
		
		await makeSession.submit()

		if (healthcareSettings.value.collect_payment && sessionFee.value > 0) {
			currentStep.value = 4
		} else {
			success.value = true
			setTimeout(() => {
				show.value = false;
				router.push(`/payment/${session.value.name}`)
				emit('booked')
			}, 1500)
		}
	} catch (error) {
		toast.error(error.messages?.[0] || 'Failed to book session')
	} finally {
		bookingLoading.value = false
	}
}

const paymentLink = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_payment_link',
	makeParams() {
		return {
			doctype: 'Therapy Session',
			docname: session.value?.name,
			title: 'Therapy Session',
			amount: sessionFee.value,
			total_amount: sessionFee.value,
			currency: currency.value,
			patient: session.value?.patient,
			redirect_to: `/patient_portal#/payment/${session.value?.name}`,
		}
	},
})

const generatePaymentLink = () => {
	paymentLink.submit(
		{},
		{
			onSuccess(data) {
				if (data && data.includes('<form')) {
					// Handle HTML form injection for gateways like GoPayFast
					const div = document.createElement('div')
					div.style.display = 'none'
					div.innerHTML = data
					document.body.appendChild(div)
					const form = div.querySelector('form')
					if (form) {
						form.submit()
					}
				} else if (data) {
					window.location.href = data
				}
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

const closeSuccess = () => {
	show.value = false
}

watch(show, (value) => {
	if (value) {
		success.value = false
		currentStep.value = 1
		error.value = null
		if (props.plan) {
			selectPlan(props.plan)
			currentStep.value = 1
		} else {
			selectedPlan.value = null
			selectedType.value = null
			currentStep.value = 1
		}
	}
})

const emit = defineEmits(['booked'])
</script>

<style scoped>
.animate-fade-in {
	animation: fadeIn 0.4s ease-out;
}

.animate-fade-up {
	animation: fadeUp 0.4s ease-out;
}

.animate-bounce-in {
	animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes fadeIn {
	from { opacity: 0; }
	to { opacity: 1; }
}

@keyframes fadeUp {
	from { opacity: 0; transform: translateY(10px); }
	to { opacity: 1; transform: translateY(0); }
}

@keyframes bounceIn {
	0% { transform: scale(0); opacity: 0; }
	70% { transform: scale(1.1); opacity: 1; }
	100% { transform: scale(1); opacity: 1; }
}
</style>

<template>
	<Dialog v-if="show" v-model="show" :options="{ size: '6xl' }" :disable-outside-click-to-close="true">
		<template #body-content>
			<div class="flex flex-col min-h-[85vh] bg-white rounded-[32px] overflow-hidden">
				<div class="px-10 pt-10 pb-6 flex items-center justify-between">
					<div>
						<h3 class="text-2xl font-black text-slate-900 tracking-tight">New Therapy Plan</h3>
						<p class="text-slate-400 text-sm font-medium mt-1">Start a new treatment journey</p>
					</div>
					<div class="flex flex-col items-end gap-2">
						<span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">
							Step {{ currentStep }} / {{ totalSteps }}
						</span>
					</div>
				</div>

				<div class="flex-1 overflow-y-auto px-10 pb-10 custom-scrollbar">
					<!-- Step 1: Select Template -->
					<div v-if="currentStep === 1" class="animate-fade-in space-y-6">
						<div>
							<p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Select Plan Template</p>
							<div class="grid grid-cols-1 gap-4">
								<div v-for="template in templates" :key="template.name"
									@click="selectTemplate(template)"
									class="p-6 rounded-2xl border-2 transition-all cursor-pointer group"
									:class="[
										selectedTemplate?.name === template.name 
										? 'border-brand-orange bg-brand-orange/5' 
										: 'border-slate-100 hover:border-slate-200 bg-slate-50'
									]"
								>
									<div class="flex items-center justify-between mb-2">
										<h4 class="font-bold text-slate-900 text-lg">{{ template.plan_name }}</h4>
										<div class="w-8 h-8 rounded-full border border-slate-200 flex items-center justify-center bg-white group-hover:scale-110 transition-transform">
											<div class="w-4 h-4 rounded-full" 
												:class="selectedTemplate?.name === template.name ? 'bg-brand-orange' : 'bg-slate-100'">
											</div>
										</div>
									</div>
									<div class="flex gap-4 text-xs text-slate-500 font-medium">
										<span v-if="template.total_sessions">{{ template.total_sessions }} Sessions</span>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Step 2: Configure Schedule & Book For -->
					<div v-if="currentStep === 2" class="animate-fade-in space-y-8">
						<!-- Booking For Section -->
						<div class="bg-slate-50 p-6 rounded-2xl border border-slate-100 mb-6">
							<h4 class="font-black text-slate-900 mb-4">Patient Details</h4>
							<FormControl
								v-model="bookingFor"
								type="select"
								:options="[
									{ label: 'Myself', value: 'Self' },
									{ label: 'Someone Else', value: 'Relative' }
								]"
								label="Booking For"
								class="mb-4 !rounded-2xl"
							/>
							
							<div v-if="bookingFor === 'Relative'" class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
								<FormControl v-model="relativeDetails.first_name" label="First Name" placeholder="Jane" />
								<FormControl v-model="relativeDetails.last_name" label="Last Name" placeholder="Doe" />
								<FormControl v-model="relativeDetails.gender" type="select" :options="['Male', 'Female', 'Other']" label="Gender" />
								<FormControl v-model="relativeDetails.mobile" label="Mobile Number" placeholder="+123..." />
								<FormControl v-model="relativeDetails.email" label="Email (Optional)" placeholder="jane@example.com" />
								<FormControl v-model="relativeDetails.dob" type="date" label="Date of Birth" />
							</div>
						</div>

						<div class="bg-slate-50 p-6 rounded-2xl border border-slate-100">
							<h4 class="font-black text-slate-900 mb-4">Scheduling Details</h4>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<FormControl
									v-model="selectedPractitioner"
									type="select"
									:options="practitionerOptions"
									label="Practitioner"
									placeholder="Select a therapist"
									class="!rounded-2xl"
								/>
								<FormControl
									v-model="frequency"
									type="select"
									:options="frequencyOptions"
									label="Frequency"
									class="!rounded-2xl"
								/>
								<div class="md:col-span-2">
									<label class="block text-xs text-gray-600 mb-1">Start Date</label>
									<Calendar v-model:selectedDate="startDate" />
								</div>
								<!-- "Schedule Now" toggle -->
								<div class="md:col-span-2 flex items-center gap-3 p-4 bg-white rounded-xl border border-slate-200">
									<input type="checkbox" v-model="scheduleNow" class="w-5 h-5 rounded border-gray-300 text-brand-orange focus:ring-brand-orange" />
									<div>
										<p class="font-bold text-slate-900 text-sm">Schedule sessions now</p>
										<p class="text-xs text-slate-500">Automatically book all {{ selectedTemplate?.total_sessions || 0 }} sessions</p>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Step 3: Review & Book Slots -->
					<div v-if="currentStep === 3" class="animate-fade-in space-y-6">
						<div class="flex items-center justify-between mb-4">
							<h4 class="font-black text-slate-900">Select Time Slots</h4>
							<Button size="sm" variant="outline" @click="generateSessionDates">Regenerate Dates</Button>
						</div>
						
						<div class="space-y-3">
							<div v-for="(session, index) in scheduledSessions" :key="index" 
								class="p-4 rounded-xl border border-slate-200 bg-white flex flex-col md:flex-row md:items-center gap-4 transition-all hover:border-brand-orange/30">
								<div class="flex-1">
									<span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Session {{ index + 1 }}</span>
									<div class="font-bold text-slate-900">{{ session.therapy_type }}</div>
								</div>
								<div class="flex-1">
									<FormControl
										v-model="session.start_date"
										type="date"
										size="sm"
										@change="fetchSlotsForSession(index)"
									/>
								</div>
								<div class="flex-1">
									<FormControl
										v-model="session.start_time"
										type="select"
										:options="session.available_slots || []"
										placeholder="Select Time"
										size="sm"
										:disabled="session.loading"
									/>
								</div>
							</div>
						</div>
					</div>
					
					<!-- Step 4: Confirmation (or skip to here if not scheduling) -->
					<div v-if="currentStep === 4" class="animate-fade-in flex flex-col items-center justify-center py-10 text-center">
						<div class="w-20 h-20 bg-brand-orange/10 rounded-[32px] flex items-center justify-center mb-8">
							<ActivityIcon class="w-10 h-10 text-brand-orange" />
						</div>
						<h2 class="text-3xl font-black text-slate-900 tracking-tight">Create Plan</h2>
						<p class="text-slate-500 font-medium mt-2">Confirm to start your new therapy plan</p>
						
						<div v-if="scheduledSessions.length && scheduleNow" class="mt-8 p-6 bg-slate-50 rounded-2xl w-full max-w-sm text-left text-sm space-y-2">
							<p><strong>Sessions to book:</strong> {{ scheduledSessions.length }}</p>
							<p><strong>Practitioner:</strong> {{ selectedPractitioner?.label }}</p>
							<p class="text-xs text-slate-400">All sessions will be created automatically.</p>
						</div>
					</div>
				</div>

				<!-- Footer -->
				<div class="px-10 py-8 border-t border-slate-50 bg-white flex justify-between items-center">
					<Button
						variant="subtle"
						class="!px-8 !rounded-2xl font-bold !text-slate-400"
						@click="currentStep > 1 ? currentStep-- : show = false"
					>
						{{ currentStep === 1 ? 'Cancel' : 'Back' }}
					</Button>
					
					<Button
						v-if="currentStep < totalSteps"
						:disabled="!isNextDisabled"
						variant="solid"
						class="!px-10 !py-6 !rounded-2xl !bg-slate-900 font-black tracking-widest text-xs uppercase"
						@click="handleNext"
					>
						Continue
					</Button>
					
					<Button
						v-else
						variant="solid"
						class="!px-10 !py-6 !rounded-2xl !bg-brand-orange font-black tracking-widest text-xs uppercase shadow-xl shadow-brand-orange/20"
						:loading="loading"
						@click="createPlan"
					>
						Confirm Plan
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { createResource, Button, Dialog, toast, FormControl } from 'frappe-ui'
import { ActivityIcon } from 'lucide-vue-next'
import Calendar from '@/components/Calendar.vue'
import { addDays, format } from 'date-fns'

const props = defineProps({
    initialTemplate: Object
})
const show = defineModel()
const emit = defineEmits(['created'])

watch(() => props.initialTemplate, (newVal) => {
    if (newVal) {
        selectTemplate(newVal)
        currentStep.value = 2 // Skip to step 2
    }
})

const currentStep = ref(1)
const loading = ref(false)
const templates = ref([])
const selectedTemplate = ref(null)

// Booking For State
const bookingFor = ref('Self')
const relativeDetails = ref({
    first_name: '',
    last_name: '',
    gender: '',
    mobile: '',
    email: '',
    dob: ''
})

// Scheduling State
const scheduleNow = ref(false)
const startDate = ref(null)
const selectedPractitioner = ref(null)
const frequency = ref('Weekly')
const frequencyOptions = ref([])
const practitionerOptions = ref([])
const scheduledSessions = ref([])
const templateDetails = ref([])

onMounted(() => {
	fetchTemplates.fetch()
	fetchPractitioners.fetch()
    fetchFrequencies.fetch()
})

const fetchFrequencies = createResource({
    url: 'healthcare.healthcare.api.patient_portal.get_therapy_plan_frequencies',
    method: 'GET',
    onSuccess(data) {
        // Fallback if backend API is empty or not yet seeded
        if (!data || !data.length) {
            frequencyOptions.value = [
                { label: 'Daily', value: 'Daily', duration_in_days: 1 },
                { label: 'Weekly', value: 'Weekly', duration_in_days: 7 }
            ]
        } else {
            frequencyOptions.value = data.map(f => ({
                label: f.frequency_name,
                value: f.name, // Use name as value for backend link, but we need duration for frontend calc
                duration_in_days: f.duration_in_days
            }))
        }
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

const fetchTemplates = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_therapy_plan_templates',
	method: 'GET',
	onSuccess(data) {
		templates.value = data
	}
})

// Add this resource to fetch therapy plan details (types) from template
const fetchTemplateDetails = createResource({
    url: 'frappe.client.get',
    method: 'GET',
    makeParams() {
        return {
            doctype: 'Therapy Plan Template',
            name: selectedTemplate.value?.name
        }
    },
    onSuccess(data) {
        templateDetails.value = data.therapy_types || [];
        if (scheduleNow.value) {
            generateSessionDates();
        }
    }
})

const selectTemplate = (template) => {
	selectedTemplate.value = template
    fetchTemplateDetails.fetch();
}

const totalSteps = computed(() => scheduleNow.value ? 4 : 2)

const handleNext = () => {
	if (currentStep.value === 2) {
		if (scheduleNow.value) {
			generateSessionDates()
            currentStep.value = 3
		} else {
            currentStep.value = 4
        }
	} else {
		currentStep.value++
	}
}

const isNextDisabled = computed(() => {
    if (currentStep.value === 1) return !selectedTemplate.value
    if (currentStep.value === 2) {
        if (bookingFor.value === 'Relative') {
            if (!relativeDetails.value.first_name || !relativeDetails.value.mobile) return true
        }
        if (scheduleNow.value) {
            return !selectedPractitioner.value || !startDate.value || !frequency.value
        }
    }
    return false
})

const generateSessionDates = () => {
    if (!startDate.value || !templateDetails.value.length) return;
    
    let sessions = [];
    let currentDate = new Date(startDate.value);
    
    // Find selected frequency duration
    const freqObj = frequencyOptions.value.find(f => f.value === frequency.value || f.label === frequency.value);
    const interval = freqObj ? (freqObj.duration_in_days || 7) : 7;
    
    // Flatten the therapy types based on no_of_sessions
    let typesToSchedule = [];
    templateDetails.value.forEach(type => {
        for(let i=0; i < type.no_of_sessions; i++) {
            typesToSchedule.push(type.therapy_type);
        }
    });
    
    typesToSchedule.forEach(type => {
        const dateStr = format(currentDate, 'yyyy-MM-dd')
        sessions.push({
            therapy_type: type,
            practitioner: selectedPractitioner.value?.value,
            start_date: dateStr,
            start_time: '',
            available_slots: [],
            loading: false
        });
        
        // Increment date based on Frequency
        currentDate = addDays(currentDate, interval);
    });
    
    scheduledSessions.value = sessions;
    
    // Fetch slots for the first few sessions automatically
    sessions.forEach((_, idx) => fetchSlotsForSession(idx));
}

const fetchSlotsForSession = async (index) => {
    const session = scheduledSessions.value[index];
    if (!session.start_date || !session.practitioner) return;
    
    session.loading = true;
    try {
        const slots = await frappe.call({
            method: 'healthcare.healthcare.api.patient_portal.get_slots',
            args: {
                practitioner: session.practitioner,
                date: session.start_date
            }
        });
        
        // Format slots for select
        session.available_slots = (slots.message || []).map(s => {
             const time = typeof s === 'string' ? s : s.slot;
             return {label: time, value: time}
        }); 
        
    } catch (e) {
        console.error(e);
        session.available_slots = [];
    } finally {
        session.loading = false;
    }
}


const createPlan = async () => {
	loading.value = true
	try {
		const result = await createResource({
			url: 'healthcare.healthcare.api.patient_portal.create_therapy_plan',
			makeParams() {
				return {
					template: selectedTemplate.value.name,
					patient: JSON.parse(localStorage.getItem('patient')).name,
                    sessions: scheduleNow.value ? JSON.stringify(scheduledSessions.value) : null,
                    relative_details: bookingFor.value === 'Relative' ? JSON.stringify(relativeDetails.value) : null,
                    frequency: frequency.value
				}
			}
		}).submit()
		
		toast.success('Therapy Plan created successfully!')
		emit('created')
		show.value = false
	} catch (error) {
		toast.error(error.messages?.[0] || 'Failed to create plan')
	} finally {
		loading.value = false
	}
}
</script>

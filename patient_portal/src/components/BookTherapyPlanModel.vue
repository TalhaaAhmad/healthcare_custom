<template>
	<Dialog v-if="show" v-model="show" :options="{ size: '6xl',title: 'New Therapy Plan' }" :disable-outside-click-to-close="true">
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
								v-model="selectedPatient"
								type="select"
								:options="patientOptions"
								label="Select Patient"
								class="mb-4 !rounded-2xl"
							/>
							
							<div v-if="isNewPatient" class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
								<FormControl v-model="relativeDetails.first_name" label="First Name" placeholder="Jane" />
								<FormControl v-model="relativeDetails.last_name" label="Last Name" placeholder="Doe" />
								<FormControl v-model="relativeDetails.gender" type="select" :options="['Male', 'Female', 'Other']" label="Gender" />
								<FormControl v-model="relativeDetails.mobile" label="Mobile Number" placeholder="+123..." />
								<FormControl v-model="relativeDetails.email" label="Email (Optional)" placeholder="jane@example.com" />
								<FormControl v-model="relativeDetails.dob" type="date" label="Date of Birth" />
							</div>
						</div>

						<div class="bg-slate-50 p-6 rounded-2xl border border-slate-100">
							<h4 class="font-black text-slate-900 mb-4">Plan Details</h4>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<FormControl
									v-model="frequency"
									type="select"
									:options="frequencyOptions"
									label="Frequency"
									class="!rounded-2xl"
								/>
								<div>
									<label class="block text-xs text-gray-600 mb-1">Start Date</label>
									<Calendar v-model:selectedDate="startDate" />
								</div>
							</div>
						</div>
					</div>

					<!-- Step 3: Confirmation -->
					<div v-if="currentStep === 3" class="animate-fade-in flex flex-col items-center justify-center py-10 text-center">
						<div class="w-20 h-20 bg-brand-orange/10 rounded-[32px] flex items-center justify-center mb-8">
							<ActivityIcon class="w-10 h-10 text-brand-orange" />
						</div>
						<h2 class="text-3xl font-black text-slate-900 tracking-tight">Create Plan</h2>
						<p class="text-slate-500 font-medium mt-2">Confirm to start your new therapy plan</p>
						
						<div class="mt-8 p-6 bg-slate-50 rounded-2xl w-full max-w-sm text-center text-sm space-y-2">
							<p><strong>Template:</strong> {{ selectedTemplate?.plan_name }}</p>
							<p><strong>Start Date:</strong> {{ startDate }}</p>
							<p><strong>Frequency:</strong> {{ frequency }}</p>
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
						:disabled="isNextDisabled"
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

// Patient Selection State (like appointment booking)
const patientOptions = ref([])
const selectedPatient = ref(null)
const relativeDetails = ref({
    first_name: '',
    last_name: '',
    gender: '',
    mobile: '',
    email: '',
    dob: ''
})

const isNewPatient = computed(() => {
    const val = selectedPatient.value;
    return val === 'new';
})

// Scheduling State
const startDate = ref(null)
const frequency = ref('Weekly')
const frequencyOptions = ref([])

const fetchPatients = createResource({
    url: 'healthcare.healthcare.api.patient_portal.get_patients',
    method: 'GET',
    onSuccess(response) {
        if (response && response.length > 0) {
            patientOptions.value = response;
            // Auto-select first patient if only one actual patient exists
            const actualPatients = response.filter(p => p.value !== 'new');
            if (actualPatients.length === 1) {
                selectedPatient.value = actualPatients[0].value;
            }
        }
    }
});

onMounted(() => {
	fetchTemplates.fetch()
    fetchFrequencies.fetch()
    fetchPatients.fetch()
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

const selectTemplate = (template) => {
	selectedTemplate.value = template
}

const totalSteps = 3

const handleNext = () => {
	currentStep.value++
}

const isNextDisabled = computed(() => {
    if (currentStep.value === 1) return !selectedTemplate.value
    if (currentStep.value === 2) {
        if (isNewPatient.value) {
            if (!relativeDetails.value.first_name || !relativeDetails.value.mobile) return true
        }
        return !startDate.value || !frequency.value
    }
    return false
})




const createPlan = async () => {
	loading.value = true
	try {
		let patientName = null;
        
        // Use the selected patient from the UI
        const patientValue = selectedPatient.value;
        
        if (!patientValue) {
             throw new Error('Please select a patient.');
        }

        if (patientValue === 'new') {
            patientName = 'new';
        } else {
            patientName = patientValue;
        }
		
		const planResource = createResource({
			url: 'healthcare.healthcare.api.patient_portal.create_therapy_plan',
			params: {
				template: selectedTemplate.value.name,
				patient: patientName,
				relative_details: isNewPatient.value ? JSON.stringify(relativeDetails.value) : null,
				frequency: frequency.value,
				start_date: startDate.value
			}
		});
		
		await planResource.submit();
		
		toast.success('Therapy Plan created successfully!')
		emit('created')
		show.value = false
	} catch (error) {
		console.error('Create plan error:', error);
		toast.error(error.messages?.[0] || error.message || 'Failed to create plan')
	} finally {
		loading.value = false
	}
}
</script>


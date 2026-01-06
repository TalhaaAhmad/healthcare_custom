<template>
	<div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50/30 flex items-center justify-center p-4">
		<!-- Decorative Background Elements -->
		<div class="fixed inset-0 overflow-hidden pointer-events-none">
			<div class="absolute -top-40 -right-40 w-80 h-80 bg-indigo-100/40 rounded-full blur-3xl"></div>
			<div class="absolute -bottom-40 -left-40 w-80 h-80 bg-orange-100/40 rounded-full blur-3xl"></div>
		</div>

		<!-- Registration Card -->
		<div class="relative w-full max-w-md">
			<!-- Logo & Header -->
			<div class="text-center mb-8">
				<div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl shadow-lg shadow-indigo-200 mb-4">
					<UserPlusIcon class="w-8 h-8 text-white" />
				</div>
				<h1 class="text-2xl font-bold text-slate-900">Create Your Account</h1>
				<p class="text-sm text-slate-500 mt-2">Register to access the patient portal</p>
			</div>

			<!-- Form Card -->
			<div class="bg-white rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 p-8">
				<!-- Success State -->
				<div v-if="success" class="text-center py-8 animate-fade-in">
					<div class="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-6 border-2 border-green-100">
						<CheckCircleIcon class="w-10 h-10 text-green-500" />
					</div>
					<h2 class="text-xl font-bold text-slate-900 mb-2">Registration Successful!</h2>
					<p class="text-slate-500 text-sm mb-6">Please check your email for login instructions.</p>
					<a href="/login" class="inline-flex items-center gap-2 px-6 py-3 bg-slate-900 text-white text-sm font-semibold rounded-xl hover:bg-slate-800 transition-all">
						<LogInIcon class="w-4 h-4" />
						Go to Login
					</a>
				</div>

				<!-- Registration Form -->
				<form v-else @submit.prevent="handleSubmit" class="space-y-5">
					<!-- Name Row -->
					<div class="grid grid-cols-2 gap-4">
						<div>
							<label class="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">First Name *</label>
							<input 
								v-model="form.first_name" 
								type="text" 
								required
								class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
								placeholder="John"
							/>
						</div>
						<div>
							<label class="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">Last Name</label>
							<input 
								v-model="form.last_name" 
								type="text" 
								class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
								placeholder="Doe"
							/>
						</div>
					</div>

					<!-- Email -->
					<div>
						<label class="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">Email Address *</label>
						<div class="relative">
							<MailIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
							<input 
								v-model="form.email" 
								type="email" 
								required
								class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
								placeholder="john@example.com"
							/>
						</div>
					</div>

					<!-- Mobile -->
					<div>
						<label class="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">Mobile Number</label>
						<div class="relative">
							<PhoneIcon class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
							<input 
								v-model="form.mobile" 
								type="tel" 
								class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
								placeholder="+1 234 567 8900"
							/>
						</div>
					</div>

					<!-- Gender -->
					<div>
						<label class="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">Gender *</label>
						<div class="grid grid-cols-3 gap-3">
							<button
								v-for="option in genderOptions"
								:key="option.value"
								type="button"
								@click="form.gender = option.value"
								class="px-4 py-3 rounded-xl text-sm font-medium border-2 transition-all"
								:class="form.gender === option.value 
									? 'bg-indigo-50 border-indigo-500 text-indigo-700' 
									: 'bg-slate-50 border-slate-200 text-slate-600 hover:border-slate-300'"
							>
								{{ option.label }}
							</button>
						</div>
					</div>

					<!-- Error Message -->
					<div v-if="error" class="p-4 bg-red-50 border border-red-100 rounded-xl">
						<p class="text-sm text-red-600">{{ error }}</p>
					</div>

					<!-- Submit Button -->
					<button 
						type="submit" 
						:disabled="loading"
						class="w-full py-4 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-semibold rounded-xl shadow-lg shadow-indigo-200 hover:from-indigo-600 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<span v-if="loading" class="inline-flex items-center gap-2">
							<LoaderIcon class="w-4 h-4 animate-spin" />
							Creating Account...
						</span>
						<span v-else>Create Account</span>
					</button>

					<!-- Login Link -->
					<p class="text-center text-sm text-slate-500">
						Already have an account? 
						<a href="/login" class="text-indigo-600 font-semibold hover:text-indigo-700">Sign in</a>
					</p>
				</form>
			</div>

			<!-- Footer -->
			<p class="text-center text-xs text-slate-400 mt-6">
				By registering, you agree to our Terms of Service and Privacy Policy
			</p>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { UserPlusIcon, CheckCircleIcon, LogInIcon, MailIcon, PhoneIcon, LoaderIcon } from 'lucide-vue-next'

const form = ref({
	first_name: '',
	last_name: '',
	email: '',
	mobile: '',
	gender: ''
})

const genderOptions = [
	{ value: 'Male', label: 'Male' },
	{ value: 'Female', label: 'Female' },
	{ value: 'Other', label: 'Other' }
]

const loading = ref(false)
const error = ref(null)
const success = ref(false)

async function handleSubmit() {
	error.value = null
	
	if (!form.value.first_name) {
		error.value = 'First name is required'
		return
	}
	if (!form.value.email) {
		error.value = 'Email is required'
		return
	}
	if (!form.value.gender) {
		error.value = 'Please select your gender'
		return
	}

	loading.value = true

	try {
		// Get CSRF token from window globals
		const csrfToken = window.csrf_token || window.frappe?.csrf_token || ''
		
		const response = await fetch('/api/method/healthcare.healthcare.api.patient_portal.register_patient', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
				'X-Frappe-CSRF-Token': csrfToken
			},
			body: JSON.stringify({
				first_name: form.value.first_name,
				last_name: form.value.last_name,
				email: form.value.email,
				mobile: form.value.mobile,
				gender: form.value.gender
			})
		})

		const data = await response.json()
		
		if (!response.ok) {
			// Handle error response
			const errorMsg = data.exc_type 
				? data._server_messages 
					? JSON.parse(data._server_messages)[0]
					: data.exception || 'Registration failed'
				: data.message || 'Registration failed. Please try again.'
			error.value = typeof errorMsg === 'string' ? errorMsg.replace(/<[^>]*>/g, '') : errorMsg
			loading.value = false
			return
		}

		success.value = true
		loading.value = false
	} catch (e) {
		console.error('Registration error:', e)
		error.value = 'An unexpected error occurred. Please try again.'
		loading.value = false
	}
}
</script>

<style>
@keyframes fade-in {
	from { opacity: 0; transform: translateY(10px); }
	to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
	animation: fade-in 0.4s ease-out;
}
</style>

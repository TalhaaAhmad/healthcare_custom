<template>
	<div class="space-y-12">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div>
				<h4 class="text-xl font-black text-slate-900 tracking-tight">Active Therapy Plans</h4>
				<p class="text-slate-400 text-sm font-medium">Manage your ongoing therapy treatments</p>
			</div>
			<Button
				variant="solid"
				class="!rounded-2xl !bg-slate-900 !px-6 font-bold"
				@click="showBooking = true"
			>
				Book New Session
			</Button>
		</div>

		<!-- Plans Grid -->
		<div v-if="getPlans.loading" class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div v-for="i in 2" :key="i" class="h-48 bg-slate-50 animate-pulse rounded-3xl"></div>
		</div>
		<div v-else-if="getPlans.data?.length" class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div v-for="plan in getPlans.data" :key="plan.name"
				class="bg-white p-8 rounded-[32px] border border-slate-100 shadow-sm hover:shadow-xl hover:shadow-slate-200/50 transition-all duration-500"
			>
				<div class="flex justify-between items-start mb-6">
					<div>
						<span class="px-3 py-1 bg-brand-orange/10 text-brand-orange text-[10px] font-black uppercase tracking-widest rounded-lg">
							{{ plan.status }}
						</span>
						<h5 class="text-lg font-black text-slate-900 mt-3">{{ plan.therapy_plan_template || 'Custom Plan' }}</h5>
						<p class="text-xs font-bold text-slate-400 mt-1 uppercase tracking-wider">{{ plan.name }}</p>
					</div>
					<div class="bg-slate-50 p-3 rounded-2xl">
						<ActivityIcon class="w-6 h-6 text-slate-400" />
					</div>
				</div>

				<div class="space-y-4">
					<div class="flex justify-between text-sm font-bold">
						<span class="text-slate-400 uppercase text-[10px] tracking-widest">Progress</span>
						<span class="text-slate-900">{{ plan.total_sessions_completed }} / {{ plan.total_sessions }} sessions</span>
					</div>
					<div class="h-2 bg-slate-100 rounded-full overflow-hidden">
						<div class="h-full bg-brand-orange transition-all duration-1000 ease-out"
							:style="{ width: (plan.total_sessions_completed / plan.total_sessions * 100) + '%' }"></div>
					</div>
				</div>
				
				<div class="pt-6 mt-6 border-t border-slate-50 flex justify-between items-center">
					<p class="text-xs font-medium text-slate-400 italic">Started on {{ plan.start_date }}</p>
					<button @click="openBooking(plan)" class="text-xs font-black text-brand-orange uppercase tracking-widest hover:translate-x-1 transition-transform">
						Book Session →
					</button>
				</div>
			</div>
		</div>
		<div v-else class="py-20 text-center bg-slate-50 rounded-[40px] border-2 border-dashed border-slate-200">
			<ActivityIcon class="w-12 h-12 text-slate-300 mx-auto mb-4" />
			<p class="text-slate-400 font-bold mb-6">No active therapy plans found.</p>
			<Button
				variant="outline"
				class="!rounded-2xl !px-6 font-bold"
				@click="showPlanBooking = true"
			>
				Start a New Treatment Plan
			</Button>
		</div>

		<!-- Sessions List -->
		<div class="pt-8">
			<h4 class="text-xl font-black text-slate-900 tracking-tight mb-6">Upcoming & Past Sessions</h4>
			<div class="bg-white rounded-[32px] border border-slate-100 overflow-hidden shadow-sm">
				<div v-if="getSessions.loading" class="p-8 space-y-4">
					<div v-for="i in 3" :key="i" class="h-12 bg-slate-50 animate-pulse rounded-xl"></div>
				</div>
				<div v-else-if="getSessions.data?.length" class="overflow-x-auto">
					<table class="w-full text-left">
						<thead class="bg-slate-50/50 border-b border-slate-100">
							<tr>
								<th class="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Session</th>
								<th class="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Therapist</th>
								<th class="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Plan</th>
								<th class="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Schedule</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-slate-50">
							<tr v-for="session in getSessions.data" :key="session.name" class="hover:bg-slate-50/50 transition-colors">
								<td class="px-8 py-5">
									<div class="flex items-center gap-3">
										<div class="w-2 h-2 rounded-full" :class="session.invoiced ? 'bg-green-500' : 'bg-brand-orange'"></div>
										<div>
											<p class="text-sm font-black text-slate-900">{{ session.therapy_type }}</p>
											<p class="text-[10px] font-bold text-slate-400 uppercase">{{ session.name }}</p>
										</div>
									</div>
								</td>
								<td class="px-8 py-5">
									<p class="text-sm font-bold text-slate-600">{{ session.practitioner || 'Unassigned' }}</p>
								</td>
								<td class="px-8 py-5">
									<p class="text-sm font-bold text-slate-600">{{ session.therapy_plan }}</p>
								</td>
								<td class="px-8 py-5 text-right">
									<p class="text-sm font-black text-slate-900">{{ session.start_date }}</p>
									<p class="text-xs font-bold text-slate-400">{{ session.start_time }} ({{ session.duration }}m)</p>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
				<div v-else class="p-12 text-center text-slate-400 italic">
					No sessions booked yet.
				</div>
			</div>
		</div>

		<!-- Booking Dialogs -->
		<BookTherapySessionModel v-model="showBooking" :plan="selectedPlan" @booked="refreshData" />
		<BookTherapyPlanModel v-model="showPlanBooking" @created="refreshData" />
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource, Button } from 'frappe-ui'
import { ActivityIcon } from 'lucide-vue-next'
import BookTherapySessionModel from './BookTherapySessionModel.vue'
import BookTherapyPlanModel from './BookTherapyPlanModel.vue'

const showBooking = ref(false)
const showPlanBooking = ref(false)
const selectedPlan = ref(null)

const getPlans = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_therapy_plans',
	method: 'GET',
	auto: true
})

const getSessions = createResource({
	url: 'healthcare.healthcare.api.patient_portal.get_therapy_sessions',
	method: 'GET',
	auto: true
})

const refreshData = () => {
	getPlans.fetch()
	getSessions.fetch()
}

const openBooking = (plan) => {
	selectedPlan.value = plan
	showBooking.value = true
}
</script>

<template>
  <div class="flex flex-col h-full animate-fade-in px-4">
    <!-- Practitioner Grid: Premium Cards -->
    <TransitionGroup 
      name="list" 
      tag="div" 
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8"
    >
      <div v-for="doc in items" :key="doc.name"
        class="group relative bg-white rounded-[40px] border border-slate-100 p-6 transition-all duration-500 hover:shadow-[0_30px_80px_-15px_rgba(0,0,0,0.1)] hover:-translate-y-2 cursor-pointer flex flex-col"
        @click="$emit('book', doc)"
      >
        <!-- Bio Image Container with Decorative Ring -->
        <div class="relative mb-6 self-start">
          <div class="absolute -inset-2 bg-gradient-to-br from-brand-orange/20 to-transparent rounded-[32px] opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="relative w-24 h-24 rounded-[28px] overflow-hidden border-2 border-white shadow-md bg-slate-50">
            <img v-if="doc.image" :src="doc.image" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
            <div v-else class="w-full h-full flex items-center justify-center text-slate-400 text-3xl font-black">
              {{ doc.practitioner_name.charAt(0).toUpperCase() }}
            </div>
          </div>
          <!-- Status Badge -->
          <div class="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 border-4 border-white rounded-full"></div>
        </div>

        <!-- Info Section -->
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-2">
            <span class="px-2.5 py-1 rounded-lg bg-brand-orange/5 text-brand-orange text-[9px] font-black uppercase tracking-widest">{{ doc.department }}</span>
          </div>
          <h3 class="text-xl font-black text-slate-900 leading-tight mb-2 group-hover:text-brand-orange transition-colors">{{ doc.practitioner_name }}</h3>
          <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-6">{{ doc.designation }}</p>
          
          <!-- Quick Stats -->
          <div class="grid grid-cols-2 gap-4 pt-6 border-t border-slate-50">
            <div class="flex flex-col">
              <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1">Fee Starting</span>
              <span class="text-sm font-black text-slate-900">Premium</span>
            </div>
            <div class="flex flex-col items-end">
              <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1">Rating</span>
              <div class="flex items-center gap-1">
                <StarIcon class="w-3 h-3 text-brand-orange fill-brand-orange" />
                <span class="text-sm font-black text-slate-900">4.9</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Button (Appear on Hover) -->
        <div class="mt-8 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity duration-300">
           <span class="text-[10px] font-black text-brand-orange uppercase tracking-widest">Book Session</span>
           <div class="w-8 h-8 rounded-full bg-brand-orange flex items-center justify-center text-white">
             <ArrowRightIcon class="w-4 h-4" />
           </div>
        </div>
      </div>
    </TransitionGroup>

    <!-- Consistent Minimalist Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-4 mt-16 pt-8 border-t border-slate-50">
      <button 
        :disabled="page === 1" 
        @click="$emit('update:page', page - 1)"
        class="w-12 h-12 flex items-center justify-center rounded-2xl border border-slate-100 text-slate-400 hover:text-slate-900 hover:border-slate-900 disabled:opacity-20 transition-all bg-white shadow-sm"
      >
        <ChevronLeftIcon class="w-5 h-5" />
      </button>
      
      <div class="flex items-center gap-4 px-6 py-3 bg-white rounded-2xl border border-slate-100 shadow-sm">
        <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest">Page</span>
        <div class="flex items-center gap-2">
          <span class="text-sm font-black text-slate-900">{{ page }}</span>
          <span class="text-[10px] font-bold text-slate-200">/</span>
          <span class="text-sm font-black text-slate-400">{{ totalPages }}</span>
        </div>
      </div>

      <button 
        :disabled="page === totalPages" 
        @click="$emit('update:page', page + 1)"
        class="w-12 h-12 flex items-center justify-center rounded-2xl border border-slate-100 text-slate-400 hover:text-slate-900 hover:border-slate-900 disabled:opacity-20 transition-all bg-white shadow-sm"
      >
        <ChevronRightIcon class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { 
  StarIcon, 
  ArrowRightIcon, 
  ChevronLeftIcon, 
  ChevronRightIcon 
} from 'lucide-vue-next'

defineProps({
	items: Array,
	selected: Object,
	page: Number,
	totalPages: Number
});

defineEmits(['update:selected', 'update:page', 'book']);
</script>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>

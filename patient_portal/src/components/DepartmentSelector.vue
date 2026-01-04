<template>
  <div class="flex flex-col h-full animate-fade-in">
    <!-- Department Grid: Soft Tiles -->
    <TransitionGroup 
      name="list" 
      tag="div" 
      class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-5"
    >
      <div v-for="dept in items" :key="dept.name"
        @click="$emit('update:selected', dept.department)"
        class="relative group cursor-pointer flex flex-col items-center py-6 px-2 rounded-[32px] transition-all duration-300"
        :class="selected === dept.department ? 'bg-slate-50 shadow-inner' : 'hover:bg-slate-50/50'"
      >
        <!-- Active Indicator (Subtle Dot) -->
        <div 
          class="absolute top-4 right-4 w-1.5 h-1.5 rounded-full transition-all duration-500"
          :class="selected === dept.department ? 'bg-brand-orange scale-100' : 'bg-transparent scale-0'"
        ></div>
        
        <!-- Icon Container: Consistent with Practitioner View -->
        <div class="w-14 h-14 rounded-[22px] mb-4 flex items-center justify-center text-xl font-black transition-all duration-500 border-2"
          :class="selected === dept.department 
            ? 'bg-brand-orange border-brand-orange text-white shadow-lg shadow-brand-orange/20 -translate-y-1' 
            : 'bg-white border-slate-50 text-slate-400 group-hover:border-brand-orange/20 group-hover:text-brand-orange'">
          {{ dept.department.charAt(0).toUpperCase() }}
        </div>
        
        <!-- Label: High-end Minimalist Typography -->
        <h3 class="text-[10px] font-black uppercase tracking-[0.15em] text-center w-full truncate px-2 transition-colors duration-300"
          :class="selected === dept.department ? 'text-slate-900' : 'text-slate-400 group-hover:text-slate-600'">
          {{ dept.department }}
        </h3>
      </div>
    </TransitionGroup>

    <!-- Consistent Minimalist Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-4 mt-12 pt-8 border-t border-slate-50">
      <button 
        :disabled="page === 1" 
        @click="$emit('update:page', page - 1)"
        class="w-10 h-10 flex items-center justify-center rounded-xl border border-slate-100 text-slate-400 hover:text-slate-900 hover:border-slate-900 disabled:opacity-20 transition-all bg-white shadow-sm"
      >
        <ChevronLeftIcon class="w-4 h-4" />
      </button>
      
      <div class="flex items-center gap-3 px-5 py-2 bg-white rounded-xl border border-slate-100 shadow-sm">
        <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest">Page</span>
        <div class="flex items-center gap-1.5">
          <span class="text-xs font-black text-slate-900">{{ page }}</span>
          <span class="text-[9px] font-bold text-slate-200">/</span>
          <span class="text-xs font-black text-slate-400">{{ totalPages }}</span>
        </div>
      </div>

      <button 
        :disabled="page === totalPages" 
        @click="$emit('update:page', page + 1)"
        class="w-10 h-10 flex items-center justify-center rounded-xl border border-slate-100 text-slate-400 hover:text-slate-900 hover:border-slate-900 disabled:opacity-20 transition-all bg-white shadow-sm"
      >
        <ChevronRightIcon class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { 
  ChevronLeftIcon, 
  ChevronRightIcon 
} from 'lucide-vue-next'

defineProps({
	items: Array,
	selected: String,
	page: Number,
	totalPages: Number
});

defineEmits(['update:selected', 'update:page']);
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

import { createApp } from 'vue'
import PatientPortal from './PatientPortal.vue'
import router from './router'
import { initSocket } from './socket'

import './index.css'

import {
	FrappeUI,
	Button,
	Dialog,
	Badge,
	setConfig,
	frappeRequest,
	FeatherIcon,
	Tooltip,
	Card
} from 'frappe-ui'

let globalComponents = {
	Button,
	Dialog,
	Badge,
	FeatherIcon,
	Tooltip,
	Card
}

// Configure CSRF token for frappe-ui requests
const originalFrappeRequest = frappeRequest;
const customFrappeRequest = (options) => {
	// Ensure headers exist
	options.headers = options.headers || {};

	// Get CSRF token dynamically
	let token = window.csrf_token || (window.frappe && window.frappe.csrf_token);

	// Fallback to cookie
	if (!token || token.includes('{{')) {
		const match = document.cookie.match(new RegExp('(^| )sid=([^;]+)'));
		// Actually frappe uses a specific cookie for csrf? No, usually X-Frappe-CSRF-Token is the header, value comes from window.csrf_token
		// But let's try reading from document.cookie 'system_user' or others? No.
		// Let's stick to window vars but make sure we don't send placeholders.
	}

	// Double check validity
	const isPlaceholder = !token || token.includes('{{') || token === 'undefined' || token === 'null';

	if (!isPlaceholder) {
		options.headers['X-Frappe-CSRF-Token'] = token;
	} else {
		// As a last ditch effort, try to get it from the common global
		if (window.frappe?.csrf_token && !window.frappe.csrf_token.includes('{{')) {
			options.headers['X-Frappe-CSRF-Token'] = window.frappe.csrf_token;
		}
	}

	return originalFrappeRequest(options);
};

let app = createApp(PatientPortal)
setConfig('resourceFetcher', customFrappeRequest)
app.use(FrappeUI)
app.use(router)
app.provide('$socket', initSocket())

for (let key in globalComponents) {
	app.component(key, globalComponents[key])
}

app.mount('#app')
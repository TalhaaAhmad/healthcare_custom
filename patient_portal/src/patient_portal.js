import { createApp } from 'vue'
import PatientPortal from './PatientPortal.vue'
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

	// Get CSRF token dynamically from window or frappe object
	let token = window.csrf_token || (window.frappe && window.frappe.csrf_token);

	// Check if token is valid (not a Jinja placeholder)
	const isPlaceholder = !token || token.includes('{{') || token === 'undefined' || token === 'null';

	if (!isPlaceholder) {
		options.headers['X-Frappe-CSRF-Token'] = token;
	}

	return originalFrappeRequest(options);
};

let app = createApp(PatientPortal)
setConfig('resourceFetcher', customFrappeRequest)
app.use(FrappeUI)
app.provide('$socket', initSocket())

for (let key in globalComponents) {
	app.component(key, globalComponents[key])
}

app.mount('#app')
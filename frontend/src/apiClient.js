import { BACKEND_URL } from './config'

async function jsonFetch(path, opts = {}) {
	const res = await fetch(BACKEND_URL + path, {
		headers: { 'Content-Type': 'application/json' },
		...opts,
	})
	let data = null
	try { data = await res.json() } catch { /* ignore non-JSON */ }
	return { ok: res.ok, status: res.status, data }
}

export const api = {
	verify: () => jsonFetch('/verify'),
	health: () => jsonFetch('/health'),
	slotsGet: (payload) => jsonFetch('/slots/get', { method: 'POST', body: JSON.stringify(payload) }),
	appointmentCreate: (payload) => jsonFetch('/appointment/create', { method: 'POST', body: JSON.stringify(payload) }),
	appointmentList: (user_email) => jsonFetch('/appointment/list?user_email=' + encodeURIComponent(user_email), { method: 'POST' }),
	appointmentCancel: (payload) => jsonFetch('/appointment/cancel', { method: 'POST', body: JSON.stringify(payload) }),
	otpSend: (payload) => jsonFetch('/otp/send', { method: 'POST', body: JSON.stringify(payload) }),
	otpVerify: (payload) => jsonFetch('/otp/verify', { method: 'POST', body: JSON.stringify(payload) }),
	voiceUpload: async (formData) => {
		const res = await fetch(BACKEND_URL + '/voice/upload', { method: 'POST', body: formData })
		let data = null
		try { data = await res.json() } catch {}
		return { ok: res.ok, status: res.status, data }
	}
}


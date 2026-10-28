export const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

async function request(path, options = {}) {
  const token = localStorage.getItem("divine_trustee_token");
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || "Server request failed");
  return data;
}
export const api = {
  health: () => request("/health"),
  temples: () => request("/temples"),
  events: () => request("/events"),
  booking: payload => request("/bookings", {method:"POST", body:JSON.stringify(payload)}),
  donation: payload => request("/donations", {method:"POST", body:JSON.stringify(payload)}),
  eventRegistration: payload => request("/event-registrations", {method:"POST", body:JSON.stringify(payload)}),
  trusteeLogin: payload => request("/trustee/login", {method:"POST", body:JSON.stringify(payload)}),
  trusteeMe: () => request("/trustee/me"),
  trusteeDashboard: () => request("/trustee/dashboard"),
  
  trusteeEvents: () => request("/trustee/events"),

  addTrusteeEvent: payload =>
    request("/trustee/events", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  closeTrusteeEvent: id =>
    request(`/trustee/events/${id}/close`, {
      method: "POST"
    }),
  confirmBooking: id => request(`/trustee/bookings/${id}/confirm`, {method:"POST"}),
  confirmDonation: id => request(`/trustee/donations/${id}/confirm`, {method:"POST"}),
  trusteePayments: () => request("/trustee/payments"),
  notifications: ({phone,email}) => request(`/notifications?${new URLSearchParams({phone:phone||"",email:email||""})}`)
};

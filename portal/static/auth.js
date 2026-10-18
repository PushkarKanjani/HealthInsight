/**
 * HealthInsight v2 — Authentication Client Helper
 * Manages JWT storage in localStorage, route guarding, and authorized requests.
 */

const AUTH_TOKEN_KEY = 'hi_token';
const AUTH_USER_KEY = 'hi_user';

function getToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

function getUser() {
  return localStorage.getItem(AUTH_USER_KEY) || 'Clinical Admin';
}

function saveSession(token, username) {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(AUTH_USER_KEY, username);
}

function clearSession() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

function logout() {
  clearSession();
  window.location.href = '/';
}

function requireAuth() {
  const token = getToken();
  if (!token) {
    window.location.href = '/';
    return false;
  }
  return true;
}

function redirectIfAuthenticated() {
  const token = getToken();
  if (token) {
    window.location.href = '/dashboard';
    return true;
  }
  return false;
}

async function fetchWithAuth(url, options = {}) {
  const token = getToken();
  if (!token) {
    window.location.href = '/';
    throw new Error('Unauthenticated');
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...(options.headers || {})
  };

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    clearSession();
    window.location.href = '/';
    throw new Error('Session expired. Please log in again.');
  }

  return response;
}

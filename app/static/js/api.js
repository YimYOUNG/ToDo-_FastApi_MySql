// API Client v2.1 - 修复版 (2026-05-15)
const API_BASE = '/api';

function getAuthToken() {
    return localStorage.getItem('access_token') || '';
}

function getHeaders() {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json'
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// 智能序列化API错误信息（处理字符串/数组/对象格式）
function formatApiError(errorObj) {
    if (!errorObj || !errorObj.detail) return 'Request failed';

    const detail = errorObj.detail;

    if (typeof detail === 'string') {
        return detail;
    } else if (Array.isArray(detail)) {
        // Pydantic ValidationError 格式: [{msg: "...", type: "...", loc: [...]}]
        return detail.map(e => e.msg || e.message || JSON.stringify(e)).join('; ');
    } else if (typeof detail === 'object') {
        // 普通对象格式
        try {
            return JSON.stringify(detail);
        } catch (err) {
            return String(detail);
        }
    }

    return String(detail || 'Request failed');
}

async function apiGet(url) {
    const response = await fetch(`${API_BASE}${url}`, {
        method: 'GET',
        headers: getHeaders()
    });

    if (response.status === 401) {
        await tryRefreshToken();
        return apiGet(url);
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(formatApiError(error));
    }

    return response.json();
}

async function apiPost(url, data) {
    const response = await fetch(`${API_BASE}${url}`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(data)
    });

    if (response.status === 401) {
        await tryRefreshToken();
        return apiPost(url, data);
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(formatApiError(error));
    }

    return response.json();
}

async function apiPut(url, data) {
    const response = await fetch(`${API_BASE}${url}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(data)
    });

    if (response.status === 401) {
        await tryRefreshToken();
        return apiPut(url, data);
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(formatApiError(error));
    }

    return response.json();
}

async function apiPatch(url) {
    const response = await fetch(`${API_BASE}${url}`, {
        method: 'PATCH',
        headers: getHeaders()
    });

    if (response.status === 401) {
        await tryRefreshToken();
        return apiPatch(url);
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(formatApiError(error));
    }

    return response.json();
}

async function apiDelete(url) {
    const response = await fetch(`${API_BASE}${url}`, {
        method: 'DELETE',
        headers: getHeaders()
    });

    if (response.status === 401) {
        await tryRefreshToken();
        return apiDelete(url);
    }

    if (!response.ok && response.status !== 204) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(formatApiError(error));
    }

    return true;
}

async function tryRefreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
        window.location.href = '/login';
        throw new Error('Not authenticated');
    }

    try {
        const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (!response.ok) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            throw new Error('Session expired');
        }

        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
    } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        throw error;
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

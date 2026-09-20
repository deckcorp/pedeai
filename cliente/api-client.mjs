function normalizeBaseUrl(baseUrl) {
  return String(baseUrl).replace(/\/$/, '');
}

export function createApiClient(baseUrl, fetchImpl = globalThis.fetch, { resolvePublicSession } = {}) {
  const base = normalizeBaseUrl(baseUrl);
  async function request(path, options = {}) {
    const response = await fetchImpl(`${base}${path}`, options);
    let body = {};
    try { body = await response.json(); } catch { /* resposta sem JSON */ }
    if (!response.ok) {
      const error = new Error(body.message || body.error || `API error ${response.status}`);
      error.status = response.status;
      error.code = body.error;
      throw error;
    }
    return body;
  }
  const auth = token => ({ authorization: `Bearer ${token}` });
  async function publicRequest(path, sessionToken, options = {}) {
    try {
      return await request(path, { ...options, headers: { ...options.headers, ...auth(sessionToken) } });
    } catch (error) {
      if (error.status !== 401 || !resolvePublicSession) throw error;
      const renewedSession = await resolvePublicSession();
      const renewedToken = typeof renewedSession === 'string' ? renewedSession : renewedSession?.session_token;
      if (!renewedToken) throw error;
      return request(path, { ...options, headers: { ...options.headers, ...auth(renewedToken) } });
    }
  }
  return {
    resolveQr: qrToken => request(`/v1/public/qr-context/${encodeURIComponent(qrToken)}`),
    identifySession: (sessionToken, identity) => publicRequest('/v1/public/session/identify', sessionToken, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(identity) }),
    getMenu: sessionToken => publicRequest('/v1/public/menu', sessionToken),
    listOrders: sessionToken => publicRequest('/v1/public/orders', sessionToken),
    getOrder: (sessionToken, orderId) => publicRequest(`/v1/public/orders/${encodeURIComponent(orderId)}`, sessionToken),
    createOrder: (sessionToken, payload, idempotencyKey) => publicRequest('/v1/public/orders', sessionToken, { method: 'POST', headers: { 'content-type': 'application/json', 'idempotency-key': idempotencyKey }, body: JSON.stringify(payload) }),
    retryOrder: (sessionToken, orderId, idempotencyKey) => publicRequest(`/v1/public/orders/${encodeURIComponent(orderId)}/retry`, sessionToken, { method: 'POST', headers: { 'content-type': 'application/json', 'idempotency-key': idempotencyKey }, body: '{}' }),
    createServiceCall: (sessionToken, type, idempotencyKey) => publicRequest('/v1/public/service-calls', sessionToken, { method: 'POST', headers: { 'content-type': 'application/json', 'idempotency-key': idempotencyKey }, body: JSON.stringify({ type }) }),
    listPublicServiceCalls: sessionToken => publicRequest('/v1/public/service-calls', sessionToken),
    cancelServiceCall: (sessionToken, callId) => publicRequest(`/v1/public/service-calls/${encodeURIComponent(callId)}`, sessionToken, { method: 'DELETE' }),
    listOperatorOrders: staffToken => request('/v1/operator/orders', { headers: auth(staffToken) }),
    listActiveOperatorOrders: staffToken => request('/v1/operator/orders/active', { headers: auth(staffToken) }),
    listServiceCalls: staffToken => request('/v1/operator/service-calls', { headers: auth(staffToken) }),
    approveOrder: (staffToken, orderId) => request(`/v1/operator/orders/${encodeURIComponent(orderId)}/approve`, { method: 'POST', headers: auth(staffToken) }),
    rejectOrder: (staffToken, orderId, reason) => request(`/v1/operator/orders/${encodeURIComponent(orderId)}/reject`, { method: 'POST', headers: { ...auth(staffToken), 'content-type': 'application/json' }, body: JSON.stringify({ reason }) }),
    updateOrderStatus: (staffToken, orderId, status) => request(`/v1/operator/orders/${encodeURIComponent(orderId)}/status`, { method: 'POST', headers: { ...auth(staffToken), 'content-type': 'application/json' }, body: JSON.stringify({ status }) }),
    resolveServiceCall: (staffToken, serviceCallId) => request(`/v1/operator/service-calls/${encodeURIComponent(serviceCallId)}/resolve`, { method: 'POST', headers: auth(staffToken) })
  };
}

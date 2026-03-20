/**
 * Authenticated API requests: rely on HttpOnly cookies + same-origin.
 * Do not send Bearer tokens from JS (stronger XSS resistance).
 */
export function credFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    return fetch(input, { ...init, credentials: 'include' });
}

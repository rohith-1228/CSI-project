import type { AnalyzeResponse, ApiError } from '../types/api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

/**
 * Sends suspicious message text to the CyberSaathi backend analysis endpoint.
 * Enforces strict timeouts and clear error translation.
 */
export async function analyzeMessage(message: string): Promise<AnalyzeResponse> {
  const cleanMessage = message.trim();
  if (!cleanMessage) {
    throw {
      message: 'Please paste a message or web link to check.',
      status: 400
    } as ApiError;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: cleanMessage }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status === 429) {
        throw {
          message: 'Rate limit reached. Please wait a moment before checking another message.',
          status: 429,
          isRateLimit: true
        } as ApiError;
      }

      if (response.status === 413) {
        throw {
          message: 'Message is too long. Please keep it under 5,000 characters.',
          status: 413
        } as ApiError;
      }

      if (response.status === 422) {
        throw {
          message: 'Please enter a valid message or link to analyze.',
          status: 422
        } as ApiError;
      }

      let errorMsg = 'Failed to analyze message. Please try again.';
      try {
        const errorData = await response.json();
        if (errorData.message) {
          errorMsg = errorData.message;
        } else if (errorData.detail) {
          errorMsg = typeof errorData.detail === 'string' ? errorData.detail : errorMsg;
        }
      } catch {
        // fallback to default error message
      }

      throw {
        message: errorMsg,
        status: response.status
      } as ApiError;
    }

    const data: AnalyzeResponse = await response.json();
    return data;
  } catch (error: any) {
    clearTimeout(timeoutId);

    if (error.status) {
      throw error;
    }

    if (error.name === 'AbortError') {
      throw {
        message: 'The safety check timed out. Please check your connection and try again.',
        status: 408
      } as ApiError;
    }

    throw {
      message: 'Unable to connect to the safety server. Please ensure the backend is running at ' + API_BASE_URL,
      status: 503
    } as ApiError;
  }
}

/**
 * Checks server availability via liveness probe.
 */
export async function checkServerHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
}

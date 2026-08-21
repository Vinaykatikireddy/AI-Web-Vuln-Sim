import axios, { AxiosError, CancelTokenSource } from 'axios';

interface RetryOptions {
    maxRetries?: number;
    delay?: number;
    retryableStatusCodes?: number[];
    retryableErrors?: string[];
}

export const retry = async <T>(
    fn: () => Promise<T>,
    options: RetryOptions = {}
): Promise<T> => {
    const {
        maxRetries = 3,
        delay = 1000,
        retryableStatusCodes = [408, 429, 500, 502, 503, 504],
        retryableErrors = ['ECONNABORTED', 'ETIMEDOUT', 'ENETDOWN', 'ENETUNREACH', 'ENOTFOUND'],
    } = options;

    let lastError: unknown;

    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            const axiosError = error as AxiosError;

            // Check if error is retryable
            if (axiosError.code && retryableErrors.includes(axiosError.code)) {
                await new Promise((resolve) => setTimeout(resolve, delay * Math.pow(2, i)));
                continue;
            }

            if (axiosError.response?.status && retryableStatusCodes.includes(axiosError.response.status)) {
                await new Promise((resolve) => setTimeout(resolve, delay * Math.pow(2, i)));
                continue;
            }

            // If not retryable, throw immediately
            throw error;
        }
    }

    throw lastError;
};
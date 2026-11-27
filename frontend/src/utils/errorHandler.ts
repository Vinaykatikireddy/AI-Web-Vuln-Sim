export const errorHandler = (error: any): string => {
    if (!error) return "An unknown error occurred. Please try again."

    // Network error (no response)
    if (!error.response) {
        return "Network error. Please check your connection and try again.";
    }

    // HTTP status codes
    const { status } = error.response;
    switch (status) {
        case 400:
            return error.response.data?.detail || "Bad request. Please check your input.";
        case 401:
            if (error.config?.url?.includes('/auth/login')) {
                return error.response.data?.detail || "Incorrect username or password.";
            }
            localStorage.removeItem('auth');
            localStorage.removeItem('user');
            window.dispatchEvent(new Event('auth:unauthorized'));
            return error.response.data?.detail || "Unauthorized. Please log in again.";
        case 403:
            return "You don't have permission to perform this action.";
        case 404:
            return "Resource not found. Please try again.";
        case 408:
            return "Request timeout. Please try again.";
        case 429:
            return "Too many requests. Please wait and try again.";
        case 500:
        case 502:
        case 503:
        case 504:
            return "Server error. Please try again later.";
        default:
            return error.response.data?.detail || "An error occurred. Please try again.";
    }
};
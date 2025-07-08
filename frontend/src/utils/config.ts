// Configuration utilities for the frontend application

/**
 * Get the API base URL from environment variables with fallback
 */
export const getApiBaseUrl = (): string => {
  return import.meta.env.VITE_API_BASE_URL || "http://localhost:5001/api";
};

/**
 * Check if we're in development mode
 */
export const isDevelopment = (): boolean => {
  return import.meta.env.DEV;
};

/**
 * Check if we're in production mode
 */
export const isProduction = (): boolean => {
  return import.meta.env.PROD;
};

/**
 * Get all environment variables (for debugging)
 */
export const getEnvVars = () => {
  return {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
    MODE: import.meta.env.MODE,
    DEV: import.meta.env.DEV,
    PROD: import.meta.env.PROD,
  };
};

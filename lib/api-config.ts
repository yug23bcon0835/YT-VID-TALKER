/**
 * API Configuration utility
 * 
 * This utility provides the correct API base URL for different environments:
 * - In development: Uses NEXT_PUBLIC_API_URL if set (e.g., http://localhost:8000)
 * - In production/Vercel: Uses relative URLs (empty string) to leverage Vercel rewrites
 */

export const getApiUrl = (): string => {
  // In production or when NEXT_PUBLIC_API_URL is not set, use relative URLs
  // This works with Vercel's rewrite configuration
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
  
  // Remove trailing slash if present
  return apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
};

/**
 * Constructs a full API endpoint URL
 * @param endpoint - The API endpoint path (should start with /api/)
 * @returns The complete URL for the API call
 */
export const getApiEndpoint = (endpoint: string): string => {
  const baseUrl = getApiUrl();
  
  // Ensure endpoint starts with /
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  return `${baseUrl}${normalizedEndpoint}`;
};

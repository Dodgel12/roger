import * as SecureStore from "expo-secure-store";
import axios from "axios";

const TOKEN_KEY = "roger_auth_token";
const USERNAME_KEY = "roger_username";

/**
 * Auth Service for managing authentication with Roger API
 */

export const authService = {
  /**
   * Register a new user
   */
  async register(username, password, serverUrl) {
    try {
      const response = await axios.post(`${serverUrl}/auth/register`, {
        username,
        password,
      });

      if (response.data.token) {
        // Store token and username securely
        await SecureStore.setItemAsync(TOKEN_KEY, response.data.token);
        await SecureStore.setItemAsync(USERNAME_KEY, username);
      }

      return { success: true, token: response.data.token, message: response.data.message };
    } catch (error) {
      const message = error.response?.data?.detail || error.message || "Registration failed";
      return { success: false, message };
    }
  },

  /**
   * Login user
   */
  async login(username, password, serverUrl) {
    try {
      const response = await axios.post(`${serverUrl}/auth/login`, {
        username,
        password,
      });

      if (response.data.token) {
        // Store token and username securely
        await SecureStore.setItemAsync(TOKEN_KEY, response.data.token);
        await SecureStore.setItemAsync(USERNAME_KEY, username);
      }

      return { success: true, token: response.data.token, message: response.data.message };
    } catch (error) {
      const message = error.response?.data?.detail || error.message || "Login failed";
      return { success: false, message };
    }
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await SecureStore.deleteItemAsync(TOKEN_KEY);
      await SecureStore.deleteItemAsync(USERNAME_KEY);
      return { success: true };
    } catch (error) {
      console.error("Logout error:", error);
      return { success: false, message: error.message };
    }
  },

  /**
   * Get stored auth token
   */
  async getToken() {
    try {
      const token = await SecureStore.getItemAsync(TOKEN_KEY);
      return token;
    } catch (error) {
      console.error("Error getting token:", error);
      return null;
    }
  },

  /**
   * Get stored username
   */
  async getUsername() {
    try {
      const username = await SecureStore.getItemAsync(USERNAME_KEY);
      return username;
    } catch (error) {
      console.error("Error getting username:", error);
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  async isAuthenticated() {
    const token = await this.getToken();
    return !!token;
  },

  /**
   * Get axios instance with auth header
   */
  async getAxiosInstance(serverUrl) {
    const token = await this.getToken();

    const instance = axios.create({
      baseURL: serverUrl,
    });

    if (token) {
      instance.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }

    return instance;
  },
};

/**
 * Create an axios instance with auth token
 */
export async function createAuthenticatedClient(serverUrl) {
  const token = await authService.getToken();

  const client = axios.create({
    baseURL: serverUrl,
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (token) {
    client.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    console.log("✓ Auth token added to request header");
  } else {
    console.warn("⚠ No auth token found - requests may fail with 401");
  }

  // Add response interceptor for debugging 401 errors
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        console.error("🔐 401 Unauthorized - Check if token is expired or invalid");
      }
      return Promise.reject(error);
    }
  );

  return client;
}

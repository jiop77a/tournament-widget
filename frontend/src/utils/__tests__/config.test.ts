import { describe, it, expect } from "vitest";
import {
  getApiBaseUrl,
  isDevelopment,
  isProduction,
  getEnvVars,
} from "../config";

describe("config utilities", () => {
  describe("getApiBaseUrl", () => {
    it("should return a valid URL", () => {
      const url = getApiBaseUrl();
      expect(url).toMatch(/^https?:\/\/.+/);
    });

    it("should return the default URL in test environment", () => {
      const url = getApiBaseUrl();
      expect(url).toBe("http://localhost:5001/api");
    });
  });

  describe("isDevelopment", () => {
    it("should return a boolean", () => {
      const result = isDevelopment();
      expect(typeof result).toBe("boolean");
    });
  });

  describe("isProduction", () => {
    it("should return a boolean", () => {
      const result = isProduction();
      expect(typeof result).toBe("boolean");
    });
  });

  describe("getEnvVars", () => {
    it("should return an object with expected properties", () => {
      const envVars = getEnvVars();

      expect(envVars).toHaveProperty("API_BASE_URL");
      expect(envVars).toHaveProperty("MODE");
      expect(envVars).toHaveProperty("DEV");
      expect(envVars).toHaveProperty("PROD");
    });

    it("should return consistent values", () => {
      const envVars1 = getEnvVars();
      const envVars2 = getEnvVars();

      expect(envVars1).toEqual(envVars2);
    });
  });
});

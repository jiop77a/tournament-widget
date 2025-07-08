// Global type declarations for tests
import type { MockInstance } from "vitest";

declare global {
  var global: {
    fetch: MockInstance;
  };
}

export {};

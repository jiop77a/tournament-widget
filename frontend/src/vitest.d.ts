/// <reference types="vitest/globals" />

import type { MockInstance } from 'vitest';

declare global {
  var global: typeof globalThis & {
    fetch: MockInstance;
  };
}

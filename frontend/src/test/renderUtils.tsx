// Custom render function for testing React components
import React from "react";
import { render, type RenderOptions } from "@testing-library/react";
import { TestProvider } from "./TestProvider";

// Custom render function that includes Material UI theme
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, "wrapper">
) => render(ui, { wrapper: TestProvider, ...options });

// Export only the custom render function
export { customRender as render };

import svelte from "eslint-plugin-svelte";
import globals from "globals";
import tsParser from "@typescript-eslint/parser";
import svelteConfig from "./svelte.config.js";

export default [
  {
    ignores: ["dist/**", "node_modules/**"],
  },
  ...svelte.configs["flat/base"],
  {
    files: ["**/*.svelte", "**/*.svelte.js", "**/*.svelte.ts"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parserOptions: {
        parser: tsParser,
        svelteConfig,
      },
    },
  },
  {
    files: ["**/*.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
];

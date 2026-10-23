import hooks from 'eslint-plugin-react-hooks';
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
export default tseslint.config({ignores:['**/.next/**','**/node_modules/**','**/next-env.d.ts']},js.configs.recommended,...tseslint.configs.recommended,{files:['**/*.{ts,tsx}'],plugins:{'react-hooks':hooks},rules:{'react-hooks/exhaustive-deps':'error','@typescript-eslint/no-unused-vars':['error',{argsIgnorePattern:'^_'}]}},{files:['**/*.mjs'],languageOptions:{globals:{process:'readonly'}}});

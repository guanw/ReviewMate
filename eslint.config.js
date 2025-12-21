import js from '@eslint/js';
import prettier from 'eslint-plugin-prettier';
import prettierConfig from 'eslint-config-prettier';

export default [
  js.configs.recommended,
  {
    files: ['**/*.js'],
    languageOptions: {
      globals: {
        require: 'readonly',
        module: 'readonly',
        console: 'readonly',
        process: 'readonly',
      },
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'commonjs',
      },
    },
    plugins: {
      prettier,
    },
    rules: {
      ...prettierConfig.rules,
      'prettier/prettier': ['error', { endOfLine: 'auto' }],
      'no-unused-vars': 'error',
      'no-console': 'warn',
      'no-debugger': 'error',
      'max-len': ['error', { code: 120 }],
      quotes: ['error', 'single'],
      semi: ['error', 'always'],
    },
  },
];
import js from '@eslint/js';
import globals from 'globals';

export default [
    { ignores: ['public/js/vendor/**', '**/*.min.js'] },
    js.configs.recommended,
    {
        files: ['public/js/**/*.js'],
        languageOptions: { sourceType: 'module', globals: globals.browser },
    },
];

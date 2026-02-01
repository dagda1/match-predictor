import defaultConfig from '@cutting/eslint-config/react';

/** @type {import("eslint").Linter.Config} */
export default [
  ...defaultConfig,
  {
    files: ['**/*.ts', '**/*.tsx'],
    rules: {
      '@typescript-eslint/no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'react',
              importNames: ['JSX'],
              message: "Don't import JSX from 'react'. Use React.FC or inline JSX.Element instead.",
            },
          ],
        },
      ],
      'max-lines': ['warn', { max: 150, skipBlankLines: true, skipComments: true }],
      'no-inline-comments': ['warn', { ignorePattern: '^\\s*(// eslint-disable|GraphQL)' }],
      'no-warning-comments': 'error',
      'no-restricted-syntax': [
        'error',
        {
          selector: "MemberExpression[object.name='React']",
          message: 'Avoid using React.*. Use named imports instead.',
        },
        {
          selector: "TSTypeReference > TSQualifiedName[left.name='React']",
          message:
            'Avoid using the global `React.` namespace for types (e.g. `React.MouseEvent`). Import the type directly instead.',
        },
        {
          selector:
            "TSTypeReference > TSQualifiedName[left.name='React'][right.property.name=/^(Mouse|Keyboard|Focus|Form|Drag|Wheel|Touch|Animation|Transition|Clipboard|Composition|Pointer)Event$/]",
          message: 'Use direct event types (MouseEvent, KeyboardEvent, etc.) instead of React.MouseEvent',
        },
        {
          selector: [
            'CallExpression[callee.property.name=/^(map|filter|forEach|reduce|some|every|find|flatMap)$/] > ArrowFunctionExpression > :matches(Identifier[name=/^[a-zA-Z]$/], ArrayPattern > Identifier[name=/^[a-zA-Z]$/])',
            'ForStatement > VariableDeclaration > VariableDeclarator > Identifier[name=/^[a-zA-Z]$/]',
            'ForOfStatement > VariableDeclaration > VariableDeclarator > Identifier[name=/^[a-zA-Z]$/]',
            'ForInStatement > VariableDeclaration > VariableDeclarator > Identifier[name=/^[a-zA-Z]$/]',
          ].join(', '),
          message:
            'Avoid single-letter variable names in loops and iteration callbacks. Use descriptive names instead (e.g. `item`, `user`, `entry`).',
        },
      ],
    },
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    ignores: ['**/*.styles.ts', '**/*.styles.tsx', '**/styles.ts'],
    rules: {
      'no-restricted-syntax': [
        'warn',
        {
          selector: "VariableDeclarator > CallExpression > CallExpression[callee.name='styled']",
          message: 'Move styled component declarations to a .styles.ts/.styles.tsx file.',
        },
      ],
    },
  },
  {
    files: ['**/*.test.ts', '**/*.test.tsx', '**/*.styles.ts', '**/*.styles.tsx', '**/vite.config.ts'],
    rules: {
      'max-lines': 'off',
    },
  },
];

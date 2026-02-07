import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

import { App } from './App';

describe('App', () => {
  it('renders heading', async () => {
    render(<App />);
    expect(await screen.findByRole('heading', { name: 'Match Predictor', level: 1 })).toBeInTheDocument();
  });
});

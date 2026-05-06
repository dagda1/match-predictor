import { ThemeProvider, createTheme } from '@mui/material/styles';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { PredictionChips } from './PredictionChips';

function renderChips(props: { mlCorrect: boolean; poissonCorrect: boolean }) {
  return render(
    <ThemeProvider theme={createTheme()}>
      <PredictionChips {...props} />
    </ThemeProvider>,
  );
}

describe('PredictionChips', () => {
  it('shows a tick when both predictions are correct', () => {
    renderChips({ mlCorrect: true, poissonCorrect: true });
    expect(screen.getByText('ML ✓')).toBeInTheDocument();
    expect(screen.getByText('Poi ✓')).toBeInTheDocument();
  });

  it('shows a cross when both predictions are wrong', () => {
    renderChips({ mlCorrect: false, poissonCorrect: false });
    expect(screen.getByText('ML ✗')).toBeInTheDocument();
    expect(screen.getByText('Poi ✗')).toBeInTheDocument();
  });

  it('renders each model independently', () => {
    renderChips({ mlCorrect: true, poissonCorrect: false });
    expect(screen.getByText('ML ✓')).toBeInTheDocument();
    expect(screen.getByText('Poi ✗')).toBeInTheDocument();
  });
});

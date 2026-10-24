import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import type { ApiResultsResponse } from '~/api/types';
import { App } from '~/App';

function stubResults(response: ApiResultsResponse) {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => new Response(JSON.stringify(response), { headers: { 'Content-Type': 'application/json' } })),
  );
}

function emptyWeek(ended: boolean): ApiResultsResponse {
  return {
    matches: [],
    summary: { mlCorrect: 0, mlTotal: 0, poissonCorrect: 0, poissonTotal: 0 },
    earlierMatchDate: '2027-05-30',
    laterMatchDate: null,
    season: { name: '2026-27', lastMatchDate: '2027-05-30 15:00:00', ended },
  };
}

describe('Results', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('shows the season has ended on a week after the last match of an ended season', async () => {
    stubResults(emptyWeek(true));
    window.history.pushState({}, '', '/results/2027-06-07/2027-06-13');

    render(<App />);

    expect(await screen.findByText('The 2026-27 season has ended')).toBeInTheDocument();
    expect(screen.queryByText('No matches this week')).not.toBeInTheDocument();
  });

  it('shows no matches this week when the season has not ended', async () => {
    stubResults(emptyWeek(false));
    window.history.pushState({}, '', '/results/2027-06-07/2027-06-13');

    render(<App />);

    expect(await screen.findByText('No matches this week')).toBeInTheDocument();
    expect(screen.queryByText('The 2026-27 season has ended')).not.toBeInTheDocument();
  });
});

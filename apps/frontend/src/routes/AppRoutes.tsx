import type { NavLinkItem } from '@match-predictor/theme';
import { Page } from '@match-predictor/theme';
import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router';

import { ResultsSkeleton } from '~/pages/Results/components/ResultsSkeleton/ResultsSkeleton';

const Home = lazy(() => import('~/pages/Home/Home'));
const Results = lazy(() => import('~/pages/Results/Results'));

const navLinks: NavLinkItem[] = [
  { label: 'Predictor', to: '/' },
  { label: 'Results', to: '/results' },
];

export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route element={<Page navLinks={navLinks} />}>
        <Route index element={<Home />} />
        <Route
          path="results"
          element={
            <Suspense fallback={<ResultsSkeleton />}>
              <Results />
            </Suspense>
          }
        />
      </Route>
    </Routes>
  );
}

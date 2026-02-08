import type { NavLinkItem } from '@match-predictor/theme';
import { Page } from '@match-predictor/theme';
import { lazy } from 'react';
import { Route, Routes } from 'react-router';

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
        <Route path="results" element={<Results />} />
      </Route>
    </Routes>
  );
}

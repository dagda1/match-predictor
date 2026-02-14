import type { NavLinkItem } from '@match-predictor/theme';
import { Page } from '@match-predictor/theme';
import dayjs from 'dayjs';
import { lazy, Suspense } from 'react';
import { Navigate, Route, Routes } from 'react-router';

import { ISO_DATE_FORMAT, mondayForDate } from '~/constants';
import { ResultsSkeleton } from '~/pages/Results/components/ResultsSkeleton/ResultsSkeleton';

const Home = lazy(() => import('~/pages/Home/Home'));
const Results = lazy(() => import('~/pages/Results/Results'));

const navLinks: NavLinkItem[] = [
  { label: 'Predictor', to: '/' },
  { label: 'Results', to: '/results' },
];

function ResultsRedirect(): JSX.Element {
  const monday = mondayForDate(dayjs());
  const sunday = monday.add(6, 'day');
  return <Navigate to={`/results/${monday.format(ISO_DATE_FORMAT)}/${sunday.format(ISO_DATE_FORMAT)}`} replace />;
}

const resultsElement = (
  <Suspense fallback={<ResultsSkeleton />}>
    <Results />
  </Suspense>
);

export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route element={<Page navLinks={navLinks} />}>
        <Route index element={<Home />} />
        <Route path="results" element={<ResultsRedirect />} />
        <Route path="results/:startDate/:endDate" element={resultsElement} />
      </Route>
    </Routes>
  );
}

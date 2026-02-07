import { Page } from '@match-predictor/theme';
import { lazy } from 'react';
import { Route, Routes } from 'react-router';

const Home = lazy(() => import('~/pages/Home/Home'));

export function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route element={<Page />}>
        <Route path="*" element={<Home />} />
      </Route>
    </Routes>
  );
}

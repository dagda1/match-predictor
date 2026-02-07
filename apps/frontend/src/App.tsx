import { ThemeProvider } from '@match-predictor/theme';
import { Suspense } from 'react';
import { BrowserRouter } from 'react-router';

import { AppRoutes } from './routes/AppRoutes';

export function App(): JSX.Element {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Suspense>
          <AppRoutes />
        </Suspense>
      </BrowserRouter>
    </ThemeProvider>
  );
}

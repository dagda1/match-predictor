import type { ReactNode } from 'react';

import { Root } from './styles';

interface MaxWidthContainerProps {
  children: ReactNode;
}

export function MaxWidthContainer({ children }: MaxWidthContainerProps): JSX.Element {
  return <Root>{children}</Root>;
}

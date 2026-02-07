import { useCallback, useSyncExternalStore } from 'react';

const STORAGE_KEY = 'theme';

function getSnapshot(): 'light' | 'dark' {
  return (localStorage.getItem(STORAGE_KEY) as 'light' | 'dark') ?? 'light';
}

function subscribe(callback: () => void): () => void {
  const handler = (e: StorageEvent) => {
    if (e.key === STORAGE_KEY) {
      callback();
    }
  };

  window.addEventListener('storage', handler);
  return () => window.removeEventListener('storage', handler);
}

export function useThemeMode(): {
  mode: 'light' | 'dark';
  toggle: () => void;
} {
  const mode = useSyncExternalStore(subscribe, getSnapshot);

  const toggle = useCallback(() => {
    const next = getSnapshot() === 'light' ? 'dark' : 'light';
    localStorage.setItem(STORAGE_KEY, next);
    window.dispatchEvent(new StorageEvent('storage', { key: STORAGE_KEY }));
  }, []);

  return { mode, toggle };
}

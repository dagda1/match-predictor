import { execSync } from 'child_process';

try {
  execSync('husky', { stdio: 'ignore' });
} catch {
  // husky not available, skip
}

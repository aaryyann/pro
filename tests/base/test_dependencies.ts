import { test } from 'node:test';
import assert from 'node:assert';
import { execSync } from 'node:child_process';

// Use process.cwd() since tests run from repository root
const repoRoot = process.cwd();

test('Node.js is available', () => {
  const result = execSync('node --version', { encoding: 'utf-8' });
  assert(result.trim().startsWith('v'), 'Node.js version should be reported');
});

test('npm is available', () => {
  execSync('npm --version', { encoding: 'utf-8' });
  // If no exception is thrown, npm is available
});

test('TypeScript can compile the project', () => {
  try {
    execSync('npm run build', { 
      cwd: repoRoot, 
      encoding: 'utf-8',
      stdio: 'pipe'
    });
  } catch (error: any) {
    assert.fail(`TypeScript compilation should succeed: ${error.stderr || error.message}`);
  }
});

test('Python is available', () => {
  try {
    const result = execSync('python3 --version', { encoding: 'utf-8' });
    const versionMatch = result.match(/Python (\d+)/);
    assert(versionMatch !== null, 'Python version should be reported');
    const majorVersion = parseInt(versionMatch![1], 10);
    assert(majorVersion >= 3, 'Python 3 should be available');
  } catch (error) {
    assert.fail('Python 3 should be available');
  }
});

test('pytest is available', () => {
  try {
    execSync('python3 -m pytest --version', { encoding: 'utf-8', stdio: 'pipe' });
    // If no exception is thrown, pytest is available
  } catch (error) {
    assert.fail('pytest should be installed');
  }
});


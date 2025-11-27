import pytest
import sys
import os

def test_node_available():
    """Test that Node.js is available in the environment."""
    import subprocess
    result = subprocess.run(['node', '--version'], capture_output=True, text=True)
    assert result.returncode == 0, "Node.js should be available"
    assert result.stdout.strip().startswith('v'), "Node.js version should be reported"

def test_npm_available():
    """Test that npm is available in the environment."""
    import subprocess
    result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
    assert result.returncode == 0, "npm should be available"

def test_typescript_compiles():
    """Test that TypeScript can compile the project."""
    import subprocess
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    result = subprocess.run(['npm', 'run', 'build'], cwd=repo_root, capture_output=True, text=True)
    assert result.returncode == 0, f"TypeScript compilation should succeed: {result.stderr}"

def test_python_available():
    """Test that Python is available in the environment."""
    assert sys.version_info.major >= 3, "Python 3 should be available"

def test_pytest_available():
    """Test that pytest is available."""
    import pytest
    assert hasattr(pytest, '__version__'), "pytest should be installed"


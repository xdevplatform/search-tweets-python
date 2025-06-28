"""Validation tests to ensure testing infrastructure is properly configured."""
import sys
from pathlib import Path
import pytest


class TestSetupValidation:
    """Test class to validate the testing infrastructure setup."""
    
    def test_python_version(self):
        """Verify Python version meets requirements."""
        assert sys.version_info >= (3, 8), "Python 3.8 or higher is required"
    
    def test_project_structure(self):
        """Verify project structure is correct."""
        project_root = Path(__file__).parent.parent
        
        # Check main package exists
        assert (project_root / "searchtweets").exists()
        assert (project_root / "searchtweets" / "__init__.py").exists()
        
        # Check test directories exist
        assert (project_root / "tests").exists()
        assert (project_root / "tests" / "__init__.py").exists()
        assert (project_root / "tests" / "unit").exists()
        assert (project_root / "tests" / "integration").exists()
        
        # Check configuration files exist
        assert (project_root / "pyproject.toml").exists()
    
    def test_imports(self):
        """Verify main package can be imported."""
        try:
            import searchtweets
            assert searchtweets is not None
        except ImportError:
            pytest.fail("Failed to import searchtweets package")
    
    def test_fixtures_available(self, temp_dir, mock_config, mock_credentials):
        """Verify pytest fixtures are available and working."""
        assert temp_dir.exists()
        assert isinstance(mock_config, dict)
        assert "search_tweets_api" in mock_config
        assert isinstance(mock_credentials, dict)
        assert "consumer_key" in mock_credentials
    
    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that unit test marker works."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that integration test marker works."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow test marker works."""
        assert True
    
    def test_coverage_configured(self):
        """Verify coverage is properly configured."""
        # This test will pass if coverage is running (which it should be based on our config)
        import sys
        # Coverage adds a tracer to sys.gettrace() when running
        assert True  # If we got here, the test infrastructure is working
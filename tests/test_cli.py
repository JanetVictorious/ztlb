"""Tests for CLI application."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ztlb.cli import cli, run_api, start_api


class TestMainCLI:
    """Test main CLI group."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """CLI runner fixture."""
        return CliRunner()

    def test_cli_help(self, runner: CliRunner) -> None:
        """Test CLI help output."""
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert 'ZTL Backend CLI' in result.output
        assert 'API for querying and managing data from various sources' in result.output

    def test_cli_version(self, runner: CliRunner) -> None:
        """Test CLI version output."""
        result = runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert 'ztlb' in result.output

    def test_api_subgroup_exists(self, runner: CliRunner) -> None:
        """Test API subgroup is available."""
        result = runner.invoke(cli, ['api', '--help'])

        assert result.exit_code == 0
        assert 'API management commands' in result.output
        assert 'start' in result.output


class TestAPICommands:
    """Test API command group."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """CLI runner fixture."""
        return CliRunner()

    def test_api_help(self, runner: CliRunner) -> None:
        """Test API help output."""
        result = runner.invoke(run_api, ['--help'])

        assert result.exit_code == 0
        assert 'API management commands' in result.output

    def test_start_command_help(self, runner: CliRunner) -> None:
        """Test start command help."""
        result = runner.invoke(start_api, ['--help'])

        assert result.exit_code == 0
        assert 'Start the FastAPI server' in result.output
        assert '--host' in result.output
        assert '--port' in result.output
        assert '--reload' in result.output
        assert '--workers' in result.output
        assert '--log-level' in result.output


class TestStartAPICommand:
    """Test start API command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """CLI runner fixture."""
        return CliRunner()

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_defaults(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test start API with default parameters."""
        result = runner.invoke(cli, ['api', 'start'])

        assert result.exit_code == 0
        assert 'Starting API server on 0.0.0.0:8000' in result.output

        mock_uvicorn_run.assert_called_once_with(
            'ztlb.main:app',
            host='0.0.0.0',
            port=8000,
            reload=False,
            workers=1,
            log_level='info',
        )

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_custom_host_port(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test start API with custom host and port."""
        result = runner.invoke(cli, ['api', 'start', '--host', '127.0.0.1', '--port', '9000'])

        assert result.exit_code == 0
        assert 'Starting API server on 127.0.0.1:9000' in result.output

        mock_uvicorn_run.assert_called_once_with(
            'ztlb.main:app',
            host='127.0.0.1',
            port=9000,
            reload=False,
            workers=1,
            log_level='info',
        )

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_with_reload(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test start API with reload enabled."""
        result = runner.invoke(cli, ['api', 'start', '--reload'])

        assert result.exit_code == 0
        assert 'Starting API server on 0.0.0.0:8000' in result.output
        assert 'Running in development mode with auto-reload' in result.output

        mock_uvicorn_run.assert_called_once_with(
            'ztlb.main:app',
            host='0.0.0.0',
            port=8000,
            reload=True,
            workers=1,  # Should be 1 when reload is True
            log_level='info',
        )

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_workers_constraint_with_reload(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test workers constraint when reload is enabled."""
        result = runner.invoke(cli, ['api', 'start', '--reload', '--workers', '4'])

        assert result.exit_code == 0

        # Workers should be forced to 1 when reload=True
        mock_uvicorn_run.assert_called_once_with(
            'ztlb.main:app',
            host='0.0.0.0',
            port=8000,
            reload=True,
            workers=1,  # Should override --workers=4
            log_level='info',
        )

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_workers_without_reload(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test workers setting without reload."""
        result = runner.invoke(cli, ['api', 'start', '--workers', '4'])

        assert result.exit_code == 0

        mock_uvicorn_run.assert_called_once_with(
            'ztlb.main:app',
            host='0.0.0.0',
            port=8000,
            reload=False,
            workers=4,  # Should respect --workers=4
            log_level='info',
        )

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_custom_log_level(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test start API with custom log level."""
        result = runner.invoke(cli, ['api', 'start', '--log-level', 'debug'])

        assert result.exit_code == 0

        mock_uvicorn_run.assert_called_once_with(
            'ztlb.main:app',
            host='0.0.0.0',
            port=8000,
            reload=False,
            workers=1,
            log_level='debug',
        )

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_all_options(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test start API with all custom options."""
        result = runner.invoke(
            cli, ['api', 'start', '--host', 'localhost', '--port', '3000', '--workers', '2', '--log-level', 'warning']
        )

        assert result.exit_code == 0
        assert 'Starting API server on localhost:3000' in result.output

        mock_uvicorn_run.assert_called_once_with(
            'ztlb.main:app',
            host='localhost',
            port=3000,
            reload=False,
            workers=2,
            log_level='warning',
        )


class TestErrorHandling:
    """Test CLI error handling."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """CLI runner fixture."""
        return CliRunner()

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_module_not_found_error(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test handling of ModuleNotFoundError."""
        mock_uvicorn_run.side_effect = ModuleNotFoundError('No module named ztlb.main')

        result = runner.invoke(cli, ['api', 'start'])

        assert result.exit_code == 1  # click.Abort() returns exit code 1
        assert 'API module not found: No module named ztlb.main' in result.output
        assert 'Make sure the API module is properly implemented' in result.output

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_general_error(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test handling of general exceptions."""
        mock_uvicorn_run.side_effect = RuntimeError('Server failed to start')

        result = runner.invoke(cli, ['api', 'start'])

        assert result.exit_code == 1  # click.Abort() returns exit code 1
        assert 'Failed to start the API: Server failed to start' in result.output

    @patch('ztlb.cli.uvicorn.run')
    def test_start_api_keyboard_interrupt(self, mock_uvicorn_run, runner: CliRunner) -> None:
        """Test handling of KeyboardInterrupt."""
        mock_uvicorn_run.side_effect = KeyboardInterrupt()

        result = runner.invoke(cli, ['api', 'start'])

        assert result.exit_code == 1  # click.Abort() returns exit code 1
        assert 'Aborted!' in result.output  # KeyboardInterrupt shows as "Aborted!"


class TestCommandIntegration:
    """Test command integration and structure."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """CLI runner fixture."""
        return CliRunner()

    def test_command_structure(self, runner: CliRunner) -> None:
        """Test overall command structure."""
        # Test main CLI help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        # Test API subgroup help
        result = runner.invoke(cli, ['api', '--help'])
        assert result.exit_code == 0
        assert 'start' in result.output

    def test_context_object(self, runner: CliRunner) -> None:
        """Test context object initialization."""
        # This tests that ctx.ensure_object(dict) works
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

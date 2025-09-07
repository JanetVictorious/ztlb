"""CLI for ZTL Backend."""

import click
import uvicorn

from .version import __version__


@click.group()
@click.version_option(version=__version__, prog_name='ztlb')
@click.pass_context
def cli(ctx: click.Context) -> None:
    """ZTL Backend CLI - API for querying and managing data from various sources."""
    ctx.ensure_object(dict)


@click.group()
def run_api() -> None:
    """API management commands."""
    pass


@run_api.command(name='start')
@click.option('--host', default='0.0.0.0', help='Host to run the API on')
@click.option('--port', default=8000, help='Port to run the API on')
@click.option('--reload', is_flag=True, help='Reload the API on code changes')
@click.option('--workers', default=1, help='Number of workers to run the API on')
@click.option('--log-level', default='info', help='Log level for the API')
def start_api(host: str, port: int, reload: bool, workers: int, log_level: str) -> None:
    """Start the FastAPI server."""
    try:
        click.echo(f'Starting API server on {host}:{port}')
        if reload:
            click.echo('Running in development mode with auto-reload')

        uvicorn.run(
            'ztlb.main:app',
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,  # uvicorn doesn't support workers with reload
            log_level=log_level,
        )
    except ModuleNotFoundError as e:
        click.secho(f'API module not found: {e}', fg='red')
        click.secho('Make sure the API module is properly implemented', fg='yellow')
        raise click.Abort() from e
    except Exception as e:
        click.secho(f'Failed to start the API: {e}', fg='red')
        raise click.Abort() from e


# Add the API commands group
cli.add_command(run_api, name='api')


if __name__ == '__main__':
    cli()

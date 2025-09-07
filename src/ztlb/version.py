"""The `version` module holds the version information for ztlb."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version('ztlb')
except importlib.metadata.PackageNotFoundError:
    # Package is not installed
    __version__ = '0.0.1'  # Fallback for development mode

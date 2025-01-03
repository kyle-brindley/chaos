from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("chaos")
except PackageNotFoundError:
    try:
        from chaos import _version  # type: ignore[attr-defined]

        __version__ = _version.version
    except ImportError:
        # Should only hit this when running as an un-installed package in the
        # local repository
        import pathlib
        import warnings

        warnings.filterwarnings(
            action="ignore",
            message="tag",
            category=UserWarning,
            module="setuptools_scm",
        )
        import setuptools_scm

        __version__ = setuptools_scm.get_version(
            root=pathlib.Path(__file__).parent.parent
        )

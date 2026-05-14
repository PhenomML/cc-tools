def pytest_addoption(parser):
    parser.addoption(
        "--regenerate",
        action="store_true",
        default=False,
        help="Reconvert from cached tarballs (fetch tarball from arXiv if not cached).",
    )
    parser.addoption(
        "--refetch",
        action="store_true",
        default=False,
        help="Force re-download of tarballs from arXiv, then reconvert.",
    )

import pytest

from notebooker.constants import (
    DEFAULT_DATABASE_NAME,
    DEFAULT_RESULT_COLLECTION_NAME,
    DEFAULT_SERIALIZER,
)
from notebooker.settings import WebappConfig
from notebooker.utils import caching
from notebooker.utils.filesystem import initialise_base_dirs, _cleanup_dirs
from notebooker.web.app import create_app, setup_app


@pytest.fixture
def bson_library(mongo_server, test_db_name, test_lib_name):
    return mongo_server.api[test_db_name][test_lib_name]


@pytest.fixture
def mongo_host(mongo_server):
    return f"{mongo_server.hostname}:{mongo_server.port}"


@pytest.fixture
def test_db_name():
    return DEFAULT_DATABASE_NAME


@pytest.fixture
def test_lib_name():
    return DEFAULT_RESULT_COLLECTION_NAME


@pytest.fixture
def template_dir(workspace):
    return workspace.workspace


@pytest.fixture
def output_dir(workspace):
    return workspace.workspace


@pytest.fixture
def cache_dir(workspace):
    return workspace.workspace


@pytest.fixture
def py_template_dir(workspace):
    return workspace.workspace


def safe_cache_clear():
    if caching.cache is not None:
        try:
            caching.cache.clear()
        except FileNotFoundError:
            pass


@pytest.fixture
def clean_file_cache(monkeypatch, workspace):
    """Set up cache environment."""
    safe_cache_clear()
    monkeypatch.setenv("CACHE_DIR", workspace.workspace)
    yield
    # purge the cache
    safe_cache_clear()
    caching.cache = None


@pytest.fixture()
def webapp_config(mongo_host, test_db_name, test_lib_name, template_dir, cache_dir, output_dir, workspace):
    return WebappConfig(
        CACHE_DIR=cache_dir,
        OUTPUT_DIR=output_dir,
        TEMPLATE_DIR=template_dir,
        DISABLE_SCHEDULER=False,
        SERIALIZER_CLS=DEFAULT_SERIALIZER,
        SERIALIZER_CONFIG={
            "mongo_host": mongo_host,
            "database_name": test_db_name,
            "result_collection_name": test_lib_name,
        },
        PY_TEMPLATE_BASE_DIR=workspace.workspace,
        PY_TEMPLATE_SUBDIR="templates",
    )


@pytest.fixture
def flask_app(webapp_config):
    flask_app = create_app(webapp_config)
    flask_app = setup_app(flask_app, webapp_config)
    flask_app.config["DEBUG"] = True
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def setup_and_cleanup_notebooker_filesystem(webapp_config):
    try:
        initialise_base_dirs(webapp_config=webapp_config)
        yield
    finally:
        _cleanup_dirs(webapp_config)

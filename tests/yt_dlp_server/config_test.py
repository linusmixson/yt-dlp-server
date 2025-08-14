import os
from contextlib import contextmanager

from yt_dlp_server.config import YtDlpSettings


@contextmanager
def env(**kwargs: str):
    old = {k: os.environ.get(k) for k in kwargs}
    try:
        os.environ.update({k: v for k, v in kwargs.items() if v is not None})
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_defaults_load():
    settings = YtDlpSettings()
    # A couple of representative defaults
    assert settings.ignoreerrors is False
    assert settings.default_search == "auto"
    assert settings.retries == 10
    assert settings.addchapters is True


def test_env_loading_bool_and_int_and_str_list():
    with env(YT_DLP_IGNOREERRORS="true", YT_DLP_RETRIES="5", YT_DLP_FORMAT_SORT='["filesize","vcodec"]'):
        settings = YtDlpSettings()
        assert settings.ignoreerrors is True
        assert settings.retries == 5
        assert settings.format_sort == ["filesize", "vcodec"]


def test_env_loading_literal_and_tuple():
    with env(YT_DLP_FORCE_IP="6", YT_DLP_WAIT_FOR_VIDEO='[10,20]'):
        settings = YtDlpSettings()
        assert settings.force_ip == "6"
        assert settings.wait_for_video == (10, 20)


def test_env_loading_nested_structures():
    with env(
        YT_DLP_PRINT_TO_FILE='{"filename":"title"}',
        YT_DLP_FORCEPRINT='{"title":["webpage_url","n_entries"]}',
    ):
        settings = YtDlpSettings()
        assert settings.print_to_file == {"filename": "title"}
        assert settings.forceprint == {"title": ["webpage_url", "n_entries"]}


def test_env_retries_infinite_literal():
    with env(YT_DLP_RETRIES="infinite"):
        settings = YtDlpSettings()
        assert settings.retries == "infinite"


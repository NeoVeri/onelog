import logging

import pytest

import onelog


@pytest.fixture(autouse=True)
def reset_onelog_state():
    onelog._configured = False
    onelog._global_config = None
    logging.getLogger().handlers.clear()
    yield
    logging.getLogger().handlers.clear()


def test_package_exposes_version_and_logger():
    logger = onelog.get_logger(
        __name__,
        level=logging.DEBUG,
        show_summary=False,
        gen_log=False,
    )

    assert onelog.__version__ == "0.1.0"
    assert isinstance(logger, logging.Logger)


def test_fatal_logs_and_exits_with_one():
    logger = onelog.get_logger(
        __name__,
        show_summary=False,
        gen_log=False,
    )

    with pytest.raises(SystemExit) as raised:
        logger.fatal("无法继续")

    assert raised.value.code == 1

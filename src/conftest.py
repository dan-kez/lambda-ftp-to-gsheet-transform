from random import random

import pytest

import settings
from models.create_models import create_models, delete_models
from utils import ftp_connection
from utils.ftp_connection import close_ftp_connection


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: only run with a scaffolded integration environment"
    )


@pytest.fixture(scope="session")
def monkeysession():
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def mock_stage(monkeysession):
    monkeysession.setattr(settings, "STAGE", "test")


@pytest.fixture(scope="session", autouse=True)
def mock_no_ftp_connection(monkeysession, sftpserver):
    """Remove requests.sessions.Session.request for all tests."""
    with sftpserver.serve_content(
        {
            "Usr": {
                "macship": {
                    "EDITRADEOUT": {
                        "002113": {
                            "EntryExtract-141716-D37{2020-03-30-121915}{D3538EB5-2207-4391-8A5D-3932603C0D21}.xml": "File Content",
                            "EntryExtract-141717-D37{2020-03-18-093014}{3375FE7B-9086-445F-9147-44A3696B54A1}.xml": "File Content",
                        },
                        "001940": {
                            "EntryExtract-141856-D37{2020-04-04-094100}{29D81A29-34FB-4993-AE12-8F19986EAA13}.xml": "File Content",
                            "EntryExtract-141888-D37{2020-04-04-094106}{A5058E79-2160-4F4E-8E3D-9F406D918449}.xml": "File Content",
                        },
                    }
                },
            },
        }
    ):
        monkeysession.setattr(ftp_connection, "allow_connection_reuse", True)
        monkeysession.setattr(settings, "FTP_HOST", sftpserver.host)
        monkeysession.setattr(settings, "FTP_PORT", sftpserver.port)
        monkeysession.setattr(settings, "EDITRADE_FTP_USERNAME", "user")
        monkeysession.setattr(settings, "EDITRADE_FTP_PASSWORD", "pw")
        yield
    close_ftp_connection()


@pytest.fixture()
def fixture_model_management(monkeypatch):
    rand_num = str(int(random() * 10000))
    monkeypatch.setattr(settings, "DYNAMO_TABLE_PREFIX", f"test_table_{rand_num}__")

    create_models()
    yield
    delete_models()

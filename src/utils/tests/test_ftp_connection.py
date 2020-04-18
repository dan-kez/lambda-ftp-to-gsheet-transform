import os
import settings


def test_get_all_files_recursively():
    from utils.ftp_connection import get_all_files_recursively, open_ftp_connection

    ftp_connection = open_ftp_connection(
        settings.FTP_HOST,
        settings.FTP_PORT,
        settings.EDITRADE_FTP_USERNAME,
        settings.EDITRADE_FTP_PASSWORD,
    )
    assert get_all_files_recursively(ftp_connection) == {
        "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141856-D37{2020-04-04-094100}{29D81A29-34FB-4993-AE12-8F19986EAA13}.xml",
        "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{2020-04-04-094106}{A5058E79-2160-4F4E-8E3D-9F406D918449}.xml",
        "/Usr/macship/EDITRADEOUT/002113/EntryExtract-141716-D37{2020-03-30-121915}{D3538EB5-2207-4391-8A5D-3932603C0D21}.xml",
        "/Usr/macship/EDITRADEOUT/002113/EntryExtract-141717-D37{2020-03-18-093014}{3375FE7B-9086-445F-9147-44A3696B54A1}.xml",
    }


def test_get_all_files_recursively_with_base_path():

    from utils.ftp_connection import get_all_files_recursively, open_ftp_connection

    ftp_connection = open_ftp_connection(
        settings.FTP_HOST,
        settings.FTP_PORT,
        settings.EDITRADE_FTP_USERNAME,
        settings.EDITRADE_FTP_PASSWORD,
    )
    assert get_all_files_recursively(
        ftp_connection, root_path="/Usr/macship/EDITRADEOUT"
    ) == {
        "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141856-D37{2020-04-04-094100}{29D81A29-34FB-4993-AE12-8F19986EAA13}.xml",
        "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{2020-04-04-094106}{A5058E79-2160-4F4E-8E3D-9F406D918449}.xml",
        "/Usr/macship/EDITRADEOUT/002113/EntryExtract-141716-D37{2020-03-30-121915}{D3538EB5-2207-4391-8A5D-3932603C0D21}.xml",
        "/Usr/macship/EDITRADEOUT/002113/EntryExtract-141717-D37{2020-03-18-093014}{3375FE7B-9086-445F-9147-44A3696B54A1}.xml",
    }

    assert get_all_files_recursively(
        ftp_connection, root_path=os.path.join(settings.FTP_ROOT_DIR, "001940")
    ) == {
        "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141856-D37{2020-04-04-094100}{29D81A29-34FB-4993-AE12-8F19986EAA13}.xml",
        "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{2020-04-04-094106}{A5058E79-2160-4F4E-8E3D-9F406D918449}.xml",
    }

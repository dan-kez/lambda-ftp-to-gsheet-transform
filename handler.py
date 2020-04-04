class NoFilesToProcess(Exception):
    pass


def checknewfiles(event, context):
    if event and event.get("throw"):
        raise NoFilesToProcess

    return ["file_path1", "file_path2"]


def downloadandprocesseditradefile(event, context):
    """

    :param event: ftp file path to process
    :param context:
    :return: None
    """
    print(f"{event}")
    return None

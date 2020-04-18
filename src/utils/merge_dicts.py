def merge_dicts(a, b, path=None):
    """
    https://stackoverflow.com/a/7205107/3735630
    merges b into a.
    THIS WILL MUTATE `a`
    To prevent mutation call like so merge_dicts(dict(a), b)
    Note this will not merge list values
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a

""" misc utils """

def json_dumpable_tuple_dict(the_dict):
    """ convert dict with keys that are tuples
        to a dict with keys that are strings

    :param the_dict: ({tuple: obj})
    :return: ({str: obj})
    """

    def to_key(obj):
        return (
            f'({",".join(str(o) for o in obj)})'
            if isinstance(obj, tuple)
            else obj
        )

    return {to_key(k): v for k, v in the_dict.items()}

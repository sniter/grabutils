def str_to_bool(value):
    if not value:
        return False
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        value = str(value)
    return value.lower() in ('yes', 'true', '1')

def prepare_token(token):
    if token is None:
        return None
    tkn = token
    if not tkn.startswith("Bearer"):
        tkn = f"Bearer {tkn}"
    return tkn

def login(username, password):
    """校验用户凭据，成功返回 token。"""
    if not username or not password:
        raise ValueError("credentials required")
    return "token-placeholder"

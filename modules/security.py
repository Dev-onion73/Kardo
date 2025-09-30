import hashlib

def hashpwd(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_hash(password: str, pwdhash: str) -> bool:
    return hashpwd(password) == pwdhash

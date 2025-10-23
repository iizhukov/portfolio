import os
import sys
from typing import Optional


def getenv(key: str, default: Optional[str] = None) -> str:
    value = os.getenv(key, default)
    
    if value is None:
        print(f"ERROR: Required environment variable '{key}' is not set!")
        sys.exit(1)
    
    return value


def getenv_int(key: str, default: Optional[int] = None) -> int:
    value = getenv(key, str(default) if default is not None else None)
    
    try:
        return int(value)
    except ValueError:
        print(f"ERROR: Environment variable '{key}' must be an integer, got: '{value}'")
        sys.exit(1)


def getenv_bool(key: str, default: Optional[bool] = None) -> bool:
    value = getenv(key, str(default).lower() if default is not None else None)
    
    if value.lower() in ('true', '1', 'yes', 'on'):
        return True
    elif value.lower() in ('false', '0', 'no', 'off'):
        return False
    else:
        print(f"ERROR: Environment variable '{key}' must be a boolean value (true/false), got: '{value}'")
        sys.exit(1)


def getenv_list(key: str, separator: str = ',', default: Optional[list] = None) -> list:
    value = getenv(key, separator.join(default) if default is not None else None)
    
    if not value.strip():
        return []
    
    return [item.strip() for item in value.split(separator) if item.strip()]


def validate_required_env_vars(required_vars: list[str]) -> None:
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var) is None:
            missing_vars.append(var)
    
    if missing_vars:
        print("ERROR: The following required environment variables are not set:")

        for var in missing_vars:
            print(f"   - {var}")

        print("\nSet the variables:")

        for var in missing_vars:
            print(f"   export {var}=<value>")


def print_env_info(env_vars: dict[str, str]) -> None:
    print("Environment variables:")

    for key, value in env_vars.items():
        if any(secret in key.lower() for secret in ['password', 'secret', 'key', 'token']):
            display_value = "***" if value else "not set"
        else:
            display_value = value or "not set"

        print(f"   {key}: {display_value}")

    print()


def create_env_file(env_vars: dict[str, str], filename: str = ".env") -> None:
    with open(filename, 'w') as f:
        f.write("# Environment Variables\n")
        
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"{filename} created with environment variables")

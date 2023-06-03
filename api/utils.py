def capitalize_each_word(str_: str) -> str:
    return " ".join(part.capitalize() for part in str_.split())

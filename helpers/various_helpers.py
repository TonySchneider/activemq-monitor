from typing import List


def convert_comma_separated_str_to_list(text: str) -> List[str]:
    """
    This function parses text that separated by commas and returns it as a list of strings
    """
    separated = [item.strip() for item in text.split(",")]
    return separated

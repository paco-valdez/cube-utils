from urllib.parse import urlparse, parse_qs, unquote


def extract_url_params(url: str) -> dict:
    """
    Extract query parameters from a URL using urllib only.

    Args:
        url (str): The input URL string.

    Returns:
        dict: A dictionary of query parameters with URL-decoded values.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Flatten single-element lists and decode values
    return {
        key: unquote(value[0]) if len(value) == 1 else [unquote(v) for v in value]
        for key, value in query_params.items()
    }

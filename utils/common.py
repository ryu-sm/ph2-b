from urllib.parse import urlparse


def parse_endpoint(url: str, path_params: dict):
    try:
        result = urlparse(url).path
        for key, value in path_params.items():
            result = result.replace(f"/{value}", "/{" + key + "}")
        return result
    except Exception:
        return None

import sys, os
import base64, requests


def open_directory(path):
    if sys.platform.startswith("darwin"):  # macOS
        os.system('open "{}"'.format(path))
    elif sys.platform.startswith("win"):  # Windows
        os.system('start "" "{}"'.format(path))
    elif sys.platform.startswith("linux"):  # Linux
        os.system('xdg-open "{}"'.format(path))
    else:
        print("Unsupported operating system.")


def download_image_as_base64(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()  # URL이 올바른지 확인하고, 문제가 있으면 예외 발생
    image_data = response.content
    base64_encoded = base64.b64encode(image_data).decode("utf-8")
    return base64_encoded

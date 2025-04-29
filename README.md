# Hotel ID Extractor API

This FastAPI application fetches the full HTML content of a given URL using a headless Chromium browser (via Playwright). It is designed to run as a standalone API service and can be used for tasks such as extracting hotel data or any other web content.

## Features

- Launches a headless Chromium browser on startup
- Navigates to the requested URL and returns the full HTML content
- Supports Bearer Token authentication using a list of tokens defined via environment variables
- Automatically shuts down the browser on service stop

## Requirements

- Python 3.8+
- Playwright
- FastAPI
- Uvicorn

## Installation

1. Install dependencies:

```bash
pip install fastapi uvicorn playwright
playwright install
```

2. Set the environment variable with allowed Bearer tokens:

```bash
export BEARER_TOKENS=token123,token456
```

3. Run the API:

```bash
uvicorn hotelidextractor_with_auth:app --host 0.0.0.0 --port 8000
```

## Usage

Send a GET request to `/fetch-html/` with the target URL and an authorized Bearer token:

```bash
curl -H "Authorization: Bearer token123" "http://localhost:8000/fetch-html/?url=https://example.com"
```

### Response

```json
{
  "url": "https://example.com",
  "html": "<!DOCTYPE html>..."
}
```

## Environment Variables

- `BEARER_TOKENS`: A comma-separated list of allowed tokens (e.g., `token123,token456`).

## License

This project is licensed under the MIT License.
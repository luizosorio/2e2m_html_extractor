import logging
import os

from fastapi import Depends
from fastapi import FastAPI, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from playwright.async_api import async_playwright, Browser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

app = FastAPI()
security = HTTPBearer()
ALLOWED_TOKENS = set(os.getenv("BEARER_TOKENS", "").split(","))

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print(f"Received Token: {token}")
    print(f"ALLOWED_TOKENS: {ALLOWED_TOKENS}")
    if token not in ALLOWED_TOKENS:
        raise HTTPException(status_code=403, detail="Invalid or missing token")


# Global browser instance
browser: Browser = None


@app.on_event("startup")
async def startup_event():
    """
    Start the browser when the API starts.
    """
    global browser
    try:
        logging.info("Starting the browser asynchronously...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)  # Headless mode
        logging.info("Browser started successfully.")
    except Exception as e:
        logging.error(f"Failed to start browser: {e}")
        raise RuntimeError(f"Failed to start browser: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Close the browser when the API shuts down.
    """
    global browser
    if browser:
        logging.info("Shutting down the browser asynchronously...")
        await browser.close()
        logging.info("Browser shut down successfully.")


@app.get("/fetch-html/")
async def fetch_html(url: str, request: Request, credentials: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Fetch the HTML content of a given URL.
    """
    print("Received Headers:", request.headers)

    global browser
    logging.info(f"Received request to fetch HTML for URL: {url}")

    if not browser:
        logging.error("Browser is not initialized.")
        raise HTTPException(status_code=500, detail="Browser not initialized")

    try:
        logging.info(f"Creating a new context and page for URL: {url}")
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, java_script_enabled=True,
                                            ignore_https_errors=True)
        async with context:
            page = await context.new_page()
            redirected_url = None

            def handle_response(response):
                nonlocal redirected_url
                if response.status == 301 or response.status == 302:
                    # logging.info(f"Redirect {response.status} detected: {response.url}")
                    if response.status == 301:
                        redirected_url = response.url

            def handle_route(route, request):
                logging.info(f">>>>>>>>>>>>>> {route} >>>>> {request}")
                if request.is_navigation_request() and request.method == "GET":
                    response = route.continue_()
                    if response.status == 302:
                        logging.info(f"Redirect 302 detected and ignored: {response.url}")
                        route.abort()
                        return
                else:
                    route.continue_()

            network_requests = []
            visited_urls = []

            page.on('response', handle_response)
            page.on('route', handle_route)
            page.on("framenavigated", lambda frame: visited_urls.append(frame.url))
            page.on("request", lambda request: network_requests.append(request.url))

            try:
                logging.info(f"Navigating to URL: {url}")
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
                final_url = page.url

                logging.info(f"Successfully fetched HTML for URL: {final_url}")

                return {
                    "url": final_url,
                    "requests": network_requests,
                    "frames": visited_urls,
                    "html": content
                }

            finally:
                logging.info("Closing the page...")
                await page.close()
    except Exception as e:
        logging.error(f"Error processing URL {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing URL: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
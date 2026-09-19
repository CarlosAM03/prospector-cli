import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

from engines.website.website_engine import WebsiteEngine


class ControlledHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = (
            "<html lang='es'><head><title>Controlled Site</title>"
            "<meta name='description' content='Controlled description'>"
            "</head><body><a href='mailto:info@example.test'>"
            "info@example.test</a></body></html>"
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


def test_website_engine_inspects_controlled_local_page():
    server = ThreadingHTTPServer(("127.0.0.1", 0), ControlledHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                metadata = WebsiteEngine(browser).inspect(url)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert metadata.status_code == 200
    assert metadata.title == "Controlled Site"
    assert metadata.description == "Controlled description"
    assert metadata.language == "es"
    assert metadata.emails == ["info@example.test"]
    assert metadata.final_url == url
    assert metadata.domain.startswith("127.0.0.1:")

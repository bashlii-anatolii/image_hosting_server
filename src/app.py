import http.server
import socketserver
import os
import json
import io
import re
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from validators import validate_image_file
from file_handler import save_file, delete_file, list_images_with_preview
from database import DatabaseManager

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

os.makedirs(LOG_DIR, exist_ok=True)


class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_time = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{log_time}] {record.levelname}: {record.getMessage()}"


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(CustomFormatter())

console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())

logger.addHandler(file_handler)
logger.addHandler(console_handler)

db = DatabaseManager()


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.address_string(), format % args))

    def do_GET(self):
        logger.info(f"GET request: {self.path}")
        routes = {
            "/": "index.html",
            "/upload": "upload.html",
            "/images-list": "images.html"
        }
        if self.path in routes:
            self.serve_template(routes[self.path])
        elif self.path.startswith("/static/"):
            self.serve_static(self.path)
        elif self.path.startswith("/api/images"):
            self.handle_get_images()
        else:
            logger.warning(f"404 Not Found: {self.path}")
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        logger.info(f"POST request: {self.path}")
        if self.path == "/upload":
            self.handle_upload()
        else:
            logger.warning(f"404 Not Found: {self.path}")
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        logger.info(f"DELETE request: {self.path}")
        if self.path.startswith("/api/images"):
            self.handle_delete_image()
        else:
            logger.warning(f"404 Not Found: {self.path}")
            self.send_response(404)
            self.end_headers()

    def handle_upload(self):
        try:
            content_type = self.headers.get("Content-Type", "")
            if not content_type.startswith("multipart/form-data"):
                logger.warning(f"Invalid content type: {content_type}")
                self.send_error(400, "Expected multipart/form-data")
                return

            form_data = self.rfile.read(int(self.headers["Content-Length"]))
            filename = self._extract_filename(form_data)
            logger.info(f"Uploading file: {filename}")

            file_like = io.BytesIO(form_data)
            is_valid, message = validate_image_file(file_like, filename)

            if not is_valid:
                logger.warning(f"Validation failed for {filename}: {message}")
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": message}).encode("utf-8"))
                return

            file_bytes = self._extract_file_bytes(form_data)
            saved_name = save_file(file_bytes, filename)
            logger.info(f"File saved: {saved_name} (size: {len(file_bytes)} bytes)")

            ext = filename.lower().split(".")[-1]
            db.save_metadata(
                filename=saved_name,
                original_name=filename,
                size=len(file_bytes),
                file_type=ext
            )
            logger.info(f"Metadata saved for: {saved_name}")

            response_data = {
                "success": True,
                "message": "File uploaded successfully",
                "name": saved_name,
                "url": f"https://image-hosting-server.com/{saved_name}"
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            logger.info(f"Upload successful: {saved_name}")

        except Exception as e:
            logger.error(f"Upload error: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            error_response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_response).encode("utf-8"))

    def handle_get_images(self):
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            page = int(params.get('page', [1])[0])
            logger.info(f"Fetching images: page {page}")

            images, total = db.get_all_images(page=page, per_page=10)
            logger.info(f"Retrieved {len(images)} images out of {total} total")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'images': [dict(img) for img in images],
                'total': total,
                'page': page,
                'page_size': 10
            }, default=str).encode('utf-8'))

        except Exception as e:
            logger.error(f"Error fetching images: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))

    def handle_delete_image(self):
        try:
            image_id = int(self.path.split('/')[-1])
            logger.info(f"Deleting image with ID: {image_id}")

            filename = db.delete_image(image_id)
            if filename:
                delete_file(filename)
                logger.info(f"Image deleted successfully: {filename}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'message': f'Image {filename} deleted'}).encode('utf-8'))
            else:
                logger.warning(f"Image not found with ID: {image_id}")
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': 'Image not found'}).encode('utf-8'))
        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))

    def _extract_filename(self, form_data):
        try:
            decoded = form_data.decode("utf-8", errors="ignore")
            match = re.search(r'filename="([^"]+)"', decoded)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"Error extracting filename: {str(e)}")
        return "unknown"

    def _extract_file_bytes(self, form_data):
        boundary = form_data.split(b'\r\n')[0]
        parts = form_data.split(boundary)

        for part in parts:
            if b'Content-Type:' in part or b'filename=' in part:
                header_end = part.find(b'\r\n\r\n')
                if header_end != -1:
                    file_content = part[header_end + 4:]
                    if file_content.endswith(b'\r\n'):
                        file_content = file_content[:-2]
                    return file_content

        return b''

    def serve_template(self, filename):
        try:
            template_path = os.path.join(os.path.dirname(__file__), "templates", filename)
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            logger.debug(f"Served template: {filename}")
        except FileNotFoundError:
            logger.error(f"Template not found: {filename}")
            self.send_response(404)
            self.end_headers()

    def serve_static(self, path):
        try:
            file_path = path[len("/static/"):]
            static_path = os.path.join(os.path.dirname(__file__), "static", file_path)

            with open(static_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            content_type = self.get_content_type(file_path)
            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(content)
            logger.debug(f"Served static file: {file_path}")
        except FileNotFoundError:
            logger.error(f"Static file not found: {path}")
            self.send_response(404)
            self.end_headers()

    def get_content_type(self, file_path):
        if file_path.endswith(".css"):
            return "text/css"
        elif file_path.endswith(".js"):
            return "application/javascript"
        elif file_path.endswith(".png"):
            return "image/png"
        elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
            return "image/jpeg"
        else:
            return "application/octet-stream"


def run_server(port=8000):
    port = int(os.environ.get("PORT", port))
    logger.info(f"Initializing server on port {port}")

    db.connect()
    logger.info("Database connected")

    try:
        with socketserver.TCPServer(("", port), ImageServerHandler) as httpd:
            logger.info(f"Server running on port {port}: http://localhost:{port}")
            print(f"Running server port:{port}: http://localhost:{port}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
                print(f"User stopped server")
    except OSError as e:
        if e.errno == 48:
            logger.error(f"Port {port} is already in use")
            print(f"Port {port} is already use")
            print(f"To stop process on port enter the command: lsof -i :{port} | kill -9 PID")
        else:
            logger.error(f"Error starting server: {e}", exc_info=True)
            print(f"Error starting server: {e}")
    finally:
        db.disconnect()
        logger.info("Database disconnected")
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    logger.info("Application started")
    run_server()
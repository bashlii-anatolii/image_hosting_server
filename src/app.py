import http.server
import socketserver
import os
import json
import io
import re
from validators import validate_image_file
from file_handler import save_file, delete_file, list_images_with_preview


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/images":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(list_images_with_preview()).encode())
            return

        routes = {
            "/": "index.html",
            "/upload": "upload.html",
            "/images-list": "images.html"
        }
        if self.path in routes:
            self.serve_template(routes[self.path])
        elif self.path.startswith("/static/"):
            self.serve_static(self.path)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/upload":
            self.handle_upload()
        elif self.path == "/delete":
            self.handle_delete()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_upload(self):
        try:
            content_type = self.headers.get("Content-Type", "")
            if not content_type.startswith("multipart/form-data"):
                self.send_error(400, "Expected multipart/form-data")
                return

            form_data = self.rfile.read(int(self.headers["Content-Length"]))
            filename = self._extract_filename(form_data)
            file_like = io.BytesIO(form_data)
            is_valid, message = validate_image_file(file_like, filename)

            if not is_valid:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": message}).encode("utf-8"))
                return

            file_bytes = self._extract_file_bytes(form_data)
            saved_name = save_file(file_bytes, filename)
            print(f"Save file: {saved_name}")

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

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            error_response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_response).encode("utf-8"))

    def handle_delete(self):
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

            filename = data.get("filename")

            if not filename:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False}).encode("utf-8"))
                return

            delete = delete_file(filename)
            print(f"File to delete: {filename}")

            if delete:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))

            else:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "File not found"}).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            error_response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_response).encode("utf-8"))

    def _extract_filename(self, form_data):
        try:
            decoded = form_data.decode("utf-8", errors="ignore")
            match = re.search(r'filename="([^"]+)"', decoded)
            if match:
                return match.group(1)
        except Exception:
            pass
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
        except FileNotFoundError:
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
        except FileNotFoundError:
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
    try:
        with socketserver.TCPServer(("", port), ImageServerHandler) as httpd:
            print(f"Running server port:{port}: http://localhost:{port}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print(f"User stopped server")
    except OSError as e:
        if e.errno == 48:
            print(f"Port {port} is already use")
            print(f"To stop process on port enter the command: lsof -i :{port} | kill -9 PID")
        else:
            print(f"Error starting server: {e}")


if __name__ == "__main__":
    run_server()

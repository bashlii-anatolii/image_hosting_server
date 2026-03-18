import http.server
import socketserver
import os
import json


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
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

            response_data = {
                "success": True,
                "message": "File uploaded successfully",
                "url": "https://image-hosting-server.com/upload-file.jpg"
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

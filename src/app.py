import http.server
import socketserver
import os


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.serve_template("index.html")
        elif self.path == "/upload":
            self.serve_template("upload.html")
        elif self.path == "/images-list":
            self.serve_template("images.html")
        else:
            self.send_response(404)
            self.end_headers()

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

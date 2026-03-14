import http.server
import socketserver


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Hello, server</h1>")
        else:
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
        else:
            print(f"Error starting server: {e}")


if __name__ == "__main__":
    run_server()
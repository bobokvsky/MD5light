import uuid
import http.server
import socketserver
import threading
import urllib.parse as urlparse
import cgi

import solver_tasks

PORT = 8000
LOG_FILE_NAME = "log_messages_server.txt"


class StoreHandler(http.server.BaseHTTPRequestHandler):

    solver_tasks = None

    def get_tasks(self):
        return self.solver_tasks

    def set_tasks(self, solver_tasks):
        self.solver_tasks = solver_tasks

    def send_response2(self, response_code, response_reason, contents):
        self.send_response(response_code, response_reason)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(contents))
        self.end_headers()
        self.wfile.write(contents.encode())
        self.wfile.flush()

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        action = parsed_path.path
        if action == "/check":
            params = urlparse.parse_qs(parsed_path.query)
            if "id" in params:
                contents = []
                for task_id in params["id"]:
                    contents.append(self.solver_tasks.get_task(task_id))

                self.send_response2(200., "OK", str(contents))
            else:
                self.send_response2(400., "Bad ID params", "")
        else:
            self.send_response2(400., "Unknown request", "")

    def do_POST(self):
        if self.path == "/submit":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = urlparse.parse_qs(post_data.decode())
            if "url" in params and len(params["url"]) == 1:
                if not ("email" in params and len(params["email"]) > 1):
                    if "email" not in params:
                        params["email"] = [None]

                    for url, email in zip(params["url"], params["email"]):
                        answer = self.solver_tasks.add_task(url, email)

                    self.send_response2(200., "OK", answer)
                else:
                    self.send_response2(400., "Email invalid", "Email invalid")
            else:
                self.send_response2(400., "URL invalid", "URL invalid")
        else:
            self.send_response2(400., "Unknown request", "Unknown request")

    def log_message(self, format, *args):
        with open(LOG_FILE_NAME, "a") as f:
            f.write("%s - - [%s] %s\n" %
                    (self.address_string(), self.log_date_time_string(),
                        format % args))


class SimpleServer():
    def __init__(self, port=PORT):
        self.httpd = socketserver.TCPServer(("", PORT), StoreHandler)

        self.is_serving = False
        self.lock = threading.Lock()

    def get_is_serving(self):
        self.lock.acquire()
        res = self.is_serving
        self.lock.release()
        return res

    def set_is_serving(self, value):
        self.lock.acquire()
        self.is_serving = value
        self.lock.release()

    def run(self, tasks) -> str:
        if not self.get_is_serving():
            self.set_is_serving(True)
            self.thread = threading.Thread(target=self.serve_forever)
            self.thread.start()

            handler = self.httpd.RequestHandlerClass
            if handler.get_tasks(handler) is None:
                handler.set_tasks(handler, tasks)
            return "Server run."
        else:
            return "Server is already running."

    def serve_forever(self):
        self.httpd.serve_forever()

    def shutdown(self) -> str:
        if self.get_is_serving():
            self.httpd.shutdown()
            self.set_is_serving(False)
            self.thread.join()

            return "Server shut down."
        else:
            return "Server is already shut down."

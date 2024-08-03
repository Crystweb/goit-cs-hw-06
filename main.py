import socket
import threading
import datetime
import http.server
import socketserver
import json
from urllib.parse import parse_qs
from pymongo import MongoClient

# Налаштування для MongoDB
mongo_client = MongoClient(
    'mongodb+srv://goit-test:rVoIjkuy~8DPWi!mV7@testcluster.dwyiq17.mongodb.net/?retryWrites=true&w=majority&ssl=true'
    '&appName=TestCluster')
db = mongo_client['app_db']
collection = db['messages']

# Налаштування для HTTP-сервера
PORT = 3000
Handler = http.server.SimpleHTTPRequestHandler


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            parsed_data = parse_qs(post_data.decode('utf-8'))

            message_data = {
                "date": datetime.datetime.now().isoformat(),
                "username": parsed_data['username'][0],
                "message": parsed_data['message'][0]
            }

            # Відправлення даних на Socket-сервер
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', 5000))
                s.sendall(json.dumps(message_data).encode('utf-8'))

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(404, 'File Not Found')

    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        elif self.path == '/message.html':
            self.path = 'message.html'
        elif self.path == '/style.css':
            self.path = 'style.css'
        elif self.path == '/logo.png':
            self.path = 'logo.png'
        else:
            self.path = 'error.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def run_http_server():
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()


# Налаштування для Socket-сервера
def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', 5000))
        server_socket.listen()
        print("Socket server running on port 5000")
        while True:
            conn, addr = server_socket.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    message_data = json.loads(data.decode('utf-8'))
                    collection.insert_one(message_data)
                    print(f"Received and stored: {message_data}")


if __name__ == "__main__":
    threading.Thread(target=run_http_server).start()
    threading.Thread(target=run_socket_server).start()

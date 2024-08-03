import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import socket
import threading
import json
import datetime
from pymongo import MongoClient
from urllib.parse import parse_qs


# HTTP Server
class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/templates/index.html'
        elif self.path == '/message.html':
            self.path = '/templates/message.html'
        elif self.path.startswith('/static'):
            self.path = self.path
        else:
            self.path = '/templates/error.html'
            self.send_error(404)
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_params = parse_qs(post_data.decode('utf-8'))
            username = post_params['username'][0]
            message = post_params['message'][0]
            send_message_to_socket_server(username, message)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()


def run_http_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()


# Socket Server
def socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5000))
    server_socket.listen(5)

    client = MongoClient('mongodb://mongodb:27017/')
    db = client.mydatabase
    collection = db.messages

    while True:
        client_socket, addr = server_socket.accept()
        data = client_socket.recv(1024)
        message_data = json.loads(data.decode('utf-8'))
        message_data['date'] = str(datetime.datetime.now())
        collection.insert_one(message_data)
        client_socket.close()


def send_message_to_socket_server(username, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('socket-server', 5000))
    message_data = json.dumps({'username': username, 'message': message})
    client_socket.send(message_data.encode('utf-8'))
    client_socket.close()


if __name__ == '__main__':
    threading.Thread(target=run_http_server).start()
    threading.Thread(target=socket_server).start()

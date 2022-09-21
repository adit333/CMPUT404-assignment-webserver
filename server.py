#  coding: utf-8 
import datetime
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

BASEPATH = "www"

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        decoded_data = self.data.decode("utf-8")
        header_line = decoded_data.split("\r\n")[0]
        header = header_line.split(" ")

        if header[0] != "GET":
            self.request.sendall(bytearray(f"HTTP/1.1 405 Method Not Allowed", "utf-8"))
        
        self.handle_get_request(header[1])

        self.request.sendall(bytearray("OK",'utf-8'))
    
    def handle_get_request(self, relative_path):
        # Check if the path is a directory
        if relative_path[-1] == "/":
            relative_path += "index.html"
        
        path = os.path.join(BASEPATH, relative_path[1:])
        # Check if the path is valid
        if not os.path.exists(path):
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found", "utf-8"))
            return

        # Check if the path is a file
        if os.path.isfile(path):
            self.send_file(path)
            return

        # Check if the path is a directory
        if os.path.isdir(path):
            self.handle_directory(path)
            return

    def send_file(self, path):
        if not path.endswith(".html") and not path.endswith(".css"):
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found", "utf-8"))
            return

        with open(path, "r") as f:
            content = f.read()
        
        content_length = len(content)
        if path.endswith(".css"):
            content_type = "text/css"
        else:
            content_type = "text/html"
        date = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")

        response = "HTTP/1.1 200 OK\r\n"
        response += f"Date: {date}\r\n"
        response += f"Content-Length: {content_length}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Connection: Closed\r\n"
        response += f"\r\n"
        response += content

        self.request.sendall(bytearray(response, "utf-8"))

    def handle_directory(self, path):
        if not path.endswith("/"):
            path += "/"
            self.request.sendall(
                bytearray(
                    f"HTTP/1.1 301 Moved Permanently\n Location:http://HTTP/1.1{path}/\r\n\r\n ",
                    "utf-8"
                )
            )


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

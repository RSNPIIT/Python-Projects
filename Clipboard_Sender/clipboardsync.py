#!/usr/bin/env python3
import ssl
import http.server, socketserver, subprocess, urllib.parse

PORT = 5050
CLIPFILE = "/home/kali/latest_clip.txt"

HTML = """
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { font-family: sans-serif; padding: 15px; }
.box { border:1px solid #ccc; padding:10px; border-radius:6px; white-space:pre-wrap; }
button { padding:8px 14px; margin-top:10px; }
textarea { width:100%; }
</style>
</head>
<body>

<h2>Clipboard Sync</h2>

<h3>Laptop → Phone (Auto)</h3>
<div id="laptop_clipboard" class="box">(waiting...)</div>
<button onclick="copyToClipboard()">Copy to phone clipboard</button>

<script>
async function fetchClip() {
    let r = await fetch("/latest");
    let t = await r.text();
    document.getElementById("laptop_clipboard").innerText = t;
}
async function copyToClipboard() {
    let t = document.getElementById("laptop_clipboard").innerText;

    if (navigator.share) {
        await navigator.share({
            title: "Clipboard from Laptop",
            text: t
        });
    } else {
        alert("Share API not supported");
    }
}
setInterval(fetchClip, 800);
fetchClip();
</script>

<hr>

<h3>Phone → Laptop (Manual)</h3>
<form method="POST">
<textarea name="clip" rows="5" placeholder="Paste here to send to laptop"></textarea><br>
<button type="submit">Send to Laptop</button>
</form>

</body>
</html>
"""

class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # route: /latest → return last clipboard
        if self.path == "/latest":
            try:
                with open(CLIPFILE, "r") as f:
                    data = f.read()
            except:
                data = ""
            self.send_response(200)
            self.end_headers()
            self.wfile.write(data.encode())
            return

        # Otherwise, serve HTML page
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        post = self.rfile.read(length).decode()
        data = urllib.parse.parse_qs(post).get("clip", [""])[0]

        # Write to laptop clipboard
        subprocess.run(["xclip", "-sel", "clip"], input=data.encode())

        # Response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h3>Sent to laptop clipboard!</h3>")
        self.wfile.write(HTML.encode())


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="/home/kali/cert.pem", keyfile="/home/kali/key.pem")

httpd = socketserver.TCPServer(("", PORT), Handler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"Serving HTTPS on port {PORT}")
httpd.serve_forever()

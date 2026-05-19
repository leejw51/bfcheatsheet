#!/usr/bin/env python3
import argparse
import http.server
import os
import ssl
import subprocess
import sys
from pathlib import Path


def ensure_cert(cert_path: Path, key_path: Path) -> None:
    if cert_path.exists() and key_path.exists():
        return
    print(f"Generating self-signed certificate at {cert_path}", file=sys.stderr)
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-keyout",
            str(key_path),
            "-out",
            str(cert_path),
            "-days",
            "365",
            "-subj",
            "/CN=localhost",
            "-addext",
            "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:0.0.0.0",
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve current folder over HTTPS.")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8443, help="Bind port (default: 8443)"
    )
    parser.add_argument("--cert", default="cert.pem", help="TLS certificate path")
    parser.add_argument("--key", default="key.pem", help="TLS private key path")
    parser.add_argument("--dir", default=os.getcwd(), help="Directory to serve")
    args = parser.parse_args()

    cert = Path(args.cert).resolve()
    key = Path(args.key).resolve()
    ensure_cert(cert, key)

    os.chdir(args.dir)

    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.ThreadingHTTPServer((args.host, args.port), handler)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving {args.dir} on https://{args.host}:{args.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.server_close()


if __name__ == "__main__":
    main()

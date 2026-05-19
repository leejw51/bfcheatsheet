#!/usr/bin/env python3
import argparse
import http.server
import os
import ssl
import subprocess
import sys
import threading
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


def make_server(host: str, port: int, ssl_ctx: ssl.SSLContext | None) -> http.server.ThreadingHTTPServer:
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.ThreadingHTTPServer((host, port), handler)
    if ssl_ctx is not None:
        httpd.socket = ssl_ctx.wrap_socket(httpd.socket, server_side=True)
    return httpd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve current folder over HTTP and HTTPS (both by default)."
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--http-port", type=int, default=8000, help="HTTP port (default: 8000)"
    )
    parser.add_argument(
        "--https-port", type=int, default=8443, help="HTTPS port (default: 8443)"
    )
    parser.add_argument(
        "--http-only", action="store_true", help="Serve plain HTTP only (no TLS)"
    )
    parser.add_argument(
        "--https-only", action="store_true", help="Serve HTTPS only"
    )
    parser.add_argument("--cert", default="cert.pem", help="TLS certificate path")
    parser.add_argument("--key", default="key.pem", help="TLS private key path")
    parser.add_argument("--dir", default=os.getcwd(), help="Directory to serve")
    args = parser.parse_args()

    if args.http_only and args.https_only:
        parser.error("--http-only and --https-only are mutually exclusive")

    serve_http = not args.https_only
    serve_https = not args.http_only

    os.chdir(args.dir)

    servers: list[tuple[str, int, http.server.ThreadingHTTPServer]] = []

    if serve_https:
        cert = Path(args.cert).resolve()
        key = Path(args.key).resolve()
        ensure_cert(cert, key)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
        servers.append(("https", args.https_port, make_server(args.host, args.https_port, ctx)))

    if serve_http:
        servers.append(("http", args.http_port, make_server(args.host, args.http_port, None)))

    print(f"Serving {args.dir} on:")
    for scheme, port, _ in servers:
        print(f"  {scheme}://localhost:{port}")
        print(f"  {scheme}://{args.host}:{port}")

    threads = []
    for scheme, port, httpd in servers:
        t = threading.Thread(target=httpd.serve_forever, name=f"{scheme}:{port}", daemon=True)
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nShutting down.")
        for _, _, httpd in servers:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    main()

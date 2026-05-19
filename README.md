# bfcheatsheet

A small static HTTPS server for serving the cheatsheet HTML files in this directory (PyTorch, LoRA, multi-agent guide, etc.).

## Contents

- `pytorch.html` — PyTorch cheatsheet
- `lora-interactive.html` — Interactive LoRA guide
- `multi-agent-guide.html` — Multi-agent system guide
- `server.py` — Local HTTPS file server

## Requirements

- Python 3.8+
- `openssl` available on PATH (used once to generate a self-signed certificate)

No third-party Python packages are required — `server.py` uses only the standard library. `requirements.txt` is included for tooling compatibility.

```bash
pip install -r requirements.txt
```

## Usage

Serve the current directory over HTTPS on the default port (8443):

```bash
python server.py
```

Then open <https://localhost:8443/> in your browser. Because the certificate is self-signed, you will need to accept the browser security warning the first time.

### Options

| Flag     | Default        | Description                                  |
| -------- | -------------- | -------------------------------------------- |
| `--host` | `0.0.0.0`      | Bind address                                 |
| `--port` | `8443`         | Bind port                                    |
| `--cert` | `cert.pem`     | TLS certificate path (auto-generated)        |
| `--key`  | `key.pem`      | TLS private key path (auto-generated)        |
| `--dir`  | current dir    | Directory to serve                           |

### Examples

Bind only to localhost:

```bash
python server.py --host 127.0.0.1
```

Use a different port and directory:

```bash
python server.py --port 9000 --dir ./public
```

## Certificate

On first run, `server.py` invokes `openssl` to generate a self-signed certificate (`cert.pem`) and private key (`key.pem`) valid for 365 days, with `localhost`, `127.0.0.1`, and `0.0.0.0` as Subject Alternative Names. Subsequent runs reuse the existing files.

**Do not commit `cert.pem` or `key.pem`.** They are listed in `.gitignore`.

## Security notes

- The server has no authentication. Anything inside `--dir` is publicly readable to whoever can reach the port.
- The default bind address `0.0.0.0` exposes the server on every network interface. Use `--host 127.0.0.1` if you only need local access.
- The certificate is self-signed; browsers will warn, and clients should not trust it for anything beyond local development.

## License

See [LICENSE](LICENSE).

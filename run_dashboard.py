"""
Servidor Web del Dashboard: SAP Business One Enterprise RPA Control Tower
Descripción: Sirve la aplicación web interactiva del Dashboard en http://localhost:8050.

Autor: Guillén Concepción - Senior Data Scientist & MLOps Engineer
Contacto: guillenconcepcion@gmail.com | https://github.com/GuillenConcepcion | https://www.linkedin.com/in/guillen-concepcion-25266b127
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8050
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/dashboard.html"
        return super().do_GET()


def main():
    os.chdir(DIRECTORY)
    start_port = 8050
    httpd = None
    selected_port = start_port

    socketserver.TCPServer.allow_reuse_address = True

    for p in range(start_port, start_port + 10):
        try:
            httpd = socketserver.TCPServer(("", p), CustomHandler)
            selected_port = p
            break
        except OSError:
            continue

    if httpd is None:
        print("[ERROR] No se pudo encontrar un puerto libre entre 8050 y 8060.")
        return

    url = f"http://localhost:{selected_port}/dashboard.html"
    print("=" * 75)
    print("=== SAP BUSINESS ONE -- CONTROL TOWER RPA & DASHBOARD FINANCIERO ===")
    print(f" Servidor iniciado exitosamente en: {url}")
    print(" Presione Ctrl+C para detener el servidor web.")
    print("=" * 75)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Servidor del Dashboard detenido.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()

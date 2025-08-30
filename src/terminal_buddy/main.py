import typer
import socket
import threading
from terminal_buddy.utils.llm_functions import get_terminal_command

app = typer.Typer()

HOST = "127.0.0.1"
PORT = 65432

# Global resource holder
resources = {}


def build_resources():
    typer.echo("Building resources once…")
    from terminal_buddy.utils.example_selection import mmr_prompt_template
    resources['mmr_prompt_template'] = mmr_prompt_template
    return resources


def parse_request(request: str):
    # You can use resources here if needed
    return get_terminal_command(user_query=request,mmr_prompt_template=resources['mmr_prompt_template'])


# --- Server / Daemon ---
def handle_client(conn, addr):
    with conn:
        data = conn.recv(4096).decode()
        typer.echo(f"Query from {addr}: {data}")
        response = parse_request(data)
        conn.sendall(response.encode())


def start_server():
    global resources
    resources = build_resources()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        typer.echo(f"Server running on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=handle_client, args=(conn, addr), daemon=True
            ).start()


@app.command()
def serve():
    """Start the background service."""
    start_server()


@app.callback(invoke_without_command=True)
def query(request: str):
    """
    Send a query to the daemon if it's running,
    otherwise fall back to one-off execution.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(request.encode())
            data = s.recv(4096).decode()
            typer.echo(data)
            return
    except ConnectionRefusedError:
        typer.echo("No daemon found. Running in one-off mode…")

    # fallback to single-shot
    command = parse_request(request)
    typer.echo(command)
    return command


# --- Nice shortcut: `tb "<query>"` directly calls query() ---
@app.command()
def __default__(request: str):
    """
    Default command: behaves like `tb query "<text>"`.
    """
    query(request)


def main():
    app()


if __name__ == "__main__":
    main()

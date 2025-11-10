#!/usr/bin/env python3
"""
RCIHM - RoboClaw Client Human-Machine Interface (minimal UI)

Behavior (per request):
- Print only 'C' upon successful connection.
- Print only '>' (no newline) whenever a new distance value is requested.
- Suppress all other console output. Still logs to file for diagnostics.
"""

import argparse
import socket
import sys
import time
import threading
import logging
from logging.handlers import RotatingFileHandler

DEFAULT_PORT = 65432
DEFAULT_HOST = "127.0.0.1"
LOG_FILENAME = "rcihm_client.log"

stop_event = threading.Event()


def setup_logging(logfile: str = LOG_FILENAME) -> logging.Logger:
    """Configure file-only logging to avoid console noise."""
    logger = logging.getLogger("RCIHM")
    logger.setLevel(logging.INFO)

    # Remove existing handlers to prevent duplicates
    for h in list(logger.handlers):
        logger.removeHandler(h)

    # File handler (rotating) only
    fh = RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(fh)

    return logger


def timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def user_input_thread(logger: logging.Logger):
    """Deprecated optional stdin watcher (kept for future use)."""
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    except Exception:
        stop_event.set()


def connect_and_stream(logger: logging.Logger, host: str, port: int, input_enabled: bool = True):
    backoff = 2
    max_backoff = 30

    while not stop_event.is_set():
        try:
            sock = socket.create_connection((host, port), timeout=10)
            # Print 'C' on successful connection (minimal UI)
            print("C", flush=True)
            
            # Remove timeout after connection is established
            sock.settimeout(None)
            
            # Convert to file-like object for convenient line reading
            sock_file = sock.makefile('r', encoding='utf-8', newline='\n', errors='replace')

            # Reset backoff after successful connection
            backoff = 2

            for line in sock_file:
                if stop_event.is_set():
                    break
                # Empty line means server disconnected
                if not line:
                    sock.close()
                    return  # Exit gracefully instead of reconnecting
                    
                msg = line.rstrip('\r\n')
                # Minimal protocol handling
                # Ignore server-sent 'C' since we already printed it on connect
                if msg == 'C':
                    continue
                # Position report from server -> print as-is
                if msg.startswith('P:'):
                    print(msg, flush=True)
                    continue
                # If server prompts with '>' request a distance value
                if msg == '>':
                    try:
                        # Minimal prompt
                        print(">", end="", flush=True)
                        distance = input().strip()
                        
                        # If user typed 'p', request position; otherwise send distance
                        if distance.lower() == 'p':
                            sock.sendall(b"p\n")
                        else:
                            params = f"DISTANCE:{distance}\n"
                            sock.sendall(params.encode('utf-8'))
                    except (EOFError, KeyboardInterrupt):
                        sock.close()
                        return
                    except BrokenPipeError:
                        sock.close()
                        return

            sock.close()

        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            if stop_event.is_set():
                break

        # Reconnect with backoff
        if not stop_event.is_set():
            for _ in range(backoff):
                if stop_event.is_set():
                    break
                time.sleep(1)
            backoff = min(max_backoff, backoff * 2)


def main():
    parser = argparse.ArgumentParser(description="RoboClaw TCP client (RCIHM)")
    parser.add_argument("--host", help=f"Server host/IP (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--no-input", action="store_true", help="Disable stdin watcher thread")
    args = parser.parse_args()

    logger = setup_logging()

    host = args.host or DEFAULT_HOST

    # Disable input watcher thread to avoid conflicts with parameter input
    # User can still use Ctrl+C to exit
    input_thread = None
    input_enabled = not args.no_input
    # Don't start the input thread - it conflicts with parameter input
    # if input_enabled:
    #     input_thread = threading.Thread(target=user_input_thread, args=(logger,), daemon=True)
    #     input_thread.start()

    try:
        connect_and_stream(logger, host, args.port, input_enabled=False)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        if input_thread and input_thread.is_alive():
            try:
                input_thread.join(timeout=1.0)
            except Exception:
                pass
        # No extra console output on exit


if __name__ == "__main__":
    main()

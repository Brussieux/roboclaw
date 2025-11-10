#!/usr/bin/env python3
"""
RCIHM - RoboClaw Client Human-Machine Interface

Simple, dependency-free TCP client to connect to the RoboClaw server
(port 65432 by default), display server messages with timestamps, and
optionally save them to a log file. Reconnects automatically if the
connection drops.

Usage:
    python3 RCIHM.py --host 192.168.1.50 --port 65432

If --host is omitted, you'll be prompted (default 127.0.0.1).
Press Ctrl+C to exit.
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
    logger = logging.getLogger("RCIHM")
    logger.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    # File handler (rotating)
    fh = RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(fh)

    return logger


def timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def user_input_thread(logger: logging.Logger):
    """Optional stdin watcher to allow future commands or quit.
    Currently only supports 'q' or Ctrl+C to exit.
    """
    try:
        while not stop_event.is_set():
            line = sys.stdin.readline()
            if not line:  # EOF
                break
            line = line.strip().lower()
            if line in {"q", "quit", "exit"}:
                logger.info("[user] Quit requested")
                stop_event.set()
                break
            else:
                logger.info(f"[user] Unknown input: {line!r} (type 'q' to quit)")
    except Exception as e:
        logger.info(f"[user] input error: {e}")
        stop_event.set()


def connect_and_stream(logger: logging.Logger, host: str, port: int):
    backoff = 2
    max_backoff = 30

    while not stop_event.is_set():
        try:
            logger.info(f"Connecting to {host}:{port} ... (Ctrl+C to cancel)")
            with socket.create_connection((host, port), timeout=10) as sock:
                logger.info(f"[{timestamp()}] Connected to {host}:{port}")
                # Convert to file-like object for convenient line reading
                sock_file = sock.makefile('r', encoding='utf-8', newline='\n', errors='replace')

                # Reset backoff after successful connection
                backoff = 2

                for line in sock_file:
                    if stop_event.is_set():
                        break
                    msg = line.rstrip('\r\n')
                    logger.info(f"[{timestamp()}] {msg}")

                logger.info(f"[{timestamp()}] Connection closed by server or lost")

        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            if stop_event.is_set():
                break
            logger.info(f"[{timestamp()}] Connection error: {e}")

        # Reconnect with backoff
        if not stop_event.is_set():
            logger.info(f"Reconnecting in {backoff}s ...")
            for _ in range(backoff):
                if stop_event.is_set():
                    break
                time.sleep(1)
            backoff = min(max_backoff, backoff * 2)


def main():
    parser = argparse.ArgumentParser(description="RoboClaw TCP client (RCIHM)")
    parser.add_argument("--host", help="Server host/IP (default: prompt)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--no-input", action="store_true", help="Disable stdin watcher thread")
    args = parser.parse_args()

    logger = setup_logging()

    host = args.host
    if not host:
        try:
            entered = input(f"Enter server host/IP [{DEFAULT_HOST}]: ").strip()
            host = entered or DEFAULT_HOST
        except (EOFError, KeyboardInterrupt):
            print()
            host = DEFAULT_HOST

    logger.info("========================================")
    logger.info("RCIHM - RoboClaw Client HMI")
    logger.info("- Connects to RoboClaw TCP server and displays messages")
    logger.info("- Press 'q' + Enter or Ctrl+C to exit")
    logger.info("========================================")

    # Optional input watcher thread
    input_thread = None
    if not args.no_input:
        input_thread = threading.Thread(target=user_input_thread, args=(logger,), daemon=True)
        input_thread.start()

    try:
        connect_and_stream(logger, host, args.port)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt - exiting ...")
    finally:
        stop_event.set()
        if input_thread and input_thread.is_alive():
            try:
                input_thread.join(timeout=1.0)
            except Exception:
                pass
        logger.info("RCIHM terminated.")


if __name__ == "__main__":
    main()

import socket
import psutil
import sys

def kill_port(port):
    for proc in psutil.process_iter():
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    proc.kill()
                    print(f"Killed process {proc.pid} running on port {port}")
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    print(f"No process found running on port {port}")
    return False

if __name__ == "__main__":
    port = 5000
    kill_port(port) 
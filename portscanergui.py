import socket
import threading
import time
import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
    3306: 'MySQL', 3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-Alt'
}

class PortScanner:
    def __init__(self, target, start_port, end_port, timeout=0.5, max_workers=100):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.max_workers = max_workers

        self._stop_event = threading.Event()
        self.total_ports = max(0, end_port - start_port + 1)
        self.scanned_count = 0
        self.open_ports = []

        self._lock = threading.Lock()
        self.result_queue = queue.Queue()

    def stop(self):
        self._stop_event.set()

    def _scan_port(self, port):
        if self._stop_event.is_set():
            return

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.target, port))

                if result == 0:
                    service = COMMON_PORTS.get(port, 'Unknown')
                    with self._lock:
                        self.open_ports.append((port, service))
                    self.result_queue.put(('open', port, service))

        except Exception as e:
            self.result_queue.put(('error', port, str(e)))

        finally:
            with self._lock:
                self.scanned_count += 1
            self.result_queue.put(('progress', self.scanned_count, self.total_ports))

    def resolve_target(self):
        return socket.gethostbyname(self.target)

    def run(self):
        sem = threading.Semaphore(self.max_workers)
        threads = []

        for port in range(self.start_port, self.end_port + 1):
            if self._stop_event.is_set():
                break

            sem.acquire()
            t = threading.Thread(target=self._worker_wrapper, args=(sem, port), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.result_queue.put(('done', None, None))

    def _worker_wrapper(self, sem, port):
        try:
            self._scan_port(port)
        finally:
            sem.release()


class ScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Port Scanner")
        self.geometry("720x520")

        self.scanner = None
        self.scanner_thread = None
        self.start_time = None

        self._build_ui()

    def _build_ui(self):
        frm = ttk.LabelFrame(self, text="Scan Settings")
        frm.pack(fill="x", padx=10, pady=10)

        ttk.Label(frm, text="Target:").grid(row=0, column=0)
        self.ent_target = ttk.Entry(frm, width=30)
        self.ent_target.grid(row=0, column=1)

        ttk.Label(frm, text="Start Port:").grid(row=0, column=2)
        self.ent_start = ttk.Entry(frm, width=8)
        self.ent_start.insert(0, "1")
        self.ent_start.grid(row=0, column=3)

        ttk.Label(frm, text="End Port:").grid(row=0, column=4)
        self.ent_end = ttk.Entry(frm, width=8)
        self.ent_end.insert(0, "1024")
        self.ent_end.grid(row=0, column=5)

        self.btn_start = ttk.Button(frm, text="Start", command=self.start_scan)
        self.btn_start.grid(row=1, column=4)

        self.btn_stop = ttk.Button(frm, text="Stop", command=self.stop_scan, state="disabled")
        self.btn_stop.grid(row=1, column=5)

        self.progress = ttk.Progressbar(self)
        self.progress.pack(fill="x", padx=10)

        self.status = tk.StringVar(value="Idle")
        ttk.Label(self, textvariable=self.status).pack()

        self.txt = tk.Text(self)
        self.txt.pack(fill="both", expand=True, padx=10, pady=10)

    def start_scan(self):
        target = self.ent_target.get().strip()

        try:
            start = int(self.ent_start.get())
            end = int(self.ent_end.get())
        except:
            messagebox.showerror("Error", "Invalid ports")
            return

        if not (1 <= start <= 65535 and 1 <= end <= 65535 and start <= end):
            messagebox.showerror("Error", "Port range 1–65535")
            return

        self.scanner = PortScanner(target, start, end)

        try:
            ip = self.scanner.resolve_target()
            self.txt.insert(tk.END, f"Target: {target} ({ip})\n\n")
        except:
            messagebox.showerror("Error", "Invalid target")
            return

        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")

        self.start_time = time.time()

        self.scanner_thread = threading.Thread(target=self.scanner.run, daemon=True)
        self.scanner_thread.start()

        self.after(50, self.poll)

    def stop_scan(self):
        if self.scanner:
            self.scanner.stop()
            self.status.set("Stopping...")

    def poll(self):
        try:
            while True:
                msg, a, b = self.scanner.result_queue.get_nowait()

                if msg == 'open':
                    self.txt.insert(tk.END, f"[+] Port {a} ({b}) open\n")

                elif msg == 'progress':
                    self.progress.config(maximum=b, value=a)
                    self.status.set(f"Scanning {a}/{b}")

                elif msg == 'error':
                    pass  # ignore spam

                elif msg == 'done':
                    self.status.set("Completed")
                    self.btn_start.config(state="normal")
                    self.btn_stop.config(state="disabled")

        except queue.Empty:
            pass

        if self.scanner_thread.is_alive():
            self.after(50, self.poll)


def main():
    app = ScannerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

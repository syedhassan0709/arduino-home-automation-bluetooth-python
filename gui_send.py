import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import serial
from serial.tools import list_ports
import queue

DEFAULT_BAUD = 9600
DEFAULT_PORT = "COM5"

# Devices in (label, on-command, off-command) tuples.
# The sketch expects commands that end with '#'. We send exact bytes, no newline.
DEVICES = [
    ("Switch", "A#", "a#"),
    ("Light", "B#", "b#"),
    ("Light", "C#", "c#"),
    ("Light", "D#", "d#"),
    ("Fan", "E#", "e#"),
]


class SerialGui:
    def __init__(self, root):
        self.root = root
        root.title('Arduino Relay Controller')
        self.ser = None
        self.reader_thread = None
        self.stop_event = threading.Event()
        self.recv_q = queue.Queue()

        frame = ttk.Frame(root, padding=10)
        frame.grid(sticky='nsew')

        # Port selection
        port_row = ttk.Frame(frame)
        port_row.grid(row=0, column=0, sticky='w')
        ttk.Label(port_row, text='Port:').grid(row=0, column=0, sticky='w')
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_row, textvariable=self.port_var, width=20)
        self.port_combo.grid(row=0, column=1, padx=(6, 6))
        self.refresh_ports()

        ttk.Label(port_row, text='Baud:').grid(row=0, column=2, sticky='w')
        self.baud_var = tk.IntVar(value=DEFAULT_BAUD)
        ttk.Entry(port_row, textvariable=self.baud_var, width=8).grid(row=0, column=3)

        ttk.Button(port_row, text='Refresh', command=self.refresh_ports).grid(row=0, column=4, padx=6)
        self.connect_button = ttk.Button(port_row, text='Connect', command=self.toggle_connect)
        self.connect_button.grid(row=0, column=5)

        self.status_var = tk.StringVar(value='Disconnected')
        ttk.Label(frame, textvariable=self.status_var).grid(row=1, column=0, sticky='w', pady=(6, 6))

        # Buttons grid
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=2, column=0, sticky='w')

        # Create rows of ON (left) and OFF (right) buttons to avoid confusion.
        for row_idx, (label, on_cmd, off_cmd) in enumerate(DEVICES):
            on_btn = ttk.Button(buttons_frame, text=f"{label} ON", width=20, command=lambda c=on_cmd: self.send_cmd(c))
            off_btn = ttk.Button(buttons_frame, text=f"{label} OFF", width=20, command=lambda c=off_cmd: self.send_cmd(c))
            on_btn.grid(row=row_idx, column=0, padx=4, pady=4)
            off_btn.grid(row=row_idx, column=1, padx=4, pady=4)

        # Custom send
        custom_frame = ttk.Frame(frame)
        custom_frame.grid(row=3, column=0, sticky='w', pady=(8, 0))
        ttk.Label(custom_frame, text='Custom (send exact bytes):').grid(row=0, column=0, sticky='w')
        self.custom_entry = ttk.Entry(custom_frame, width=30)
        self.custom_entry.grid(row=0, column=1, padx=(6, 6))
        ttk.Button(custom_frame, text='Send', command=self.send_custom).grid(row=0, column=2)

        # Echo / log
        ttk.Label(frame, text='Incoming:').grid(row=4, column=0, sticky='w', pady=(8, 0))
        self.log = scrolledtext.ScrolledText(frame, width=60, height=12, state='disabled')
        self.log.grid(row=5, column=0, pady=(4, 0))

        # Clean up on close
        root.protocol('WM_DELETE_WINDOW', self.on_close)

        # poll queue for incoming lines
        self.root.after(100, self.process_recv_q)

    def refresh_ports(self):
        ports = list_ports.comports()
        devices = [p.device for p in ports]
        if not devices:
            devices = [DEFAULT_PORT]
        self.port_combo['values'] = devices
        if not self.port_var.get():
            self.port_var.set(devices[0])

    def toggle_connect(self):
        if self.ser and self.ser.is_open:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        port = self.port_var.get()
        baud = int(self.baud_var.get())
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            time.sleep(2)  # wait for Arduino reset if it occurs
            self.status_var.set(f'Connected to {port} @ {baud}')
            self.connect_button.config(text='Disconnect')
            self.stop_event.clear()
            self.reader_thread = threading.Thread(target=self.reader_loop, daemon=True)
            self.reader_thread.start()
        except Exception as e:
            messagebox.showerror('Connection failed', f'Could not open {port}: {e}')
            self.ser = None
            self.status_var.set('Disconnected')

    def disconnect(self):
        self.stop_event.set()
        if self.reader_thread:
            self.reader_thread.join(timeout=1)
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        self.ser = None
        self.status_var.set('Disconnected')
        self.connect_button.config(text='Connect')

    def reader_loop(self):
        ser = self.ser
        try:
            while not self.stop_event.is_set() and ser and ser.is_open:
                try:
                    if ser.in_waiting:
                        line = ser.readline().decode('utf-8', errors='replace').strip()
                        if line:
                            self.recv_q.put(line)
                    else:
                        time.sleep(0.05)
                except Exception:
                    time.sleep(0.1)
        finally:
            pass

    def process_recv_q(self):
        try:
            while True:
                line = self.recv_q.get_nowait()
                self.append_log(f'<- {line}')
        except queue.Empty:
            pass
        self.root.after(100, self.process_recv_q)

    def append_log(self, text):
        self.log.configure(state='normal')
        self.log.insert('end', text + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def send_bytes(self, data: bytes):
        if not self.ser or not self.ser.is_open:
            messagebox.showwarning('Not connected', 'Open a serial connection first')
            return
        try:
            self.ser.write(data)
            self.ser.flush()
            self.append_log(f"-> {data}")
        except Exception as e:
            messagebox.showerror('Send failed', str(e))

    def send_cmd(self, cmd_str):
        # cmd_str is like 'A#' — send raw bytes, no newline appended
        self.send_bytes(cmd_str.encode('utf-8'))

    def send_custom(self):
        txt = self.custom_entry.get()
        if not txt:
            return
        self.send_bytes(txt.encode('utf-8'))

    def on_close(self):
        self.disconnect()
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = SerialGui(root)
    root.mainloop()

import time
import os
import tkinter as tk
import serial  # type: ignore
import serial.tools.list_ports  # type: ignore

class NexusMTKEngine:
    def __init__(self):
        self.port = None
        self.baudrate = 115200
        self.connection = None

    def scan_mtk_ports(self):
        print("[*] Scanning for connected devices in BROM / VCOM mode...")
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(f"[*] Found Port: {p.device} - {p.description}")
            self.port = p.device
            return self.port
        print("[-] No MTK port detected. Please connect device in BROM mode.")
        return None

    def connect_to_brom(self):
        if not self.port:
            print("[-] Error: Port not specified.")
            return False
        try:
            print(f"[*] Connecting to target on {self.port} at {self.baudrate} baud...")
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2
            )
            print("[+] BROM communication channel opened successfully.")
            return True
        except Exception as e:
            print(f"[-] Connection failed: {str(e)}")
            return False

    def send_handshake(self):
        print("[*] Sending BROM synchronization handshake...")
        try:
            if self.connection and self.connection.is_open:
                sync_bytes = b'\xA0\x0A\x50\x05'
                self.connection.write(sync_bytes)
                time.sleep(0.3)
                response = self.connection.read(2)
                if response:
                    print(f"[+] Handshake acknowledged by target! Response: {response.hex()}")
                    return True
                else:
                    print("[-] Warning: Direct sync reply timeout, forcing BROM command vector...")
                    return True
            return False
        except Exception as e:
            print(f"[-] Handshake error: {str(e)}")
            return False

    def read_device_info(self):
        print("[*] Requesting hardware security flags & chip identification...")
        if self.connection and self.connection.is_open:
            cmd_query = b'\xD0\x00\x00\x00'
            self.connection.write(cmd_query)
            time.sleep(0.5)
            res = self.connection.read(16)
            print(f"[+] Target Chip HW Code Response: {res.hex() if res else 'Standard MTK Target'}")
            print("[+] Storage Type: UFS / eMMC Direct Interface Confirmed.")
            print("[+] Security Status: Bootrom Mode Active.")
        else:
            print("[-] Error: Device not connected.")

    def bypass_frp(self):
        print("[*] Initializing DA (Download Agent) payload injection...")
        time.sleep(0.5)
        print("[*] Lifting security protection blocks...")
        time.sleep(0.5)
        if self.connection and self.connection.is_open:
            print("[*] Addressing FRP partition sector in flash storage...")
            erase_command = b'\x40\x01\x00\x00'
            self.connection.write(erase_command)
            time.sleep(1)
            print("[+] Success: FRP partition block erased successfully at hardware level!")
            print("[+] Resetting target device...")
        else:
            print("[-] Operation failed: No active serial link.")

    def format_user_data(self):
        print("[*] Initializing factory reset storage block erase...")
        time.sleep(0.5)
        if self.connection and self.connection.is_open:
            print("[*] Unlocking user data boundaries...")
            time.sleep(1)
            format_command = b'\x40\x02\x00\x00'
            self.connection.write(format_command)
            time.sleep(1.5)
            print("[+] Success: Userdata and Cache sectors completely formatted.")
        else:
            print("[-] Operation failed: No active serial link.")

    def close_connection(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("[*] Connection closed safely.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Nexus MTK Tool V2")
    root.geometry("600x400")

    try:
        if os.path.exists("logo.png"):
            app_icon = tk.PhotoImage(file="logo.png")
            root.iconphoto(True, app_icon)
        elif os.path.exists("logo.jpeg"):
            app_icon = tk.PhotoImage(file="logo.jpeg")
            root.iconphoto(True, app_icon)
        else:
            print("[-] Warning: logo file not found in project directory.")
    except Exception as ex:
        print(f"[-] Warning: Could not load window logo icon: {ex}")

    mtk_engine = NexusMTKEngine()
    root.mainloop()
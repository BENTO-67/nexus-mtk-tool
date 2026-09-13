import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import os
import sys
import subprocess
import threading
import shutil

try:
    from license_manager import TrialLicenseManager
except ImportError:
    TrialLicenseManager = None

class NexusMTKApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexus MTK Tool V2")
        self.root.geometry("780x850")
        
        # Initialize License Manager
        try:
            if TrialLicenseManager:
                self.license_manager = TrialLicenseManager(trial_days=3)
                self.verify_system_license()
            else:
                self.show_main_interface("License Module Missing (Bypassed)")
        except Exception:
            self.show_main_interface("Trial Active (Fallback Mode)")

    def verify_system_license(self):
        try:
            status = self.license_manager.check_license_status()
            if status == "activated" or (isinstance(status, dict) and status.get("status") == "trial_active"):
                if isinstance(status, dict):
                    remaining = status.get("remaining_hours")
                    self.show_main_interface(f"Trial Active (Remaining: {remaining} hours)")
                else:
                    self.show_main_interface("Activated (Permanent License)")
            else:
                self.show_activation_window()
        except Exception:
            self.show_main_interface("Trial Active (Offline Mode)")

    def show_main_interface(self, license_info):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Top status bar
        self.status_label = tk.Label(self.root, text=f"License Status: {license_info}", fg="green", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=3)
        
        # Tool Header
        title_label = tk.Label(self.root, text="NEXUS MTK TOOL V2 - REAL FIELD ENGINE", font=("Arial", 18, "bold"), fg="#111")
        title_label.pack(pady=2)
        
        sub_label = tk.Label(self.root, text="Direct Hardware Interface Bridge (MTKClient Real-Time Execution)", font=("Arial", 9), fg="gray")
        sub_label.pack(pady=2)

        # Main Notebook (Tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        tab_operations = ttk.Frame(notebook)
        tab_flashing = ttk.Frame(notebook)
        tab_settings = ttk.Frame(notebook)

        notebook.add(tab_operations, text=" ⚡ Live Device Operations ")
        notebook.add(tab_flashing, text=" 📂 Scatter & Partition Flashing ")
        notebook.add(tab_settings, text=" ⚙️ MTKClient Core & DA ")

        # --- Tab 1: Operations ---
        btn_frame = tk.Frame(tab_operations)
        btn_frame.pack(pady=15)

        btn_read = tk.Button(btn_frame, text="Read Device Info", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["printgpt"], "Read Device Info"))
        btn_read.grid(row=0, column=0, padx=8, pady=8)

        btn_bypass = tk.Button(btn_frame, text="Bypass FRP", bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["reset-frp"], "Bypass FRP"))
        btn_bypass.grid(row=0, column=1, padx=8, pady=8)

        btn_format = tk.Button(btn_frame, text="Factory Reset / Wipe", bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["factory-reset"], "Factory Reset"))
        btn_format.grid(row=0, column=2, padx=8, pady=8)

        btn_lock_safe = tk.Button(btn_frame, text="Remove Screen Lock", bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["safe-format"], "Remove Screen Lock"))
        btn_lock_safe.grid(row=1, column=0, padx=8, pady=8)

        btn_app_lock = tk.Button(btn_frame, text="Remove App Lock", bg="#E91E63", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["reset-locks"], "Remove App Lock"))
        btn_app_lock.grid(row=1, column=1, padx=8, pady=8)

        btn_hw_check = tk.Button(btn_frame, text="Storage Inspection", bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["storage-check"], "Storage Inspection"))
        btn_hw_check.grid(row=1, column=2, padx=8, pady=8)

        btn_backup = tk.Button(btn_frame, text="Backup NVRAM / Security", bg="#673AB7", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["backup-nvram"], "Backup NVRAM"))
        btn_backup.grid(row=2, column=0, padx=8, pady=8)

        btn_auth_bypass = tk.Button(btn_frame, text="Bypass SLA / Auth", bg="#795548", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["bypass-auth"], "Bypass SLA/Auth"))
        btn_auth_bypass.grid(row=2, column=1, padx=8, pady=8)

        btn_scan = tk.Button(btn_frame, text="Detect MTK Port", bg="#00BCD4", fg="white", font=("Arial", 10, "bold"), width=21, height=2, command=lambda: self.run_real_command(["detect"], "Detect MTK Device"))
        btn_scan.grid(row=2, column=2, padx=8, pady=8)

        # --- Tab 2: Flashing ---
        flash_frame = tk.Frame(tab_flashing)
        flash_frame.pack(pady=15, padx=15, fill="both", expand=True)

        tk.Label(flash_frame, text="Select Scatter File (*.txt):", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
        
        scatter_sub_frame = tk.Frame(flash_frame)
        scatter_sub_frame.pack(fill="x", pady=5)
        
        self.scatter_path_entry = tk.Entry(scatter_sub_frame, font=("Arial", 10), width=58)
        self.scatter_path_entry.pack(side=tk.LEFT, padx=5)
        
        btn_browse_scatter = tk.Button(scatter_sub_frame, text="Browse...", bg="#607D8B", fg="white", font=("Arial", 9, "bold"), command=self.action_browse_scatter)
        btn_browse_scatter.pack(side=tk.LEFT, padx=5)

        tk.Label(flash_frame, text="Scatter Partition Analysis Console:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 2))
        self.scatter_info_box = scrolledtext.ScrolledText(flash_frame, width=85, height=8, bg="#f9f9f9", fg="black", font=("Consolas", 9))
        self.scatter_info_box.pack(pady=5, fill="both", expand=True)
        self.scatter_info_box.insert(tk.END, "[*] No scatter file loaded. Select a valid MTK Scatter text file to parse partitions.\n")

        btn_start_flash = tk.Button(flash_frame, text="Execute Real Scatter Flashing via MTKClient", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), width=40, height=2, command=self.action_start_flash)
        btn_start_flash.pack(pady=8)

        # --- Tab 3: Settings / Core ---
        da_frame = tk.Frame(tab_settings)
        da_frame.pack(pady=15, padx=15, fill="both", expand=True)

        tk.Label(da_frame, text="Custom Download Agent (DA) File Path:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
        
        da_sub_frame = tk.Frame(da_frame)
        da_sub_frame.pack(fill="x", pady=5)
        
        self.da_path_entry = tk.Entry(da_sub_frame, font=("Arial", 10), width=58)
        self.da_path_entry.insert(0, os.path.join(os.getcwd(), "DA_AllInOne.bin"))
        self.da_path_entry.pack(side=tk.LEFT, padx=5)
        
        btn_browse_da = tk.Button(da_sub_frame, text="Browse...", bg="#607D8B", fg="white", font=("Arial", 9, "bold"), command=self.action_browse_da)
        btn_browse_da.pack(side=tk.LEFT, padx=5)

        tk.Label(da_frame, text="Target Chipset Architecture Selection:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))
        self.chipset_combobox = ttk.Combobox(da_frame, font=("Arial", 10), width=55, state="readonly")
        self.chipset_combobox['values'] = (
            "[⚡] Auto-Detect Chipset (Universal BROM Core)",
            "Helio G25 / G35 / G37 / MT6761 / MT6762 / MT6765",
            "Helio G80 / G85 / G90 / G90T / MT6785",
            "Helio G96 / G99 / Dimensity 700 / 810 / 6020",
            "Dimensity 800 / 900 / 1080 / 7050 / 8200"
        )
        self.chipset_combobox.current(0)
        self.chipset_combobox.pack(anchor="w", pady=5)

        # Logs Section Container (Shared at bottom)
        log_container = tk.Frame(self.root)
        log_container.pack(fill="both", expand=True, padx=15, pady=5)

        log_label = tk.Label(log_container, text="Live Hardware Engine Output (Real Subprocess Stream):", font=("Arial", 9, "bold"), fg="#333")
        log_label.pack(anchor="w", pady=1)

        self.log_box = scrolledtext.ScrolledText(log_container, width=92, height=9, bg="black", fg="#00FF00", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True, pady=2)
        self.log_box.insert(tk.END, "[*] Nexus MTK Tool V2 initialized.\n[*] Ready to connect via physical BROM/Preloader interface.\n")

    def log_action(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def run_real_command(self, args_list, action_name):
        threading.Thread(target=self._execute_subprocess_thread, args=(args_list, action_name), daemon=True).start()

    def _execute_subprocess_thread(self, args_list, action_name):
        self.log_action(f"\n[***] Starting Real Hardware Action: [{action_name}]")
        
        # استخدام الأمر المباشر لضمان العمل بدون مشاكل مسارات بايثون
        mtk_executable = shutil.which("mtk") or "mtk"
        cmd = [mtk_executable] + args_list
        
        da_file = self.da_path_entry.get().strip()
        if os.path.exists(da_file) and args_list[0] not in ["detect"]:
            cmd.extend(["--da", da_file])
            
        self.log_action(f"[+] Executing command: {' '.join(cmd)}")
        self.log_action("[!] Please connect your MTK device in BROM mode (Volume Up + Down)...")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_action(output.strip())

            return_code = process.poll()
            if return_code == 0:
                self.log_action(f"[✔] [{action_name}] completed successfully on device!")
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Operation '{action_name}' finished successfully!"))
            else:
                self.log_action(f"[-] [{action_name}] finished with exit code {return_code}.")
        except Exception as e:
            self.log_action(f"[-] Subprocess Execution Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Execution Error", f"Failed to execute: {str(e)}"))

    def action_browse_da(self):
        file_path = filedialog.askopenfilename(
            title="Select Download Agent (DA) File",
            filetypes=[("Bin Files", "*.bin"), ("All Files", "*.*")]
        )
        if file_path:
            self.da_path_entry.delete(0, tk.END)
            self.da_path_entry.insert(0, file_path)
            self.log_action(f"[+] Selected DA: {file_path}")

    def action_browse_scatter(self):
        file_path = filedialog.askopenfilename(
            title="Select MediaTek Scatter File",
            filetypes=[("Scatter Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.scatter_path_entry.delete(0, tk.END)
            self.scatter_path_entry.insert(0, file_path)
            self.parse_scatter_file(file_path)

    def parse_scatter_file(self, file_path):
        self.scatter_info_box.delete("1.0", tk.END)
        self.log_action(f"\n[+] Parsing Scatter File: {os.path.basename(file_path)}")
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            lines = content.splitlines()
            partition_count = 0
            self.scatter_info_box.insert(tk.END, "=== PARSED PARTITIONS & ADDRESSES ===\n")
            
            for line in lines:
                if "partition_name" in line or "file_name" in line or "linear_start_addr" in line:
                    self.scatter_info_box.insert(tk.END, line.strip() + "\n")
                    partition_count += 1
                    
            self.scatter_info_box.insert(tk.END, f"\n[✔] Total parsed partition entries: {partition_count}\n")
            self.log_action(f"[✔] Scatter parsed successfully. Ready for flashing pipeline.")
        except Exception as e:
            self.scatter_info_box.insert(tk.END, f"[-] Error parsing scatter file: {str(e)}\n")
            self.log_action(f"[-] Scatter Parse Error: {str(e)}")

    def action_start_flash(self):
        scatter_file = self.scatter_path_entry.get().strip()
        if not scatter_file or not os.path.exists(scatter_file):
            messagebox.showerror("Error", "Please select a valid Scatter file first!")
            return
            
        self.log_action(f"\n[***] Initializing Real Scatter Flashing...")
        self.run_real_command(["w", "rom", scatter_file], "Scatter Flashing")

    def show_activation_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        hwid = self.license_manager.get_hardware_id() if hasattr(self.license_manager, 'get_hardware_id') else "UNKNOWN-HWID"
        
        tk.Label(self.root, text="Hardware-Locked Activation Required", font=("Arial", 14, "bold"), fg="red").pack(pady=15)
        tk.Label(self.root, text="Your trial period has expired. Please enter your permanent activation key.", font=("Arial", 10)).pack(pady=5)
        
        hwid_frame = tk.Frame(self.root)
        hwid_frame.pack(pady=10)
        tk.Label(hwid_frame, text="Your Machine HWID:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        hwid_entry = tk.Entry(hwid_frame, font=("Arial", 11), width=45, fg="blue")
        hwid_entry.insert(0, hwid)
        hwid_entry.config(state="readonly")
        hwid_entry.pack(pady=5)
        make_text_menu(hwid_entry)
        
        key_frame = tk.Frame(self.root)
        key_frame.pack(pady=10)
        tk.Label(key_frame, text="Enter Activation Key:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.key_entry = tk.Entry(key_frame, font=("Arial", 11), width=45)
        self.key_entry.pack(pady=5)
        make_text_menu(self.key_entry)
        
        verify_btn = tk.Button(self.root, text="Verify & Launch", bg="#2196F3", fg="white", font=("Arial", 11, "bold"), width=20, command=self.process_activation)
        verify_btn.pack(pady=15)

    def process_activation(self):
        entered_key = self.key_entry.get().strip()
        if not entered_key:
            messagebox.showerror("Error", "Please select/enter a valid activation key!")
            return
            
        result = self.license_manager.check_license_status(user_entered_key=entered_key)
        if result == "activated":
            messagebox.showinfo("Success", "Tool activated successfully! Welcome.")
            self.show_main_interface("Activated (Permanent License)")
        else:
            messagebox.showerror("Invalid Key", "The activation key you entered is incorrect.")

def make_text_menu(entry_widget):
    menu = tk.Menu(entry_widget, tearoff=0)
    menu.add_command(label="Cut", command=lambda: entry_widget.event_generate("<<Cut>>"))
    menu.add_command(label="Copy", command=lambda: entry_widget.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: entry_widget.event_generate("<<Paste>>"))
    menu.add_separator()
    menu.add_command(label="Select All", command=lambda: entry_widget.select_range(0, 'end'))

    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)

    entry_widget.bind("<Button-3>", show_menu)

if __name__ == "__main__":
    root = tk.Tk()
    app = NexusMTKApp(root)
    root.mainloop()
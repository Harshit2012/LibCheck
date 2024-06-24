import os
import sys
import ast
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext

def get_imports(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module.split('.')[0])
    return imports

def check_installed(package_name):
    try:
        subprocess.check_output([sys.executable, '-m', 'pip', 'show', package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def get_os():
    if sys.platform.startswith("linux"):
        if os.path.isfile("/etc/lsb-release") or os.path.isfile("/etc/debian_version"):
            return "ubuntu"
        return "linux"
    elif sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
        return "windows"
    else:
        return "other"

def suggest_install_commands(missing_packages, os_type):
    commands = []
    for package in missing_packages:
        if os_type == "windows":
            commands.append(f"pip install {package}")
        else:
            commands.append(f"pip3 install {package}")
    return commands

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(0, file_path)

def check_libraries():
    file_path = entry_file_path.get()
    
    if not os.path.isfile(file_path):
        messagebox.showerror("Error", "File does not exist.")
        return

    imports = get_imports(file_path)
    missing_packages = [pkg for pkg in imports if not check_installed(pkg)]

    terminal_output.configure(state='normal')
    terminal_output.delete('1.0', tk.END)
    
    if not missing_packages:
        terminal_output.insert(tk.END, "All required libraries are installed.\n", 'success')
    else:
        terminal_output.insert(tk.END, "The following libraries are missing:\n", 'error')
        for pkg in missing_packages:
            terminal_output.insert(tk.END, f"- {pkg}\n", 'error')
        os_type = get_os()
        if os_type == "other":
            terminal_output.insert(tk.END, "Unsupported operating system.\n", 'error')
        else:
            commands = suggest_install_commands(missing_packages, os_type)
            terminal_output.insert(tk.END, f"To install them, you can run the following command(s):\n", 'info')
            for cmd in commands:
                terminal_output.insert(tk.END, f"{cmd}\n", 'command')
    
    terminal_output.configure(state='disabled')

root = tk.Tk()
root.title("LibCheck")

heading = tk.Label(root, text="LibCheck", font=("Arial", 18))
heading.pack(pady=10)

subheading = tk.Label(root, text="Check for missing libraries and get installation commands", font=("Arial", 12))
subheading.pack(pady=5)

file_path_frame = tk.Frame(root)
file_path_frame.pack(pady=10)
entry_file_path = tk.Entry(file_path_frame, width=50)
entry_file_path.pack(side=tk.LEFT, padx=5)
browse_button = tk.Button(file_path_frame, text="Browse", command=browse_file)
browse_button.pack(side=tk.LEFT)

check_button = tk.Button(root, text="Check Libraries", command=check_libraries)
check_button.pack(pady=10)

terminal_output = scrolledtext.ScrolledText(root, width=80, height=20, bg='black', fg='white', font=('Courier', 10))
terminal_output.pack(pady=10)
terminal_output.tag_configure('success', foreground='green')
terminal_output.tag_configure('error', foreground='red')
terminal_output.tag_configure('info', foreground='yellow')
terminal_output.tag_configure('command', foreground='cyan')
terminal_output.configure(state='disabled')

root.mainloop()
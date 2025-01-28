import psutil
import tkinter as tk
import ctypes
import winreg


# Define the RECT structure
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def get_network_data():
    """Get the current total data received in bytes."""
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv


def format_speed(speed):
    """Convert speed into human-readable format."""
    if speed < 1024 ** 2:
        return f"{speed / 1024 :.1f} KBps"
    else:
        return f"{speed / 1024 ** 2:.1f} MBps"


def format_data(data):
    """Convert data into human-readable format."""
    if data < 1024 ** 2:
        return f"{data / 1024:.1f} KB"
    elif data < 1024 ** 3:
        return f"{data / 1024 ** 2:.1f} MB"
    else:
        return f"{data / 1024 ** 3:.1f} GB"


def is_fullscreen():
    """Check if any window is in fullscreen mode."""
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    hwnd = user32.GetForegroundWindow()
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.pointer(rect))

    window_width = rect.right - rect.left
    window_height = rect.bottom - rect.top

    return window_width == screen_width and window_height == screen_height


def get_system_color_mode():
    """Check the current Windows color mode (dark or light)."""
    try:
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return "light" if value == 1 else "dark"
    except FileNotFoundError:
        return "light"


class NetworkSpeedDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.last_bytes_received = get_network_data()
        self.total_data_used = 0  # Initialize total data used
        self.update_interval = 500  # Update every second
        # Determine initial color mode
        self.color_mode = get_system_color_mode()
        self.bg_color, self.text_color = self.get_color_scheme()

        # Configure the window
        self.root.title("Network Speed")
        self.root.configure(background=self.bg_color)
        self.root.attributes("-transparentcolor", self.bg_color)
        self.root.configure(bg=self.bg_color)

        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", self.bg_color)
        self.root.overrideredirect(True)

        # Create labels to display speed and total data
        self.speed_label = tk.Label(
            self.root,
            text="Speed: Loading...",
            font=("Arial Rounded MT Bold", 11),
            fg=self.text_color,
            bg=self.bg_color,
        )
        self.speed_label.place(x=50, y=43)  # Set position for speed label

        self.data_label = tk.Label(
            self.root,
            text="Data: Loading...",
            font=("Arial Rounded MT Bold", 11),
            fg=self.text_color,
            bg=self.bg_color,
        )
        self.data_label.place(x=130, y=43)  # Set position for data label

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"+{screen_width - 600}+{screen_height - 70}")  # Adjust window position

        self.update_speed()
        self.enforce_topmost()

    def get_color_scheme(self):
        """Get the background and text colors based on the system color mode."""
        if self.color_mode == "light":
            return "white", "black"
        else:
            return "black", "white"

    def update_color_scheme(self):
        """Update the colors dynamically if the system color mode changes."""
        current_color_mode = get_system_color_mode()
        if current_color_mode != self.color_mode:
            self.color_mode = current_color_mode
            self.bg_color, self.text_color = self.get_color_scheme()
            self.root.configure(bg=self.bg_color)
            self.root.attributes("-transparentcolor", self.bg_color)
            self.speed_label.configure(bg=self.bg_color, fg=self.text_color)
            self.data_label.configure(bg=self.bg_color, fg=self.text_color)

    def enforce_topmost(self):
        """Ensure the window stays on top."""
        if not is_fullscreen():
            self.root.deiconify()
            self.root.wm_attributes("-topmost", True)
        self.root.after(1, self.enforce_topmost)

    def update_speed(self):
        """Update the displayed network speed and total data."""
        self.update_color_scheme()

        if is_fullscreen():
            self.root.withdraw()  # Hide the window
        else:
            self.root.deiconify()  # Show the window

            current_bytes_received = get_network_data()
            speed = current_bytes_received - self.last_bytes_received
            self.last_bytes_received = current_bytes_received

            # Update total data usage
            self.total_data_used += speed

            # Format and update the text
            formatted_speed = format_speed(speed)
            formatted_data = format_data(self.total_data_used)
            self.speed_label.config(text=f"{formatted_speed}")
            self.data_label.config(text=f"{formatted_data}")

        self.root.after(self.update_interval, self.update_speed)
        
    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.running = False


if __name__ == "__main__":
    app = NetworkSpeedDisplay()
    app.run()

import customtkinter as ctk
from PIL import Image, ImageOps
from utils import resource_path
import math

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        WIDTH = 500
        HEIGHT = 350
        self.logo_base_size = (300, 75)
        self.pulse_amount = 1.05 # 5% larger at peak

        self.overrideredirect(True)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.configure(fg_color="#1c1c1c")
        
        # --- Center based on screen dimensions ---
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (WIDTH // 2)
        y = (screen_height // 2) - (HEIGHT // 2)
        self.geometry(f"+{x}+{y}")

        # Start transparent
        self.attributes("-alpha", 0.0)
        self.lift()
        self.attributes("-topmost", True)

        # --- Widgets ---
        logo_path = resource_path("assets/DevDuo.png")
        self.original_logo = Image.open(logo_path).convert("RGBA")
        
        self.logo_image = ctk.CTkImage(light_image=self.original_logo, size=self.logo_base_size)
        
        self.logo_label = ctk.CTkLabel(self, text="", image=self.logo_image, bg_color="transparent")
        self.logo_label.pack(pady=(90, 10))

        self.title_label = ctk.CTkLabel(self, text="Invoice Genius", font=("Helvetica", 28, "bold"), text_color="#1c1c1c")
        self.title_label.pack(pady=5)

        self.subtitle_label = ctk.CTkLabel(self, text="Developed by DevDuo Innovation", font=("Helvetica", 12), text_color="#1c1c1c")
        self.subtitle_label.pack(pady=(0, 5))

        self.version_label = ctk.CTkLabel(self, text="v1.0.0", font=("Helvetica", 9, "italic"), text_color="#1c1c1c")
        self.version_label.pack(pady=(0, 40))

        # --- Animation ---
        self.pulse_state = 0.0
        self.is_pulsing = False
        self.update()
        self._fade_in_window()

    def _fade_in_window(self, alpha=0.0):
        if alpha < 1.0:
            alpha = min(alpha + 0.06, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, lambda: self._fade_in_window(alpha))
        else:
            self._fade_in_text()

    def _fade_in_text(self, alpha=0.0):
        if alpha < 1.0:
            alpha = min(alpha + 0.08, 1.0)
            title_color = self._interpolate_color("#1c1c1c", "#FFFFFF", alpha)
            subtitle_color = self._interpolate_color("#1c1c1c", "#AAAAAA", alpha)
            version_color = self._interpolate_color("#1c1c1c", "#888888", alpha)
            
            self.title_label.configure(text_color=title_color)
            self.subtitle_label.configure(text_color=subtitle_color)
            self.version_label.configure(text_color=version_color)
            self.after(20, lambda: self._fade_in_text(alpha))
        else:
            # Start pulsing after text is visible
            self.is_pulsing = True
            self._pulse_logo()

    def _pulse_logo(self):
        if not self.is_pulsing:
            return

        # Use a sine wave for a smooth pulse
        self.pulse_state += 0.08
        if self.pulse_state > 2 * math.pi:
            self.pulse_state = 0

        scale_factor = 1 + ((math.sin(self.pulse_state) + 1) / 2) * (self.pulse_amount - 1)
        
        new_width = int(self.logo_base_size[0] * scale_factor)
        new_height = int(self.logo_base_size[1] * scale_factor)
        
        self.logo_image.configure(size=(new_width, new_height))
        
        self.after(30, self._pulse_logo)

    def _interpolate_color(self, start_hex, end_hex, fraction):
        start_rgb = tuple(int(start_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        end_rgb = tuple(int(end_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        new_rgb = [int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * fraction) for i in range(3)]
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"

    def fade_out_and_destroy(self):
        self.is_pulsing = False # Stop the pulse animation
        self._fade_out()

    def _fade_out(self, alpha=1.0):
        if alpha > 0.0:
            alpha = max(alpha - 0.08, 0.0)
            self.attributes("-alpha", alpha)
            self.after(15, lambda: self._fade_out(alpha))
        else:
            self.destroy()

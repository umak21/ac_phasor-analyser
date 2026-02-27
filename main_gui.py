# main_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import your custom engineering module
from engineering_math import analyze_rlc_circuit

class InputPanel(ttk.LabelFrame):
    """A frame for user inputs for the RLC circuit."""
    def __init__(self, parent, run_callback):
        super().__init__(parent, text="Circuit Parameters", padding="15")
        self.run_callback = run_callback

        self.vars = {
            "Resistance (R) [Ω]": tk.StringVar(value="100"),
            "Inductance (L) [H]": tk.StringVar(value="0.1"),
            "Capacitance (C) [µF]": tk.StringVar(value="10"),
            "Voltage (V_rms) [V]": tk.StringVar(value="120"),
            "Frequency (f) [Hz]": tk.StringVar(value="60")
        }

        for i, (label_text, var) in enumerate(self.vars.items()):
            ttk.Label(self, text=label_text).grid(row=i, column=0, sticky="w", pady=8)
            entry = ttk.Entry(self, textvariable=var, width=14, font=('Segoe UI', 10))
            entry.grid(row=i, column=1, padx=10, pady=8)

        analyze_btn = ttk.Button(self, text="Run Phasor Analysis", command=self.run_callback)
        analyze_btn.grid(row=len(self.vars), column=0, columnspan=2, pady=20, sticky="ew")

    def get_values(self):
        """Parses and returns the input values as a dictionary of floats."""
        return {
            'R': float(self.vars["Resistance (R) [Ω]"].get()),
            'L': float(self.vars["Inductance (L) [H]"].get()),
            'C': float(self.vars["Capacitance (C) [µF]"].get()) * 1e-6,
            'V_rms': float(self.vars["Voltage (V_rms) [V]"].get()),
            'freq': float(self.vars["Frequency (f) [Hz]"].get())
        }

class ResultsPanel(ttk.LabelFrame):
    """A frame for displaying the numerical results of the analysis."""
    def __init__(self, parent):
        super().__init__(parent, text="Engineering Results", padding="10")
        self.res_text = tk.Text(self, height=20, width=40, font=("Consolas", 11),
                                bg="#ffffff", fg="#2c3e50", relief="flat", padx=10, pady=10)
        self.res_text.pack(fill=tk.BOTH, expand=True)

    def display_results(self, res, current_f):
        """Clears the text area and displays the new results."""
        self.res_text.delete(1.0, tk.END)
        output = (
            f"=== COMPLEX IMPEDANCE ===\n"
            f"Z     = {res['Z_total']:.2f} Ω\n"
            f"|Z|   = {abs(res['Z_total']):.2f} Ω\n"
            f"Phase = {res['phase_deg']:.2f}°\n\n"
            f"=== PHASOR CALCULATIONS ===\n"
            f"I_mag = {res['I_mag']:.3f} A\n\n"
            f"=== POWER ANALYSIS ===\n"
            f"P     = {res['P_real']:.2f} W (Real)\n"
            f"Q     = {res['Q_react']:.2f} VAR (React)\n"
            f"S     = {res['S_app']:.2f} VA (Apparent)\n"
            f"PF    = {res['pf']:.3f}\n\n"
            f"=== FILTER & RESONANCE ===\n"
            f"f_op  = {current_f:.2f} Hz\n"
            f"f_res = {res['f_res']:.2f} Hz\n"
            f"Q-Fac = {res['Q_factor']:.2f}\n"
            f"BW    = {res['bandwidth']:.2f} Hz\n"
        )
        self.res_text.insert(tk.END, output)

class PlotPanel(ttk.Frame):
    """A frame for displaying the matplotlib frequency response plots."""
    def __init__(self, parent):
        super().__init__(parent, padding="20")
        plt.style.use('bmh')
        self.fig, (self.ax_mag, self.ax_phase) = plt.subplots(2, 1, figsize=(8, 8), dpi=100)
        self.fig.patch.set_facecolor('#ecf0f1')
        self.fig.tight_layout(pad=5.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear_plots(self):
        """Clears both plot axes."""
        self.ax_mag.clear()
        self.ax_phase.clear()

    def draw(self):
        """Redraws the canvas."""
        self.canvas.draw()

class ACAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AC Circuit Phasor Analysis Tool")
        self.root.geometry("1150x800")
        self.root.configure(bg="#ecf0f1") # Light gray background
        
        self.apply_advanced_styling()
        
        # Main Layout
        self.left_panel = ttk.Frame(root, padding="20")
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        self.right_panel = ttk.Frame(root, padding="20")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create and pack the component panels
        self.input_panel = InputPanel(self.left_panel, self.run_analysis)
        self.input_panel.pack(fill=tk.X, pady=(0, 15))
        self.results_panel = ResultsPanel(self.left_panel)
        self.results_panel.pack(fill=tk.BOTH, expand=True)
        self.plot_panel = PlotPanel(self.right_panel)
        self.plot_panel.pack(fill=tk.BOTH, expand=True)

    def apply_advanced_styling(self):
        """Applies a modern, flat UI theme to the Tkinter widgets."""
        style = ttk.Style()
        style.theme_use('clam') # 'clam' allows for better color customization
        
        # Colors
        bg_color = "#ecf0f1"
        text_color = "#2c3e50"
        accent_color = "#2980b9"
        
        # Configure standard widgets
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, font=('Segoe UI', 12, 'bold'), foreground=accent_color)
        style.configure('TLabelframe.Label', background=bg_color)
        style.configure('TLabel', background=bg_color, font=('Segoe UI', 10), foreground=text_color)
        
        # Configure stylized button
        style.configure('TButton', font=('Segoe UI', 11, 'bold'), background=accent_color, foreground="white", padding=8)
        style.map('TButton', background=[('active', '#3498db')]) # Lighter blue on hover

    def run_analysis(self):
        try:
            inputs = self.input_panel.get_values()
            components = {'R': inputs['R'], 'L': inputs['L'], 'C': inputs['C']}
            
            # Perform calculation
            results = analyze_rlc_circuit(components, inputs['V_rms'], inputs['freq'])
            
            # Update UI components
            self.results_panel.display_results(results, inputs['freq'])
            self.plot_frequency_response(components, inputs['freq'], results['f_res'])

        except ValueError:
            messagebox.showerror("Input Error", "All inputs must be valid numbers.")
        except ZeroDivisionError:
            messagebox.showerror("Math Error", "Frequency and component values must be > 0.")

    def plot_frequency_response(self, components, current_f, f_res):
        R, L, C = components['R'], components['L'], components['C']
        
        f_min = max(1, f_res * 0.1)
        f_max = f_res * 3
        freqs = np.linspace(f_min, f_max, 500)
        omegas = 2 * np.pi * freqs
        
        Z_array = R + 1j * (omegas * L - 1 / (omegas * C))
        Z_mag = np.abs(Z_array)
        Z_phase = np.degrees(np.angle(Z_array))
        
        # Plot Magnitude
        self.plot_panel.clear_plots()
        ax_mag = self.plot_panel.ax_mag
        ax_mag.plot(freqs, Z_mag, color='#2980b9', linewidth=2, label='|Z| (Ohms)')
        ax_mag.axvline(f_res, color='#27ae60', linestyle=':', linewidth=2, label='Resonance')
        ax_mag.axvline(current_f, color='#e74c3c', linestyle='--', linewidth=2, label='Operating Freq')
        ax_mag.set_title('Impedance Magnitude Response', fontweight='bold')
        ax_mag.set_ylabel('|Z| (Ω)')
        ax_mag.legend()

        # Plot Phase
        ax_phase = self.plot_panel.ax_phase
        ax_phase.plot(freqs, Z_phase, color='#8e44ad', linewidth=2, label='Phase Angle')
        ax_phase.axhline(0, color='gray', linewidth=1)
        ax_phase.axvline(f_res, color='#27ae60', linestyle=':', linewidth=2)
        ax_phase.axvline(current_f, color='#e74c3c', linestyle='--', linewidth=2)
        ax_phase.set_title('Impedance Phase Response', fontweight='bold')
        ax_phase.set_xlabel('Frequency (Hz)')
        ax_phase.set_ylabel('Phase (°)')

        self.plot_panel.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ACAnalyzerApp(root)
    root.mainloop()
# engineering_math.py
import numpy as np

def analyze_rlc_circuit(components, v_rms, freq):
    """
    Performs phasor and power calculations for a series RLC circuit.
    Fulfills Requirements 1 (Component Modeling) & 2 (Phasor Calculations).
    """
    R = components['R']
    L = components['L']
    C = components['C']
    
    omega = 2 * np.pi * freq
    
    # 1. Component Modeling (Complex Impedances)
    Z_R = complex(R, 0)
    Z_L = complex(0, omega * L)
    Z_C = complex(0, -1 / (omega * C))
    Z_total = Z_R + Z_L + Z_C
    
    # 2. Phasor Calculations
    I_phasor = v_rms / Z_total
    phase_rad = np.angle(Z_total)
    
    # Power Calculations
    S = v_rms * np.conj(I_phasor)  # Complex Power
    P = S.real                     # Real Power (W)
    Q_power = S.imag               # Reactive Power (VAR)
    app_power = abs(S)             # Apparent Power (VA)
    pf = np.cos(phase_rad)         # Power Factor
    
    # 4. Engineering Applications (Resonance, Q-factor, Bandwidth)
    f_res = 1 / (2 * np.pi * np.sqrt(L * C))
    Q_factor = (1 / R) * np.sqrt(L / C)
    bandwidth = f_res / Q_factor
    
    return {
        'Z_total': Z_total,
        'I_mag': abs(I_phasor),
        'phase_deg': np.degrees(phase_rad),
        'P_real': P,
        'Q_react': Q_power,
        'S_app': app_power,
        'pf': pf,
        'f_res': f_res,
        'Q_factor': Q_factor,
        'bandwidth': bandwidth
    }
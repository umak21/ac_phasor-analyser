# test_engineering_math.py
import unittest
import numpy as np
from engineering_math import analyze_rlc_circuit

class TestRLCCircuitAnalysis(unittest.TestCase):

    def setUp(self):
        """Set up common variables for tests."""
        self.v_rms = 120
        self.components_standard = {'R': 10, 'L': 0.02, 'C': 100e-6}
        self.freq_standard = 60

    def test_standard_rlc_circuit(self):
        """
        Test with a standard set of RLC values at 60Hz.
        The circuit should be capacitive (X_C > X_L).
        """
        results = analyze_rlc_circuit(self.components_standard, self.v_rms, self.freq_standard)

        # Expected values calculated manually for R=10, L=0.02, C=100uF, V=120, f=60Hz
        # omega = 377, X_L = 7.54, X_C = 26.53
        # Z = 10 - j18.99
        self.assertAlmostEqual(results['Z_total'].real, 10.0, places=2)
        self.assertAlmostEqual(results['Z_total'].imag, -18.99, places=2)
        self.assertAlmostEqual(abs(results['Z_total']), 21.45, places=2)
        self.assertAlmostEqual(results['phase_deg'], -62.24, places=2)

        # I = V/Z = 120 / (10 - j18.99) = 2.61 + j4.95
        self.assertAlmostEqual(results['I_mag'], 5.60, places=2)

        # S = V * I_conj = 120 * (2.61 - j4.95) = 313.2 - j594
        self.assertAlmostEqual(results['P_real'], 313.16, places=2)
        self.assertAlmostEqual(results['Q_react'], -594.34, places=2)
        self.assertAlmostEqual(results['S_app'], 672.03, places=2)
        self.assertAlmostEqual(results['pf'], 0.466, places=3) # cos(-62.24)

        # Resonance calculations
        self.assertAlmostEqual(results['f_res'], 112.54, places=2)
        self.assertAlmostEqual(results['Q_factor'], 1.41, places=2)
        self.assertAlmostEqual(results['bandwidth'], 79.58, places=2)

    def test_resonant_frequency(self):
        """
        Test the circuit at its resonant frequency.
        Impedance should be purely real (Z=R), phase angle should be 0.
        """
        # f_res = 1 / (2*pi*sqrt(LC)) for the standard components
        resonant_freq = 112.54
        results = analyze_rlc_circuit(self.components_standard, self.v_rms, resonant_freq)

        # At resonance, Z = R
        self.assertAlmostEqual(results['Z_total'].real, self.components_standard['R'], places=2)
        self.assertAlmostEqual(results['Z_total'].imag, 0.0, places=2)
        self.assertAlmostEqual(results['phase_deg'], 0.0, places=2)

        # Current is maximum: I = V/R
        self.assertAlmostEqual(results['I_mag'], self.v_rms / self.components_standard['R'], places=2)

        # Power factor is 1, reactive power is 0
        self.assertAlmostEqual(results['pf'], 1.0, places=2)
        self.assertAlmostEqual(results['Q_react'], 0.0, places=2)

    def test_inductive_circuit(self):
        """
        Test with a frequency that makes the circuit inductive (X_L > X_C).
        Phase angle and reactive power should be positive.
        """
        # Use a frequency higher than resonance (e.g., 200 Hz)
        inductive_freq = 200
        results = analyze_rlc_circuit(self.components_standard, self.v_rms, inductive_freq)

        # Z.imag, phase, and Q should be positive
        self.assertGreater(results['Z_total'].imag, 0)
        self.assertGreater(results['phase_deg'], 0)
        self.assertGreater(results['Q_react'], 0)

    def test_capacitive_circuit(self):
        """
        Test with a frequency that makes the circuit capacitive (X_C > X_L).
        Phase angle and reactive power should be negative.
        """
        # The standard 60Hz case is already capacitive
        results = analyze_rlc_circuit(self.components_standard, self.v_rms, self.freq_standard)

        # Z.imag, phase, and Q should be negative
        self.assertLess(results['Z_total'].imag, 0)
        self.assertLess(results['phase_deg'], 0)
        self.assertLess(results['Q_react'], 0)

    def test_zero_frequency_error(self):
        """Test that a ZeroDivisionError is raised for a frequency of 0."""
        with self.assertRaises(ZeroDivisionError):
            analyze_rlc_circuit(self.components_standard, self.v_rms, 0)

    def test_zero_component_value_error(self):
        """Test that a ZeroDivisionError is raised for C=0."""
        components_zero_c = {'R': 10, 'L': 0.02, 'C': 0}
        with self.assertRaises(ZeroDivisionError):
            analyze_rlc_circuit(components_zero_c, self.v_rms, self.freq_standard)

if __name__ == '__main__':
    unittest.main()
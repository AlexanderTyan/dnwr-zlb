# Filename: lininterp.py
# Author: John Stachurski
# Date: August 2009
# Corresponds to: Listing 6.4

from scipy import interp
from scipy.interpolate import pchip_interpolate
import numpy as np
import matplotlib.pyplot as plt


class LinInterp(object):
    "Provides linear interpolation in one dimension."

    def __init__(self, X, Y, kind='linear'):
        """Parameters: X and Y are sequences or arrays
        containing the (x,y) interpolation points.

        kind : type of interpolation. one of {"linear", "pchip"}
        """
        self.X = np.sort(X)
        self.Y = Y

        if kind == 'linear':
            self.interp = interp
        elif kind == 'pchip':
            self.interp = pchip_interpolate
        else:
            raise NotImplementedError

    def __call__(self, z):
        """Parameters: z is a number, sequence or array.
        This method makes an instance f of LinInterp callable,
        so f(z) returns the interpolation value(s) at z.
        """
        try:
            return self.interp(z, self.X, self.Y)
        except ValueError:
            return self.interp(self.X, self.Y, z)

    def __add__(self, other):
        assert (self.X == other.X).all()
        return self.Y + other.Y

    def __sub__(self, other):
        assert (self.X == other.X).all()
        return self.Y - other.Y

    def plot(self, **kwargs):
        return plt.plot(self.X, self.Y, **kwargs)

    def inverse(self):
        return LinInterp(self.Y, self.X)

    def __mul__(self, other):
        """Elementwise Multiplication"""
        return LinInterp(X, Y * self.Y)

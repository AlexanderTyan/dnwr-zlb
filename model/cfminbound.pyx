cdef extern from "/usr/include/math.h":
    double sqrt(double x)
    double fabs(double)
    int signbit(double)
    double fmaxf(double, double)
    int copysign(int, double)

import numpy as np
cimport numpy as np
cimport cython
cimport numpy as np

cpdef double ch_(double x, double shock, w,
                    double pi, double beta=.97, double eta=2.5, double gamma=0.5, aggL=0.85049063822172699):
    """
    x: wage for tomorrow
    shock:
    w:
    pi:
    """
    return -1 * (x ** (1 - eta) - ((gamma / (gamma + 1)) * shock * (x ** (-eta) * aggL) ** ((gamma + 1) / gamma)) + beta * w((x / (1 + pi))))

cpdef cfminbound(func, double x1, double x2, w,
                 float shock, double pi, double eta=2.5, double gamma=0.5, double beta=.97,
                 int maxfun=500, double xtol=.00001, aggL=0.85049063822172699):
    """
    Minimize the negative of the value function.

    Parameters
    ----------
    func: function to be minimized
    x1 : lower bound
    x2 : upper bound
    w : value function
    shock : shock
    pi : inflation rate
    eta : utility param
    gamma : utility param
    maxfun : maximum number of function evaluations
    beta : discount
    xtol : tolerance
    aggL : utility param

    """
    cdef:
        double sqrt_eps = sqrt(2.2e-16)
        double golden_mean = 0.5 * (3.0 - sqrt(5.0))
        double a = x1
        double b = x2
        double fulc = a + golden_mean * (b - a)
        double nfc = fulc
        double xf = fulc
        double rat = 0.0
        double e = 0.0
        double x = xf
        double fx = func(x, shock, w, pi, beta)
        int num = 1
        fmin_data = (1, xf, fx) # array

        double ffulc = fx
        double fnfc = fx
        double xm = 0.5 * (a + b)
        double tol1 = sqrt_eps * fabs(xf) + xtol / 3.0
        double tol2 = 2.0 * tol1

        int golden, flag
        double r, q, p

    while (fabs(xf - xm) > (tol2 - 0.5 * (b - a))):
        golden = 1
        # Check for parabolic fit
        if fabs(e) > tol1:
            golden = 0
            r = (xf - nfc) * (fx - ffulc)
            q = (xf - fulc) * (fx - fnfc)
            p = (xf - fulc) * q - (xf - nfc) * r
            q = 2.0 * (q - r)
            if q > 0.0:
                p = -p
            q = fabs(q)
            r = e
            e = rat

            # Check for acceptability of parabola
            if ((fabs(p) < fabs(0.5*q*r)) and (p > q*(a - xf)) and
                    (p < q * (b - xf))):
                rat = (p + 0.0) / q
                x = xf + rat
                step = '       parabolic'

                if ((x - a) < tol2) or ((b - x) < tol2):
                    # si = np.sign(xm - xf) + ((xm - xf) == 0)
                    si = copysign(1, xm - xf) + ((xm - xf) == 0)
                    rat = tol1 * si
            else:      # do a golden section step
                golden = 1

        if golden:  # Do a golden-section step
            if xf >= xm:
                e = a - xf
            else:
                e = b - xf
            rat = golden_mean*e
            step = '       golden'

        si = copysign(1, rat) + (rat == 0)
        x = xf + si * fmaxf(fabs(rat), tol1)
        fu = func(x, shock, w, pi, beta)
        num += 1
        fmin_data = (num, x, fu)

        if fu <= fx:
            if x >= xf:
                a = xf
            else:
                b = xf
            fulc, ffulc = nfc, fnfc
            nfc, fnfc = xf, fx
            xf, fx = x, fu
        else:
            if x < xf:
                a = x
            else:
                b = x
            if (fu <= fnfc) or (nfc == xf):
                fulc, ffulc = nfc, fnfc
                nfc, fnfc = x, fu
            elif (fu <= ffulc) or (fulc == xf) or (fulc == nfc):
                fulc, ffulc = x, fu

        xm = 0.5 * (a + b)
        tol1 = sqrt_eps * fabs(xf) + xtol / 3.0
        tol2 = 2.0 * tol1

        if num >= maxfun:
            flag = 1
            break

    fval = fx
    return xf
#-----------------------------------------------------------------------------
# Main eval loop
DTYPE = np.double
# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.double_t DTYPE_t


@cython.boundscheck(False)
@cython.wraparound(False)
def opt_loop(np.ndarray[DTYPE_t, ndim=3] vals, np.ndarray[DTYPE_t, ndim=1] grid, np.ndarray[DTYPE_t, ndim=1] shock,
             object w, double pi, double lambda_):
    """
    This is the double loop at the heart of the optimization problem.

    Parameters
    ----------
    vals : ndarray :: Initially zeros; will be filled.
        (len(grid) x len(shock) x 5) where 5 is
        (wage, shock, convex combo of vals, free val, restricted val)
    grid : ndarray :: discrete set of wages
    shock : ndarray :: discrete set of shocks.

    Returns
    -------

    vals : ndarray :: filled in values.
    """
    cdef:
        int i = 0
        int j = 0
        int ngrid = grid.shape[0]
        int nshock = shock.shape[0]
        double w_max = grid[ngrid - 1]

        double y, z, m1, m2, value

    for i in range(ngrid):
        y = grid[i]
        for j in range(nshock):
            z = shock[j]

            if i == 0:
                m1 = cfminbound(ch_, 0, w_max, w, z, pi)
            else:
                m1 = vals[0, j, 3]
            m2 = cfminbound(ch_, y, w_max, w, z, pi)
            value = -1 * ((1 - lambda_) * ch_(m1, z, w, pi) + lambda_ * ch_(m2, z, w, pi))
            vals[i, j, 0] = y
            vals[i, j, 1] = z
            vals[i, j, 2] = value
            vals[i, j, 3] = m1
            vals[i, j, 4] = m2

    return vals

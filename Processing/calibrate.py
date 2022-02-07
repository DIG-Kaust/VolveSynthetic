import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from pylops.utils.signalprocessing     import convmtx

    
def calibrate(p, vz, s, r, isrc, dt, nt, vel_dir, vel_sep, rho_sep, twin=[0.01, 0.07], nfilt=15, plotflag=False):
    """direct wave calibration (for separation below seabed)"""
    # direct arrival
    distance = np.sqrt((s[1, isrc] - r[1]) ** 2 + \
                       (s[0, isrc] - r[0]) ** 2)
    tdir = distance / vel_dir
    
    # extract window around direct arrival
    offset = s[0, isrc] - r[0]
    itrace = np.argmin(np.abs(offset))

    pwin = p[itrace][int((tdir[itrace]-twin[0])/dt):int((tdir[itrace]+twin[1])/dt)]
    vzwin = vz[itrace][int((tdir[itrace]-twin[0])/dt):int((tdir[itrace]+twin[1])/dt)]
    nwin = len(pwin)

    # perform calibration
    vzmatx = convmtx(vzwin, nfilt)[:nwin]
    h = np.linalg.lstsq(vzmatx, pwin)[0]
    vzwincalib = sp.signal.fftconvolve(vzwin, h)[:nwin]
    vzcalib = sp.signal.fftconvolve(vz, h[np.newaxis, :], axes=-1)[:, :nt] / (rho_sep*vel_sep) 
    
    if plotflag:
        plt.figure()
        plt.plot(tdir)
        plt.figure()
        plt.plot(h / (rho_sep*vel_sep))

        plt.figure(figsize=(2, 3))
        plt.plot(pwin, 'k')
        plt.plot(vzwin * (rho_sep*vel_sep), 'r')

        plt.figure(figsize=(2, 3))
        plt.plot(pwin, 'k')
        plt.plot(vzwincalib, 'r')
    return vzcalib



def calibrate_refl(p, vz, s, r, isrc, dt, nt, vel_dir, vel_layer, z_layer, 
                   rho_dir, twin=[0.01, 0.07], nfilt=15, plotflag=False):
    """first reflection calibration (for separation above seabed)"""
    # direct arrival (src-rec)
    distance = np.sqrt((s[1, isrc] - r[1]) ** 2 + \
                       (s[0, isrc] - r[0]) ** 2)
    tdir = distance / vel_dir
    
    # extract window around direct arrival
    offset = s[0, isrc] - r[0]
    itrace = np.argmin(np.abs(offset))
    tdir = tdir[itrace]
    
    # add time in subsurface (up to first reflection)
    trefl = tdir + 2 * (z_layer - r[1, itrace]) / vel_layer
    
    pwin = p[itrace][int((trefl-twin[0])/dt):int((trefl+twin[1])/dt)]
    vzwin = vz[itrace][int((trefl-twin[0])/dt):int((trefl+twin[1])/dt)]
    nwin = len(pwin)

    # perform calibration
    vzmatx = convmtx(vzwin, nfilt)[:nwin]
    h = np.linalg.lstsq(vzmatx, -pwin)[0]
    vzwincalib = sp.signal.fftconvolve(vzwin, h)[:nwin]
    vzcalib = sp.signal.fftconvolve(vz, h[np.newaxis, :], axes=-1)[:, :nt] / (rho_dir*vel_dir) 
    
    if plotflag:
        plt.figure()
        plt.plot(h / (rho_dir*vel_dir))

        plt.figure(figsize=(2, 3))
        plt.plot(-pwin, 'k')
        plt.plot(vzwin * (rho_dir*vel_dir), 'r')

        plt.figure(figsize=(2, 3))
        plt.plot(-pwin, 'k')
        plt.plot(vzwincalib, 'r')
    return vzcalib
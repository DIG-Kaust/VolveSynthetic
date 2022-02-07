import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import butter, lfilter, medfilt, fftconvolve, filtfilt, sosfilt
from pylops.utils.signalprocessing import convmtx
from pylops.signalprocessing import FFT2D


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    sos = butter(order, normal_cutoff, btype='low', analog=False, output='sos')
    return sos


def butter_lowpass_filter(data, cutoff, fs, order=5):
    sos = butter_lowpass(cutoff, fs, order=order)
    y = sosfilt(sos, data)
    # shift back (use impulse response to find number of samples to shift back)
    imp = sosfilt(sos, [1] + [0] * 100)
    y = y[..., np.argmax(imp):]
    y = np.hstack([y, np.zeros(list(y.shape[:-1])+[np.argmax(imp)])])
    return y


def fk_filter(data, nrec, nt, dr, dt, FFTop, fmax, critical=0.95, 
              vel_sep=1500, ntapersmooth=100, ntapermask=10):
    nffts = (nrec, nt)
    FFTop = FFT2D(dims=[nrec, nt], 
                  nffts=nffts, sampling=[dr, dt])
    D = FFTop * data.ravel()
    D = D.reshape(nffts)
            
    [Kx, F] = np.meshgrid(FFTop.f1, FFTop.f2, indexing='ij')
    MASKFK = np.abs(Kx)<critical*np.abs(F)/vel_sep
    smooth = np.ones(ntapermask)/ntapermask
    MASKFK = filtfilt(smooth, 1, MASKFK, axis=1)

    imask = np.argmin(np.abs(FFTop.f2-fmax))
    MASK = np.zeros_like(D, dtype=np.complex)
    MASK[:, :imask] = 1
    MASK[:, -imask:] = 1
    smooth = np.ones(ntapersmooth)/ntapersmooth
    MASK = filtfilt(smooth, 1, MASK, axis=1)
    MASKAll = MASKFK * MASK

    Dfilt = MASKAll * D
    dfilt = FFTop.H * Dfilt.ravel()
    dfilt = np.real(dfilt.reshape(nrec, nt))
    return dfilt, D, Dfilt, MASKAll, imask


def fix_corrupt(d, izmin, nmed, threshmax, threshmin, plotflag=False, zmax=None,
                clip=1e5):
    """Simple fixing of anomalous traces based on rms+median filter
    identification and neighbour traces averaging
    """
    dorig = d.copy()
    rms = np.sqrt(np.sum(d[:, izmin:] ** 2, axis=1))
    rms_med = medfilt(rms, nmed)
    corrupted = (rms / rms_med > threshmax) | (rms / rms_med < threshmin)
    for icorr in np.where(corrupted)[0]:
        if icorr > 0 and icorr < d.shape[0] - 1:
            d[icorr] = (dorig[icorr - 1] + dorig[icorr + 1]) / 2.
    rms1 = np.sqrt(np.sum(d[:, izmin:] ** 2, axis=1))

    if plotflag:
        plt.figure()
        plt.plot(rms)
        plt.plot(rms_med)
        plt.plot(rms1)

        plt.figure()
        plt.plot(rms / rms_med)
        plt.plot(corrupted)

        zmax = d.shape[1] if zmax is None else zmax
        fig, axs = plt.subplots(1, 3, sharex=True, sharey=True, figsize=(16, 4))
        axs[0].imshow(dorig.T, cmap='seismic', vmin=-clip, vmax=clip,
                      interpolation=None)
        axs[0].set_title('d')
        axs[0].axis('tight')
        axs[1].imshow(d.T, cmap='seismic', vmin=-clip, vmax=clip,
                      interpolation=None)
        axs[1].set_title('dfilt')
        axs[1].axis('tight')
        axs[2].imshow(dorig.T - d.T, cmap='seismic', vmin=-clip, vmax=clip,
                      interpolation=None)
        axs[2].set_title('err')
        axs[2].axis('tight')
        axs[2].set_ylim(zmax, 0)

    return d, np.where(corrupted)[0]


def calibrated_wavefield_separation(sg, ishot,
                                    izmin=200, nmed=7, threshmax=1.4, threshmin=0.4, #fix_corrupt
                                    fmax=100., nlpf=5, filttype='butter', #filter
                                    vwater=1480., twin=[0.01, 0.07], nfilt=15,
                                    vel_sep=1500, rho_sep=1000, #calibration
                                    critical = 0.95, ntapersmooth=100, ntapermask=10, # fk filter
                                    plotflag=False, vzsc=1, imclip=1, tmax=1.,
                                    offmax=None):
    # read geometry for selected shot
    src_x = sg.srcx_local[ishot]
    src_y = sg.srcy_local[ishot]
    src_z = sg.srcz[ishot]
    
    nrec = len(sg.selected_rec)
    rec_x = sg.recx_local[sg.selected_rec]
    rec_y = sg.recy_local[sg.selected_rec]
    rec_z = sg.recz[sg.selected_rec]

    # compute offset
    offset_x = np.sqrt((src_x - rec_x) ** 2)
    offset = np.sqrt((src_x - rec_x) ** 2 + (src_y - rec_y) ** 2)
    distance = np.sqrt((src_z - rec_z) ** 2 + \
                       (src_x - rec_x) ** 2 + \
                       (src_y - rec_y) ** 2)
    tdir = distance / vwater
    offsetreg = np.linspace(-offset[0], offset[-1], nrec)
    if offmax is None:
        offmin = offsetreg[0]
        offmax = offsetreg[-1]
    else:
        offmin = -offmax

    # read data
    shot = sg.get_shotgather(ishot)
    
    # apply 3d to 2d conversion
    tgain = np.sqrt(sg.t[np.newaxis, :])
    shot['P'] = shot['P'] * tgain
    shot['VZ'] = shot['VZ'] * tgain

    # fix corrupted traces
    shot['P'] = fix_corrupt(shot['P'], izmin, nmed, threshmax, threshmin,
                            plotflag=plotflag, zmax=int(tmax/sg.dt))[0]
    shot['VZ'] = fix_corrupt(shot['VZ'], izmin, nmed, threshmax, threshmin,
                             plotflag=plotflag, zmax=int(tmax/sg.dt))[0]

    if fmax is None:
        pfilt, vzfilt = shot['P'].copy(), shot['VZ'].copy()
    else:
        # filter data to remove high-freq noise
        if filttype=='butter':
            pfilt = butter_lowpass_filter(shot['P'], fmax, 1 / sg.dt, nlpf)
            vzfilt = butter_lowpass_filter(shot['VZ'], fmax, 1 / sg.dt, nlpf)
        else:
            # filter data to remove high-freq noise and apply mask outside of signal cone
            dr = np.mean(np.diff(sg.recx[sg.selected_rec]))
            nffts = (nrec, sg.nt)
            FFTop = FFT2D(dims=[nrec, sg.nt], 
                          nffts=nffts, sampling=[dr, sg.dt])
          
            pfilt, P, Pfilt, MASKAll, imask = fk_filter(shot['P'], nrec, sg.nt, dr, sg.dt, FFTop, fmax, 
                                                        critical, vel_sep, ntapersmooth, ntapermask)
            vzfilt, VZ, VZfilt, _, _ = fk_filter(shot['VZ'], nrec, sg.nt, dr, sg.dt, FFTop, fmax, 
                                                 critical, vel_sep, ntapersmooth, ntapermask)
            
            
            if plotflag:
                fig, axs = plt.subplots(1, 3, sharey=True, figsize=(14, 7))
                axs[0].imshow(np.fft.fftshift(np.abs(MASKAll).T, axes=1)[:sg.nt//2], vmin=0, vmax=1, cmap='gray_r')
                axs[0].axis('tight')
                axs[1].imshow(np.fft.fftshift(np.abs(P).T, axes=1)[:sg.nt//2], 
                              vmin=0, vmax=0.5*np.abs(P).max(), cmap='jet')
                axs[1].axis('tight')
                axs[2].imshow(np.fft.fftshift(np.abs(Pfilt).T, axes=1)[:sg.nt//2], 
                              vmin=0, vmax=0.5*np.abs(P).max(), cmap='jet')
                axs[2].axis('tight')
                axs[2].set_ylim(imask+100, 0)

    # extract window around direct arrival
    itrace = np.argmin(offset)

    pwin = pfilt[itrace][int((tdir[itrace] - twin[0]) / sg.dt):int(
        (tdir[itrace] + twin[1]) / sg.dt)]
    vzwin = vzfilt[itrace][int((tdir[itrace] - twin[0]) / sg.dt):int(
        (tdir[itrace] + twin[1]) / sg.dt)]
    nwin = len(pwin)

    # perform calibration
    VZ = convmtx(vzwin, nfilt)[:nwin]
    h = np.linalg.lstsq(VZ, -pwin)[0]
    vzwincalib = fftconvolve(vzwin, h)[:nwin]
    vzcalib = fftconvolve(vzfilt, h[np.newaxis, :], axes=-1)[:, :sg.nt] / (vel_sep * rho_sep)

    # perform separation
    pup = (pfilt + vzcalib * (vel_sep * rho_sep)) / 2
    pdown = (pfilt - vzcalib * (vel_sep * rho_sep)) / 2

    if plotflag:
        pmax = np.max(np.abs(pfilt))
        vzorigmax = np.max(np.abs(vzfilt))
        vzmax = np.max(np.abs(vzcalib))

        plt.figure(figsize=(2, 3))
        plt.plot(pwin, 'k')
        plt.plot(-vzwin * vzsc, 'r')

        plt.figure()
        plt.plot(h)
        plt.figure(figsize=(2, 3))
        plt.plot(pwin, 'k')
        plt.plot(-vzwincalib, 'r')
        
        plt.figure(figsize=(12, 3))
        plt.plot(sg.t[:int(tmax/sg.dt)], sg.t[:int(tmax/sg.dt)] *pfilt[itrace][:int(tmax/sg.dt)], 'k', label='p')
        plt.plot(sg.t[:int(tmax/sg.dt)], -sg.t[:int(tmax/sg.dt)] *vzcalib[itrace][:int(tmax/sg.dt)] * (vel_sep * rho_sep), 'r', label='-vz scaled')
        plt.plot(sg.t[:int(tmax/sg.dt)], sg.t[:int(tmax/sg.dt)] *pup[itrace][:int(tmax/sg.dt)], 'g', label='pup')
        plt.legend()
        
        fig, axs = plt.subplots(1, 3, sharex=True, sharey=True, figsize=(15, 7))
        axs[0].imshow(pfilt.T, cmap='gray', vmin=-imclip * pmax, vmax=imclip * pmax,
                      extent=(-offset[0], offset[-1], sg.t[-1], sg.t[0]))
        axs[0].plot(offsetreg, tdir, 'r')
        axs[0].set_title('P(t,x)')
        axs[0].axis('tight')
        axs[0].set_xlim(-offmax, offmax)
        axs[1].imshow(-vzfilt.T, cmap='gray', vmin=-imclip * vzorigmax,
                      vmax=imclip * vzorigmax,
                      extent=(-offset[0], offset[-1], sg.t[-1], sg.t[0]))
        axs[1].set_title('-VZ(t,x)')
        axs[1].axis('tight')
        axs[1].set_xlim(-offmax, offmax)
        axs[1].set_ylim(tmax, 0)
        axs[2].imshow(-vzcalib.T * (vel_sep * rho_sep), cmap='gray', vmin=-imclip * pmax,
                      vmax=imclip * pmax,
                      extent=(-offset[0], offset[-1], sg.t[-1], sg.t[0]))
        axs[2].set_title('-VZcalib(t,x)')
        axs[2].axis('tight')
        axs[2].set_xlim(-offmax, offmax)
        axs[2].set_ylim(tmax, 0)

        fig, axs = plt.subplots(1, 3, sharex=True, sharey=True, figsize=(18, 7))
        axs[0].imshow(pfilt.T, cmap='gray', vmin=-imclip * pmax, vmax=imclip * pmax,
                      extent=(-offset[0], offset[-1], sg.t[-1], sg.t[0]))
        axs[0].set_title('P(t,x)')
        axs[0].set_xlim(-offmax, offmax)
        axs[0].axis('tight')
        axs[1].imshow(pup.T, cmap='gray', vmin=-imclip * pmax, vmax=imclip * pmax,
                      extent=(-offset[0], offset[-1], sg.t[-1], sg.t[0]))
        axs[1].set_title('P-(t,x)')
        axs[1].axis('tight')
        axs[1].set_xlim(-offmax, offmax)
        axs[2].imshow(pdown.T, cmap='gray', vmin=-imclip * pmax, vmax=imclip * pmax,
                      extent=(-offset[0], offset[-1], sg.t[-1], sg.t[0]))
        axs[2].set_title('P+(t,x)')
        axs[2].axis('tight')
        axs[2].set_xlim(-offmax, offmax)
        axs[2].set_ylim(tmax, 0)

    return pfilt, vzfilt, vzcalib, pup, pdown, offset_x, \
           pfilt[itrace], vzcalib[itrace], pup[itrace], pdown[itrace], rec_x[itrace], rec_y[itrace]


def mask_xt(trav, t, toff, nsmooth):
    """Causality mask in the time-space domain

    :param trav: Eikonal traveltimes, (nr, ns)
    :param t: Time axis, (nt,)
    :param toff: Time 'Epsilon' shift in the mask
    :param nsmooth: Smoothing parameter

    :return: Causality Preconditioner mask, (nt, nr, ns)
    """
    # define window size
    nt = t.size
    nr, ns = trav.shape

    # replicate along time axis
    trav = np.tile(trav, (nt, 1, 1))
    trav_off = trav - toff

    # build mask
    C = (t * np.ones([nt, nr, ns]).transpose(2, 1, 0)).transpose(2, 1, 0)
    C = (C > trav_off).astype(np.int)

    # smooth adges
    if nsmooth > 0:
        smooth = np.ones(nsmooth) / nsmooth
        C = filtfilt(smooth, 1, C)

    # extend to negative time [-t, t]
    C = np.concatenate((np.zeros([nt, nr, ns]), C[1:, :, :]), axis=0)

    return C
import m8r
import numpy as np
import matplotlib.pyplot as plt

# VP
vp_rsf = m8r.Input('../vp.rsf')
vp = np.array(vp_rsf[:]).reshape(vp_rsf.int('n2'), vp_rsf.int('n1')).T

# Ifull
i_rsf = m8r.Input('isum.rsf')
i = np.array(i_rsf[:]).reshape(i_rsf.int('n2'), i_rsf.int('n1')).T

# Iup
i_rsf = m8r.Input('iupsum.rsf')
iup = np.array(i_rsf[:]).reshape(i_rsf.int('n2'), i_rsf.int('n1')).T


# Inofs
i_rsf = m8r.Input('i_nofssum.rsf')
inofs = np.array(i_rsf[:]).reshape(i_rsf.int('n2'), i_rsf.int('n1')).T

# Inosea
i_rsf = m8r.Input('i_noseasum.rsf')
inosea = np.array(i_rsf[:]).reshape(i_rsf.int('n2'), i_rsf.int('n1')).T

# Imdd
i_rsf = m8r.Input('imddsum.rsf')
imdd = np.array(i_rsf[:]).reshape(i_rsf.int('n2'), i_rsf.int('n1')).T

# Imdd
i_rsf = m8r.Input('isgdsum.rsf')
isgd = np.array(i_rsf[:]).reshape(i_rsf.int('n2'), i_rsf.int('n1')).T

plt.figure(figsize=(10,5))
plt.imshow(i, cmap='gray', interpolation=None)
plt.show()

np.savez('images', vp=vp, i=i, iup=iup, inofs=inofs, inosea=inosea, imdd=imdd, isgd=isgd)

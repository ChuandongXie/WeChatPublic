# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 16:17:56 2022

@author: Chuandong
"""

import openseespy.opensees as op
from scipy import integrate
import numpy as np
import matplotlib.pyplot as plt


# %% Function
# %%% OpenSees
def forced_response_opensees():
    
    # %% Model
    op.wipe()
    op.model('basic', '-ndm', 1, '-ndf', 1)
    
    # %% Node
    op.node(1, 0.)
    op.node(2, 0.)
    op.fix(1, 1)
    op.mass(2, m)
    
    # %% Material
    matTag_Elastic = 1
    op.uniaxialMaterial('Elastic', matTag_Elastic, k)
    
    # %% Element
    eleTag_zeroLength = 1
    op.element('zeroLength', eleTag_zeroLength, *[1,2], '-mat', matTag_Elastic, '-dir', 1)
    
    # %% Damping
    alphaM = zeta
    betaKcurr = 0.0
    betaKinit = 0.0
    betaKcomm = 0.0
    op.rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm)
    
    # %% Load
    timeSeriesTag = 2
    op.timeSeries('Path', timeSeriesTag, '-dt', tStep, '-values', *acc)
    
    # uniformExcitation pattern
    uniformExcitationTag = 2
    accelDir = 1 # X direction
    op.pattern('UniformExcitation', uniformExcitationTag, accelDir, '-accel', timeSeriesTag, '-fact', -A_g)
    
    # %% Analysis
    op.wipeAnalysis()
    op.constraints('Plain')
    op.numberer('Plain')
    op.system('UmfPack')
    op.algorithm('Newton')
    op.test('NormDispIncr', 1.0e-8, 20)
    op.integrator('Newmark', 0.5, 0.25)
    op.analysis('Transient')
    
    # Analysis & record disp
    d = np.empty([0,1])
    for _ in range(len(ts)):
        op.analyze(1, tStep)
        d = np.append(d, [[op.nodeDisp(2,1)]], axis=0)
    
    max_d = np.max(np.abs(d[-num_max:-1]))
    op.wipe()
    return max_d


# %%% ODEINT

def forced_response_ode():

    def sdofs_deriv(x_xd, t, m=m, zeta=zeta, k=k):
        x, xd = x_xd
        return [xd, (A_g * np.cos(omega_g * t) / m) - (zeta / m) * xd - (k / m) * x]
    
    z0 = np.array([0.0, 0.0])
    z_t = integrate.odeint(sdofs_deriv, z0, ts)

    x, y = z_t.T
    max_x = np.max(np.abs(x[-num_max:-1]))
    return max_x


# %% Parameters
m = 1.0 # mass
k = 1.0 # stiffness
omega_n = np.sqrt(k / m) # frequency


# excitation
duration = 1000.0 # running time
tStep = 0.05 # time step
ts = np.arange(0.0, duration, tStep) # time list
A_g = 1.0 # amplitude of excitation
analysisSteps = int(duration / tStep) # running times


# analysis
omega_ls = np.linspace(0.1, 2.0,40)
zeta_ls = np.array([0.01])
sigma = np.linspace(0.0, 2.0, 200)


max_response_op = np.empty([0,2])
max_response_od = np.empty([0,2])
fig, ax = plt.subplots(figsize=(4,3), dpi=300)

for zeta in zeta_ls:
    for omega_g in omega_ls:
        acc = np.cos(omega_g * ts) # acceleration
        num_max = int(2*np.pi/omega_g/tStep)
        
        # OpenSees
        max_d = forced_response_opensees()
        max_response_op = np.append(max_response_op, [[omega_g / omega_n, max_d]], axis=0)
        
        # odeint
        max_d = forced_response_ode()
        max_response_od = np.append(max_response_od, [[omega_g / omega_n, max_d]], axis=0)
    
    R_d = 1 / np.sqrt((1 - sigma**2)**2 + (2 * zeta * sigma)**2) # Exact solution
    ax.plot(sigma, R_d, lw=1.0, label=f"$\zeta=\;{zeta}$")
    ax.scatter(max_response_op[:,0], max_response_op[:,1], s=2.0, label="Numerical: OpenSees")
    ax.scatter(max_response_od[:,0], max_response_od[:,1], s=2.0, label="Numerical: odeint")

# plot
ax.set_xlim([0,2.0])
ax.set_ylim([0,10])
ax.set_xlabel("$\omega/\omega_n$")
ax.set_ylabel("$R_d$")
ax.legend(fancybox=False, loc='upper right', edgecolor=[0,0,0])
plt.savefig('steady_state_response.png')
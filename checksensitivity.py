import numpy as np
from AeroSolver import AeroModel
from WeightSolver import WeightModel
from MDOF import MDOFinputs
from MDOF import FunctionsAndConstraints
from MDOF import optimizer
#
modelParams={'units': 'SI',
             'rho':1.2256,
             'bladeDensity':600,
             'emptyWeight':64000,
             'grossWeight':80000}

designvar=['Cl','R','Omega','sigma']
#
# instantiate inputs
# and analyses
#
inputObject=MDOFinputs(designvar)
inputs=inputObject.inputVar()
aero=AeroModel('momentumTheory',modelParams)
weight=WeightModel('simpleWeight',modelParams)
#
# create the input->output network
#
x1=aero.getModel(inputs)
outputs=weight.getModel(x1)
#
# evaluate response and sensitivity
# for a design point
#
x0=np.array([0.6,8.0,25.0,0.08],'d')
inputObject.setValue(x0)
obj=outputs(inputs)
#
# verify sensitivities against
# finite difference
#
eps=1e-6
#
for i in range(len(x0)):
  x1=x0.copy()
  x1[i]+=eps
  inputObject.setValue(x1)
  objp=outputs(inputs)
  if i==0:
     sens=((objp['values']-obj['values'])/eps)
  else:
     sens=np.vstack([sens,(objp['values']-obj['values'])/eps])
#
senso=obj['sensitivity'].transpose()
print('FD sensitivity\n',senso)
print('Analytical sensitivity\n',sens)

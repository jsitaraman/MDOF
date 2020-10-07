#
# driver code for sizing a simple
# rotor. 
#
# Design Variables are 
# [ Cl   -> mean Lift Coefficient,
#   R    -> Radius of the rotor,
#  Omega -> Rotor frequency
#  sigma -> Rotor solidity]
#
# Objective:
# Minimize Power (1) inequality constraint on gross weight (2) Thrust=weight
#
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
             'grossWeight':82000}

designvar=['Cl','R','Omega','sigma']
#
inputObject=MDOFinputs(designvar)
inputs=inputObject.inputVar()
aero=AeroModel('momentumTheory',modelParams)
weight=WeightModel('simpleWeight',modelParams)
#
# create the input to output mapping
#
x1=aero.getModel(inputs)
outputs=weight.getModel(x1)
#
fc=FunctionsAndConstraints(inputObject,inputs,outputs)
#objective=fc.get('constraint','Thrust',constraintValue=modelParams['grossWeight'],constraintType='eq')
#gradient=fc.get('gradient','Thrust',constraintValue=modelParams['grossWeight'],constraintType='eq')
objective=fc.get('constraint','Thrust=Weight',constraintType='eq')
gradient=fc.get('constraintgrad','Thrust=Weight',constraintType='eq')
eqconstraint=[]
eqconstraintgrad=[]
ineqconstraint=[]
ineqconstraintgrad=[]
#
x0=np.array([0.8,8.0,21.0,0.08],'d')
lb=[0.7,7.0,20.0,0.06]
ub=[1.0,9.0,30.0,0.12]
#
opt=optimizer(objective,gradient,eqconstraint,eqconstraintgrad,ineqconstraint,ineqconstraintgrad)
x=opt.optimize(x0,lb,ub)
print(objective(x))

# x0=x.copy()
# objective=fc.get('function','Power')
# gradient=fc.get('gradient','Power')
# ineqconstraint=[]
# ineqconstraintgrad=[]
# #ineqconstraint.append(fc.get('constraint','Weight',constraintValue=modelParams['grossWeight'],constraintType='eq'))
# #ineqconstraintgrad.append(fc.get('gradient','Weight',constraintValue=modelParams['grossWeight'],constraintType='eq'))
# #ineqconstraint.append(fc.get('constraint','Weight',constraintValue=modelParams['grossWeight']))
# #ineqconstraintgrad.append(fc.get('gradient','Weight',constraintValue=modelParams['grossWeight']))
# eqconstraint=[]
# eqconstraintgrad=[]
# #eqconstraint.append(fc.get('constraint','Thrust=Weight',constraintType='eq'))
# #eqconstraintgrad.append(fc.get('constraintgrad','Thrust=Weight',constraintType='eq'))
# ineqconstraint.append(fc.get('constraint','Thrust=Weight'))
# ineqconstraintgrad.append(fc.get('constraintgrad','Thrust=Weight'))
#
opt2=optimizer(objective,gradient,eqconstraint,eqconstraintgrad,ineqconstraint,ineqconstraintgrad)
x=opt2.optimize(x0,lb,ub)
#
print('designNames   :',designvar)
print('values        :',x)
resp=outputs(inputs)
print('stateNames    :',resp['varNames'])
print('values        :',resp['values'])
#
eps=1e-3
x1=x.copy()
x1[0]=x1[0]+eps
inputObject.setValue(x1)
resp=outputs(inputs)
x1[0]=x1[0]-2*eps
inputObject.setValue(x1)
resp2=outputs(inputs)



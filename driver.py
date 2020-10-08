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
# Minimize Hover power for carrying a given empty weight and payload with constraint
# of Thrust equaling Weight
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
             'emptyWeight':49000,
             'payLoad':15000,
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
# input--->----- Aero Model
#           |          |
#           ----- Weight Model ---> output
# 
x1=aero.getModel(inputs)
outputs=weight.getModel(x1)
#
# create the objective function and 
# constraints from vehicle response
#
fc=FunctionsAndConstraints(inputObject,inputs,outputs)
objective=fc.get('function','Power')
gradient=fc.get('gradient','Power')
ineqconstraint=[]
ineqconstraintgrad=[]
eqconstraint=[]
eqconstraintgrad=[]
eqconstraint.append(fc.get('constraint','Thrust=Weight'))
eqconstraintgrad.append(fc.get('constraintgrad','Thrust=Weight'))
#
# intialize optimizer object
# provide it the objectives, gradients and constraints
#
opt2=optimizer(objective,gradient,eqconstraint,eqconstraintgrad,ineqconstraint,ineqconstraintgrad)
#
# starting values and
# bounds
#
x0=np.array([0.6,7.5,25.0,0.08],'d')
lb=[0.1,6.0,10.0,0.06]
ub=[1.0,9.0,30.0,0.12]
#
# perform actual optimization
# functions and gradients are only 
# evaluated here
#
x=opt2.optimize(x0,lb,ub,1.0) # optimize such that abs(T-W) < 1 N
#
print('designNames   :',designvar)
print('values        :',x)
#
resp=inputObject.getResponse()
print('stateNames    :',resp['varNames'])
print('values        :',resp['values'])
#


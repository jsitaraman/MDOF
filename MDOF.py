import sys
import numpy as np


class MDOFinputs:
    def __init__(self,designVar):
        self.designVar=designVar
        self.x=np.zeros((len(designVar),),'d')

    def setValue(self,xx):
        m=0
        for x in xx:
            self.x[m]=x
            m=m+1
   
    def inputVar(self):
        def inputs():
            return self.x
        return inputs

class FunctionsAndConstraints:
    def __init__(self,inputObject,inputs,outputs):
        self.inputObject=inputObject
        self.inputs=inputs
        self.outputs=outputs

    def get(self,funcType,funcName,constraintValue=None,constraintType=None):
        def func(x):
            self.inputObject.setValue(x)
            response=self.outputs(self.inputs)            
            m=response['varNames'].index(funcName)
            if constraintValue is None:
                return response['values'][m] 
            else:
                if constraintType=='eq':
                    return abs(response['values'][m]-constraintValue)
                else:
                    return (response['values'][m]-constraintValue)

        def eqfunc(x):
            self.inputObject.setValue(x)
            response=self.outputs(self.inputs)
            name1=funcName.split('=')[0]
            name2=funcName.split('=')[1]
            m1=response['varNames'].index(name1)
            m2=response['varNames'].index(name2)
            if constraintType=='eq':
                return abs(response['values'][m1]-response['values'][m2])
            else:
                return (response['values'][m1]-response['values'][m2])

        def eqgrad(x):
            self.inputObject.setValue(x)
            response=self.outputs(self.inputs)
            name1=funcName.split('=')[0]
            name2=funcName.split('=')[1]
            m1=response['varNames'].index(name1)
            m2=response['varNames'].index(name2)
            if constraintType=='eq':
                if response['values'][m1] > response['values'][m2]:
                    return response['sensitivity'][m1,:]-response['sensitivity'][m2,:]
                else:
                    return response['sensitivity'][m2,:]-response['sensitivity'][m1,:]
            else:
                return response['sensitivity'][m1,:]-response['sensitivity'][m2,:]
        def grad(x):
            self.inputObject.setValue(x)
            response=self.outputs(self.inputs)
            m=response['varNames'].index(funcName)
            if constraintValue is None:
                return response['sensitivity'][m,:]
            else:
                if constraintType=='eq':
                    if response['values'][m] > constraintValue:
                        return response['sensitivity'][m,:]
                    else:
                        return -response['sensitivity'][m,:]
                else:
                    return response['sensitivity'][m,:]

        if funcType=='function' or funcType=='constraint':
            if '=' not in funcName:
                return func
            else:
                return eqfunc
        else:
            if '=' not in funcName:
                return grad
            else:
                return eqgrad


class optimizer:
    def __init__(self,J,dJ_dx,Ceq,dCeq_dx,Cineq,dCineq_dx):
        self.J=J
        self.dJ_dx=dJ_dx
        self.constraints=[]
        if (len(Ceq) > 0):
            self.eq_cons={'type':'eq',
                          'fun':Ceq[0],
                          'jac':dCeq_dx[0]}
            self.constraints.append(self.eq_cons)
        if (len(Cineq) > 0):
            self.ineq_cons={'type':'ineq',
                            'fun':Cineq[0],
                            'jac':dCineq_dx[0]}
            self.constraints.append(self.ineq_cons)
    def optimize(self,x0,lb,ub):
        from scipy.optimize import Bounds
        from scipy.optimize import minimize

        bounds=Bounds(lb,ub)
        res = minimize(self.J,x0,method='SLSQP', jac=self.dJ_dx,
                       constraints=self.constraints,options={'ftol': 1e-9, 'disp': True},
                       bounds=bounds)
        return res.x
    
        

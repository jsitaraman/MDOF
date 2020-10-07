import sys
import numpy as np
#
# MDOF inputs class
# basic now
#
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
#
# Functions and constraintss
# library, have to be expanded
# significantly, Also needs error checking
#
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
            return (response['values'][m1]-response['values'][m2])

        def eqgrad(x):
            self.inputObject.setValue(x)
            response=self.outputs(self.inputs)
            name1=funcName.split('=')[0]
            name2=funcName.split('=')[1]
            m1=response['varNames'].index(name1)
            m2=response['varNames'].index(name2)
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
#
# basic optimizer class
# that wraps scipy constrained optimizers
#
class optimizer:
    def __init__(self,J,dJ_dx,Ceq,dCeq_dx,Cineq,dCineq_dx):
        self.J=J
        self.dJ_dx=dJ_dx
        self.constraints=[]
        self.Ceq=Ceq
        self.dCeq_dx=dCeq_dx
        self.Cineq=Cineq
        self.dCineq_dx=dCineq_dx
        #
        # TODO: have to figure out how to send more than one constraint
        # function to SLSQP minimize
        #
        if (len(Ceq) > 0):
            self.eq_cons={'type':'eq',
                          'fun':self.Ceq[0],
                          'jac':self.dCeq_dx[0]}
            self.constraints.append(self.eq_cons)
        if (len(Cineq) > 0):
            self.ineq_cons={'type':'ineq',
                            'fun':self.Cineq[0],
                            'jac':self.dCineq_dx[0]}
            self.constraints.append(self.ineq_cons)
        
    def optimize(self,x0,lb,ub,eq_tol,method='trust-constr'):
        from scipy.optimize import Bounds
        from scipy.optimize import minimize
        from scipy.optimize import NonlinearConstraint
        from scipy.optimize import BFGS
        from scipy.optimize import SR1
        
        if (method=='SLSQP'):
            #
            # TODO SLSQP doesn't seem to work now ?
            #
            bounds=Bounds(lb,ub)
            res = minimize(self.J,x0,method='SLSQP', jac=self.dJ_dx,
                           constraints=self.constraints,options={'ftol': 1e-9, 'disp': True},
                           bounds=bounds)
            return res.x
        elif (method=='trust-constr'):
            bounds=Bounds(lb,ub)
            def cons_f(x):
                val=[]
                for f in self.Ceq:
                   val.append(f(x))
                for f in self.Cineq:
                   val.append(f(x))
                val=np.array(val,'d')
                return val
            def jac_f(x):
                jac=None
                for c in self.dCeq_dx:
                    if jac==None:
                        jac=c(x)
                    else:
                        jac=np.vstack([jac,c(x)])
                for c in self.dCineq_dx:
                    if jac==None:
                        jac=c(x)
                    else:
                        jac=np.vstack([jac,c(x)])
                return jac
            lc=[]
            uc=[]
            for f in self.Ceq:
                lc.append(-eq_tol)
                uc.append(eq_tol)
            for f in self.Cineq:
                lc.append(0.0)
                uc.append(np.inf)
            #
            # create the constraint
            # and minimize by using SR1 update for the hessian
            #
            nonlinear_constraint=NonlinearConstraint(cons_f,lc,uc, jac=jac_f, hess=BFGS())
            res = minimize(self.J, x0, method='trust-constr',  jac=self.dJ_dx, hess=SR1(),
               constraints=[nonlinear_constraint],
               options={'verbose': 1}, bounds=bounds)
            return res.x
        

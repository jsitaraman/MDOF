import numpy as np
import sys

class AeroModel:
    def __init__(self,modelName,modelParams=None):
        self.mp=modelParams
        self.modelName=modelName
    def getModel(self,auxInputs=None):
        def momentumTheory(inputs):
            #
            # simple momentum theory
            #
            # Ct=sigma*Cl/6
            # Cq=k*CT^1.5/sqrt(2)+sigma*Cd0/8
            # induced power coefficient, k  : f(DL) -> increases with disk loading
            # profile drag coefficient, Cd0 : f(Cl) -> increases with Cl (drag bucket)
            #
            x=inputs()
            if auxInputs!=inputs:
                aux=auxInputs(inputs)
            else:
                aux={}
                aux['varNames']=[]
                aux['values']=None
                aux['sensitivity']=None
            #
            Cl=x[0]
            R=x[1]
            Omega=x[2]
            sigma=x[3]
            #
            Ct=sigma*Cl/6
            dCt_dsigma=Cl/6
            dCt_dCl=sigma/6
            #
            Cd0=0.005+np.exp(0.01*Cl**4)-1.0 # drag bucket
            dCd0_dCl=np.exp(0.01*Cl**4)*0.01*4*Cl**3
            #
            T=Ct*self.mp['rho']*np.pi*R**4*Omega**2
            dT_dCt=self.mp['rho']*np.pi*R**4*Omega**2
            #
            dT_dCl=dT_dCt*dCt_dCl
            dT_dR =Ct*self.mp['rho']*np.pi*4*R**3*Omega**2
            dT_dOmega=Ct*self.mp['rho']*np.pi*R**4*2*Omega
            dT_dsigma=dT_dCt*dCt_dsigma
            #
            if self.mp['units']=='SI':
                factor=0.020885
            else:
                factor=1
            #
            DL=factor*T/(np.pi*R**2)
            dDL_dT=factor/(np.pi*R**2)
            #
            dDL_dCl=dDL_dT*dT_dCl
            dDL_dsigma=dDL_dT*dT_dsigma
            dDL_dR=factor/(np.pi)*(-2/R**3)
            dDL_dOmega=dDL_dT*dT_dOmega
            #
            k=np.exp(0.0001*DL*DL)   # induced power factor increases with DL
            dk_dDL=k*0.0001*2*DL
            #
            dk_dCl=dk_dDL*dDL_dCl
            dk_dR=dk_dDL*dDL_dR
            dk_dOmega=dk_dDL*dDL_dOmega
            dk_dsigma=dk_dDL*dDL_dsigma
            #
            Cp=k*Ct**(1.5)/np.sqrt(2)+sigma*Cd0*0.125
            dCp_dk=Ct**(1.5)/np.sqrt(2)
            dCp_dCt=k*1.5*np.sqrt(Ct)/np.sqrt(2)
            dCp_dCd0=sigma*0.125
            dCp_dsigma=Cd0*0.125
            #
            dCp_dCl=dCp_dk*dk_dCl+dCp_dCt*dCt_dCl+dCp_dCd0*dCd0_dCl
            dCp_dR=dCp_dk*dk_dR
            dCp_dsigma+=dCp_dk*dk_dsigma+dCp_dCt*dCt_dsigma
            dCp_dOmega=dCp_dk*dk_dOmega
            #
            P=Cp*(self.mp['rho']*np.pi*R**5*Omega**3)
            dP_dCp=(self.mp['rho']*np.pi*R**5*Omega**3)
            dP_dR=Cp*(self.mp['rho']*np.pi*5*R**4*Omega**3)
            dP_dOmega=Cp*(self.mp['rho']*np.pi*R**5*3*Omega**2)
            #
            dP_dCl=dP_dCp*dCp_dCl
            dP_dR+=dP_dCp*dCp_dR
            dP_dOmega+=dP_dCp*dCp_dOmega
            dP_dsigma=dP_dCp*dCp_dsigma
            #
            outputs=aux
            outputs['varNames'].append('Thrust')
            outputs['varNames'].append('Power')
            if outputs['values'] is not None:
                outputs['values']=np.hstack([outputs['values'],np.array([T,P],'d')])
            else:
                outputs['values']=np.array([T,P],'d')

            sensitivity=np.array([[dT_dCl,dT_dR,dT_dOmega,dT_dsigma],
                                  [dP_dCl,dP_dR,dP_dOmega,dP_dsigma]])
            if outputs['sensitivity'] is not None:
                outputs['sensitivity']=np.vstack([outputs['sensitivity'],sensitivity])
            else:
                outputs['sensitivity']=sensitivity
            #
            return outputs

        if self.modelName=='momentumTheory':
           return momentumTheory
        else:
            print("Model not implemented")
            sys.exit()

import numpy as np
import sys

class WeightModel:
    def __init__(self,modelName,modelParams=None):
        self.modelParams=modelParams
        self.modelName=modelName
    def getModel(self,auxInputs=None):
        # A simple weight model
        def simpleWeight(inputs):
            x=inputs()
            if auxInputs!=None:
                aux=auxInputs(inputs)
            #
            R=x[1]
            sigma=x[3]
            T=aux['values'][0]
            P=aux['values'][1]
            #
            rhos=self.modelParams['bladeDensity'] 
            kt=0.01   # factor for hub weight
            kp=0.005  # factor for engine weight
            emptyWeight=self.modelParams['emptyWeight']
            payLoad=self.modelParams['payLoad']
            #
            # Weight = empty weight + blade weight + hub weight + engine weight
            # hub weight    = kt*Thrust
            # engine weight = kp*Power
            #
            Weight=emptyWeight+payLoad+rhos*sigma*np.pi*R*R+kt*T+kp*P 
            #
            dWeight_dCl=0
            dWeight_dR=rhos*sigma*np.pi*2*R
            dWeight_dOmega=0
            dWeight_dsigma=rhos*np.pi*R*R
            #
            dWeight_dT=kt
            dWeight_dP=kp
            #
            outputs=aux
            outputs['varNames'].append('Weight')
            outputs['values']=np.hstack([outputs['values'],np.array([Weight],'d')])
            sensitivity=np.array([dWeight_dCl,dWeight_dR,dWeight_dOmega,dWeight_dsigma],'d')
            localAuxSensitivity=np.array([kt,kp])
            sensitivity+=np.dot(localAuxSensitivity,aux['sensitivity'])
            outputs['sensitivity']=np.vstack([outputs['sensitivity'],sensitivity])
            #
            return outputs

        if self.modelName=='simpleWeight':
           return simpleWeight
        else:
            print("Model not implemented")
            sys.exit()

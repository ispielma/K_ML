from labscript_utils.unitconversions.UnitConversionBase import UnitConversion

class IntraAction_FM(UnitConversion):
    """
    Frequency modulation unit converesion, linear fit works well
    """
    base_unit = 'V'
    derived_units = ['MHz']
    
    def __init__(self, calibration_parameters=None):

        if calibration_parameters is None:
            calibration_parameters = {}
        
        self.parameters = calibration_parameters
        
        self.parameters.setdefault('f_0', 80)        # base frequency
        self.parameters.setdefault('MHz_per_V', 30)  # MHz per volt
        
        UnitConversion.__init__(self,self.parameters)

    def MHz_to_base(self, aom_frequency_MHz):
        return (aom_frequency_MHz - self.parameters['f_0']) / self.parameters['MHz_per_V']
        
    def MHz_from_base(self, V):
        return V * self.parameters['MHz_per_V'] +  self.parameters['f_0']


import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication
import KratosMultiphysics.ConstitutiveLawsApplication
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

class MainKratos_FOM(StructuralMechanicsAnalysis):
    def __init__(self, model, parameters):
        super().__init__(model, parameters)

    def ApplyBoundaryConditions(self):
        """
        Manually apply boundary conditions via Python logic.
        Stage 1a (0.0 to 1.0s): Axial stretching (Symmetric Pulling: +/- 1mm).
        Stage 1b (1.0 to 2.0s): Vertical pinching.
        """
        super().ApplyBoundaryConditions()
        
        model_part = self.model["Structure"]
        time = model_part.ProcessInfo[KratosMultiphysics.TIME]
        
        # 1. SYMMETRIC PULLING NEGATIVE (Z=-0.05)
        # Goal: reach -1mm stretch at t=1.0, maintain after.
        neg_val = -0.001 * min(time, 1.0)
        neg_part = model_part.GetSubModelPart("End_Boundary_Negative_z")
        for node in neg_part.Nodes:
            node.Fix(KratosMultiphysics.DISPLACEMENT_X)
            node.Fix(KratosMultiphysics.DISPLACEMENT_Y)
            node.Fix(KratosMultiphysics.DISPLACEMENT_Z)
            node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_X, 0.0)
            node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_Y, 0.0)
            node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_Z, neg_val)

        # 2. SYMMETRIC PULLING POSITIVE (Z=+0.05)
        # Goal: reach +1mm stretch at t=1.0, maintain after.
        pos_val = 0.001 * min(time, 1.0)
        pos_part = model_part.GetSubModelPart("End_Boundary_Positive_z")
        for node in pos_part.Nodes:
            node.Fix(KratosMultiphysics.DISPLACEMENT_X)
            node.Fix(KratosMultiphysics.DISPLACEMENT_Y)
            node.Fix(KratosMultiphysics.DISPLACEMENT_Z)
            node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_X, 0.0)
            node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_Y, 0.0)
            node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_Z, pos_val)

        # 3. PINCHING TOP
        # Goal: start at t=1.0, reach -9mm at t=2.0
        pinch_top = model_part.GetSubModelPart("Outer_Pinching_Boundary_Top")
        pinch_top_val = -0.009 * max(0.0, min(time - 1.0, 1.0))
        for node in pinch_top.Nodes:
            node.Fix(KratosMultiphysics.DISPLACEMENT_Y)
            node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_Y, pinch_top_val)

        # 4. PINCHING BOTTOM
        # Goal: start at t=1.0, reach +9mm at t=2.0
        pinch_bottom = model_part.GetSubModelPart("Outer_Pinching_Boundary_Bottom")
        pinch_bottom_val = 0.009 * max(0.0, min(time - 1.0, 1.0))
        for node in pinch_bottom.Nodes:
            node.Fix(KratosMultiphysics.DISPLACEMENT_Y)
            node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT_Y, pinch_bottom_val)

    def InitializeSolutionStep(self):
        super().InitializeSolutionStep()

if __name__ == "__main__":
    with open("ProjectParameters_FOM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    global_model = KratosMultiphysics.Model()
    simulation = MainKratos_FOM(global_model, parameters)
    simulation.Run()

import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication
import KratosMultiphysics.ConstitutiveLawsApplication

print("--- REGISTERED CONSTITUTIVE LAWS ---")
for key in KratosMultiphysics.KratosComponents.GetConstitutiveLawList():
    if "Neo" in key or "Hyper" in key:
        print(key)

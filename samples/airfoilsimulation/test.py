from airfoil import Airfoil

if __name__ == "__main__":
    af = Airfoil()
    af.angle = 30
    af.angle = 30
    af.nodes =200
    af.refinement = 3
    af.samples = 10
    af.viscosity = 0.0001
    af.speed = 10.0
    af.time = 1

    af.execute()

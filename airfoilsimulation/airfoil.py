import os
import subprocess
from subprocess import call
from molnframework.core.service.base import ServiceBase

def calc_ratio():
    numOfRatios = 0
    totRatio = 0.0
    for filename in os.listdir('results/'):
        if filename.endswith(".m"):
            name = "sudo chmod ugo+wrx " + 'results/'+filename
            subprocess.call(name, shell=True)
            with open('results/' + filename, "r") as f:
                lines = f.readlines()[1:]
                for results in lines:
                    words = results.split()
                    drag = words[1]
                    lift = words[2]
                    numOfRatios += 1
                    totRatio += float(drag)/float(lift)
    if numOfRatios == 0:
        numOfRatios = 1
    return totRatio/numOfRatios

def gen_msh(angle, nodes, ref):
    name = "scripts/./run.sh " + str(angle) + " " + str(angle) + " 1 " + str(nodes) + " " + str(ref)
    print (name)
    subprocess.call(name, shell=True)

def convert():
    for filename in os.listdir('outputs/msh'):
        if filename.endswith(".msh"):
            print (filename)
            name = "sudo chmod ugo+wrx " + "outputs/msh/"+filename
            subprocess.call(name, shell=True)
            name = "sudo dolfin-convert " + "outputs/msh/" + filename + " outputs/msh/" + filename + ".xml"
            subprocess.call(name, shell=True)

def cleanup():
    subprocess.call("rm outputs/geo/*.*" , shell=True)
    subprocess.call("rm outputs/msh/*.*" , shell=True)
    subprocess.call("rm results/*.*" , shell=True)

class Airfoil(object):

    angle = 0
    nodes = 0
    refinement = 0 
    samples = 0
    viscosity = 0.0 
    speed = 0.0 
    time = 0.0

    # service configuration
    
    parameters = ['angle','nodes','refinement','samples','viscosity','speed','time']
    is_single_instance = True
    address='air_foil'

    def execute(self):
        # clean up
        cleanup()

        # generate mesh
        gen_msh(self.angle,self.nodes,self.refinement)

        # convert mesh to xml
        convert()

        for filename in os.listdir('outputs/msh'):
            if "r" + str(self.refinement) in filename and filename.endswith(".xml"):
                name = "sudo chmod ugo+wrx " + "outputs/msh/"+filename
                subprocess.call(name, shell=True)
                name = 'bin/./airfoil ' + str(self.samples) + ' ' + str(self.viscosity) + ' ' + str(self.speed) + ' ' + str(self.time) + ' outputs/msh/' + filename
                #print (name)
                subprocess.call(name, shell=True)

        return calc_ratio()

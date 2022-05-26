# -*- coding: utf-8 -*-
"""
Created on Wed Jul 09 16:14:35 2014
"""

# import of functions, classes...
import os, sys, time, random
#from numpy import *
#from scipy import *
sys.path.append(os.path.join('c:\\','app','sumo-0.21.0','tools'))
import traci
import winsound
from functions import *
#import pylab as pl

#### Begin Initilization of Variables ####

gui_on=1 # 1: SUMO starts with GUI | 0: SUMO starts without GUI
k=0      # Startvalue for counter of simulation steps

# Definition of Colors (R,G,B, unused)
red=(255,0,0,0)
green=(0,255,0,0)
blue=(0,0,255,0)
white=(0,0,0,0)

# Creation of Demand
demand_highway=[2000]
demand_onramp=[900]
truck_share=[10]
create_demand(demand_highway, demand_onramp, truck_share)


# Derivation of number of simulationsteps
K=3600*len(demand_highway)

#### End Initilization of Variables ####

# Start of SUMO and TRACI
#exe_name=start_sumo(gui_on)
exe_name='sumo-gui'
embed_traci(exe_name)
num_of_veh=0;

#### begin main loop (simulation)
while k==0 or k<K:


    # constant green to turn off ramp metering
    next_TL_state='G'

    traci.trafficlights.setRedYellowGreenState('tl_onramp',next_TL_state)

    # function designed to help vehicles merging
    raise_cooperativeness(1,80)
    # function to limit speed on neighbouring lanes
    lane_dependency(['A','X','B'],[0,1,1],3)

	if k > 499:
	 num_of_veh=traci.vehicle.getIDCount()
	 veh_list=traci.vehicle.getIDList()
	 counter = 1
	 while (counter<num_of_veh):
	  traci.vehicle.setColor(veh_list[counter], green)
	  counter+=1

    k+=1
    traci.simulationStep()

#### end main loop (simulation)

traci.close()

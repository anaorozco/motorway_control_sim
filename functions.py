# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 16:27:24 2014
"""
# traci Traffic Control Interface *
import traci
from sumolib import checkBinary
import os, sys, time, subprocess
#from win32com.client import GetObject


def start_sumo(gui_on):
    if gui_on==1:
        exe_name="sumo-gui"
    else:
        exe_name="sumo"

    ########## SUMO SCHLIESSEN ################
    proc_list=[]
    WMI = GetObject('winmgmts:')
    processes = WMI.InstancesOf('Win32_Process')
    for process in processes:
        proc_list.append(process.Properties_('Name').Value )
    if exe_name+".exe" in proc_list:
        os.system("TASKKILL.exe /F /IM %s.exe" % exe_name)
        time.sleep(1)
    ########## SUMO SCHLIESSEN ################

    return exe_name


def embed_traci(exe_name):
    PORT = 8813
    if not traci.isEmbedded():

        sumoBinary = checkBinary(exe_name+'.exe')
        sumoConfig = "sumo/saa_ext.sumo.cfg"
        if len(sys.argv) > 1:
            retCode = subprocess.call("%s -c %s --python-script %s --time-to-teleport -1" % (sumoBinary, sumoConfig, __file__), shell=True, stdout=sys.stdout)
            sys.exit(retCode)
        else:
            sumoProcess = subprocess.Popen("%s -c %s --time-to-teleport -1" % (sumoBinary, sumoConfig), shell=True, stdout=sys.stdout)
            traci.init(PORT)

    return 0

def create_demand (demand_highway, demand_onramp, truck_share):

    if len(demand_highway) != len(demand_onramp) or len(demand_highway) != len(truck_share):
        print "Demand cannot be created. Wrong length."
        return 0


    routes = open("sumo/saa_ext.rou.xml", "w")

    hours=min(min(len(demand_highway),len(demand_highway)),len(truck_share))

    print >> routes, """<routes>"""
    print >> routes, """<vTypes>"""
    print >> routes, """ <vType id="car1" accel="1.5" decel="8.0" sigma="0.5" tau="1.0" length="5" minGap="1.5" maxSpeed="45" speedFactor="1.2" speedDev="0.1" guishape="passenger"/>
    <vType id="car2" accel="1.2" decel="7.0" sigma="0.5" tau="1.2" length="5" minGap="2.5" maxSpeed="38" speedFactor="1.0" speedDev="0.1" guishape="passenger" />
    <vType id="truck1" accel="0.8" decel="5.0" sigma="0.5" tau="1.5" length="10" minGap="3.0" maxSpeed="25" speedFactor="0.8" speedDev="0.1" guishape="delivery" vClass="delivery"/>
    <vType id="car3" accel="1.5" decel="3.0" sigma="0.5" tau="1.0" length="5" minGap="1.0" maxSpeed="45" speedFactor="1.2" speedDev="0.1" guishape="passenger" vClass="ignoring"/>
    <vType id="car4" accel="1.2" decel="3.0" sigma="0.5" tau="1.2" length="5" minGap="1.0" maxSpeed="38" speedFactor="1.0" speedDev="0.1" guishape="passenger" vClass="ignoring"/>
    <vType id="truck2" accel="0.8" decel="3.0" sigma="0.5" tau="1.5" length="10" minGap="1.0" maxSpeed="25" speedFactor="0.8" speedDev="0.1" guishape="delivery" vClass="ignoring"/>"""

    print >> routes, """</vTypes>"""
    print >> routes, """<route id="r1" color="1,1,0" edges="Start S A X B C D E"/>
    <route id="r2" color="1,1,0" edges="Einfahrt M N X B C D E"/>"""
    print >> routes, "<flows>"
    for hour in range(hours):
        hour_str=str(hour)
        begin=str(hour*3600)
        end=str((hour+1)*3600)

        truck_share[hour]=max(truck_share[hour],1)
        truck_share[hour]=min(truck_share[hour],99)

        dem_hw_car=str(max(demand_highway[hour]*(100-truck_share[hour])/200,1))
        dem_or_car=str(max(demand_onramp[hour]*(100-truck_share[hour])/200,1))
        dem_hw_truck=str(max(demand_highway[hour]*(truck_share[hour])/100,1))
        dem_or_truck=str(max(demand_onramp[hour]*(truck_share[hour])/100,1))

        print >> routes, """
        <flow id='car_1_HW_"""+hour_str+"""' route='r1' begin='"""+begin+"""' end='"""+end+"""' vehsPerHour='"""+dem_hw_car+"""' type='car1' departLane='random' departPos='random_free' departSpeed='max'/>
        <flow id='car_2_HW_"""+hour_str+"""' route='r1' begin='"""+begin+"""' end='"""+end+"""' vehsPerHour='"""+dem_hw_car+"""' type='car2' departLane='random' departPos='random_free' departSpeed='max'/>
        <flow id='truck_1_HW_"""+hour_str+"""' route='r1' begin='"""+begin+"""' end='"""+end+"""' vehsPerHour='"""+dem_hw_truck+"""' type='truck1' departLane='random' departPos='random_free' departSpeed='max'/>

        <flow id='car_1_OR_"""+hour_str+"""' route='r2' begin='"""+begin+"""' end='"""+end+"""' vehsPerHour='"""+dem_or_car+"""' type='car3' departLane='best' departPos='random_free' departSpeed='max'/>
        <flow id='car_2_OR_"""+hour_str+"""' route='r2' begin='"""+begin+"""' end='"""+end+"""' vehsPerHour='"""+dem_or_car+"""' type='car4' departLane='best' departPos='random_free' departSpeed='max'/>
        <flow id='truck_1_OR_"""+hour_str+"""' route='r2' begin='"""+begin+"""' end='"""+end+"""' vehsPerHour='"""+dem_or_truck+"""' type='truck2' departLane='best' departPos='random_free' departSpeed='max'/>"""

    print >> routes, "</flows>"
    print >> routes, "</routes>"
    routes.close()


    return 1

def raise_cooperativeness (no_of_veh_on_ramp, max_speed):
    if traci.lane.getLastStepVehicleNumber('X_0')+traci.lane.getLastStepVehicleNumber('N_0')>no_of_veh_on_ramp:
        traci.lane.setMaxSpeed('A_0',max_speed/3.6)
        traci.lane.setMaxSpeed('X_1',max_speed/3.6)

#        traci.lane.setMaxSpeed('A_1',200/3.6)
#        traci.lane.setMaxSpeed('A_2',200/3.6)
        #traci.lane.setMaxSpeed('X_1',80/3.6)
        #traci.lane.setMaxSpeed('X_2',100/3.6)
#        traci.lane.setMaxSpeed('X_3',140/3.6)
#        traci.lane.setMaxSpeed('B_1',120/3.6)
#        traci.lane.setMaxSpeed('B_2',200/3.6)
#        traci.lane.setMaxSpeed('B_3',200/3.6)
        #print "Geschwindigkeit reduziert"

    else:
        traci.lane.setMaxSpeed('A_0',45)
        traci.lane.setMaxSpeed('A_1',45)
        traci.lane.setMaxSpeed('A_2',45)
        traci.lane.setMaxSpeed('X_1',45)
        traci.lane.setMaxSpeed('X_2',45)
        traci.lane.setMaxSpeed('X_3',45)
        traci.lane.setMaxSpeed('B_1',45)
        traci.lane.setMaxSpeed('B_2',45)
        traci.lane.setMaxSpeed('B_3',45)

def lane_dependency (edge_list, lane_list, no_of_lanes):
    edge_counter=0
    for edge in edge_list:
        meanspeed=traci.lane.getLastStepMeanSpeed(edge+'_'+str(lane_list[edge_counter]))
        meanspeed=max(20,meanspeed)
        for counter in range(no_of_lanes-1):
            traci.lane.setMaxSpeed(edge+'_'+str(lane_list[edge_counter]+counter+1),meanspeed*pow(1.5,counter))
        edge_counter+=1

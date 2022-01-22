import numpy as np
import math
import pandas as pd
import geopandas as gpd


height_of_a_person=1.55
height_of_a_vehicle=1.9

#*******************************************************************************
#functions
def froude_from_floodsimulations(flowdepth,flowvelocity):
    #compute the Froude number from flow velocity (vector from x and y velocity in m/s and flow depth in m
    #returns the Froude number
    froude = flowvelocity/(np.sqrt(9.81*flowdepth))
    return froude

def stability_of_a_person(heightofsubject, froudenumber, flowdepth):
    #compute the stability of a person in flood water
    #returns True or False
    #source Arrighi et al. (2019) https://doi.org/10.1016/j.scitotenv.2018.11.191
    relativesubmergence=0.29/(0.24+froudenumber)
    criticalflooddepth=relativesubmergence*heightofsubject
    if flowdepth/criticalflooddepth<1.0:
        pedestrianstability=True
    else:
        pedestrianstability=False
    return pedestrianstability

def stability_of_parked_vehicles(heightofobject, froudenumber, flowdepth):
    #compute the stability of a person in flood water
    #returns True or False
    # source Arrighi et al. (2019) https://doi.org/10.1016/j.scitotenv.2018.11.191
    relativesubmergence = -0.05 * froudenumber + 0.34
    criticalflooddepth = relativesubmergence * heightofobject
    if flowdepth/criticalflooddepth<1.0:
        vehiclestability = True
    else:
        vehiclestability = False
    return vehiclestability

def hazardclass(flowdepth, flowvelocity):
    #0..Not flooded, 1..flooded but not dangerous, 2..vehicle driving impossible, 3..pedestrians and vehicles endangered, 4..building damages expected
    froudenumber=froude_from_floodsimulations(flowdepth,flowvelocity)
    hazardclass=0
    pedestrianstability=stability_of_a_person(height_of_a_person, froudenumber, flowdepth)
    vehiclestability=stability_of_parked_vehicles(height_of_a_vehicle, froudenumber, flowdepth)
    vxh=flowvelocity*flowdepth
    if flowdepth==0 and flowvelocity==0:
        hazardclass = 0
    else:
        if pedestrianstability==True and vehiclestability==True and vxh<0.3 and flowdepth <0.3 and flowvelocity<2.0:
            hazardclass=1
        if flowdepth>=0.2:
            hazardclass=2
        if pedestrianstability==False or vehiclestability==False or vxh>=0.6 or flowdepth>0.5 or flowvelocity>2.0:
            hazardclass=3
        if flowdepth>1.5:
            hazardclass=4
    return hazardclass






#tests
v=0.5
d=0.25
fr=froude_from_floodsimulations(d,v)
pedstability=stability_of_a_person(height_of_a_person, fr, d)
vestab=stability_of_parked_vehicles(height_of_a_vehicle, fr, d)
hclass=hazardclass(d, v)

myworkspace="O:/MAAREplus/AarMei"
velocityx = gpd.read_file(myworkspace+"/AarMei_els_velocity_x.shp")
velocityy = gpd.read_file(myworkspace+"/AarMei_els_velocity_y.shp")
depth = gpd.read_file(myworkspace+"/AarMei_els_depth.shp")

outdf=pd.merge(depth['ext_id','50400'], velocityx['50400'], velocityy['50400'], on='ext_id', how='left')

velocityx.columns

hdf=depth[['ext_id','50400']].rename(columns={'50400':'h'})
velxdf= velocityx[['ext_id','50400']].rename(columns={'50400':'vx'})
velydf= velocityx[['ext_id','50400']].rename(columns={'50400':'vy'})
mergev=pd.merge(velxdf,velydf, on="ext_id")
mergev["v"]=np.sqrt(np.power(mergev["vx"],2)+np.power(mergev["vy"],2))
hazardclassdf=pd.merge(hdf,mergev, on="ext_id")
hazardclassdf["hazardclass"]=0
for i in hazardclassdf.index:
    hazardclassdf.at[i,"hazardclass"]=hazardclass(hazardclassdf.at[i,"h"], hazardclassdf.at[i,"v"])

max(hazardclassdf["hazardclass"])
hazardclassdf.to_csv(myworkspace+"/hazardclassat50400.csv")
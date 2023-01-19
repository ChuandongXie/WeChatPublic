# -*- coding: utf-8 -*-

import os
import pandas as pd
import re


def DATA_Processing(folder):
    # pattern
    pattern_ls = [
        '^(?P<Record_Number>[^\n]*)\n',
        '^(?P<Earthquake_Number>[^ ]*) (?P<Date>[^ ]*) (?P<Time>[^ ]*) (?P<Time_Zone>[^\n]*)\n',
        '^(?P<Earthquake_Name>[^,]*), (?P<Position>[^,]*),(?P<Country>[^\n]*)\n',
        '^EPICENTER +(?P<Latitude>[^ ]*) (?P<Longitude>[^ ]*) DEPTH (?P<Depth>[^ ]*) KM\n',
        '^MAGNITUDE +(?P<Magnitude>[^(]*)\((?P<Type_of_Magnitude>[^)]*)\)\n',
        '^[^:]*: (?P<Code_of_Station>[^ ]*) (?P<Latitude_of_Station>[^ ]*) (?P<Longitude_of_Station>[^\n]*)\n',
        '^SITE CONDITION: (?P<Site_Condition>[^\n]*)\n',
        '^INSTRUMENT TYPE: (?P<Instrument_Type>[^\n]*)\n',
        '^OBSERVING POINT: (?P<Observing_Point>[^\n]*)\n',
        '^COMP. (?P<Component>[^\n]*)\n',
        '^(?P<Correction>[A-Z ]*) +UNIT: (?P<Unit>[^\n]*)\n',
        '^NO. OF POINTS: +(?P<Number_of_Points>[^ ]*) +EQUALLY SPACED INTERVALS OF: +(?P<Intervals>[^ ]*)  SEC\n',
        '^PEAK VALUE: +(?P<Peak_Value>[^ ]*) +AT +(?P<Time_at_Peak_Value>[^ ]*) SEC +DURATION: +(?P<Duration>[^ ]*) +SEC\n',
        'PRE-EVENT TIME: +(?P<PreE_Time>[^ ]*) +SEC +RECORDER TIME: +(?P<Record_Date>[^ ]*) (?P<Record_Time>[^ ]*) (?P<Record_Time_Zone>[^\n]*)\n',
        '^(?P<Department>[^\n]*)\n',
        '\n'
        ]
    
    # filename list
    filename_ls = os.listdir(folder)
    
    # df_data
    df_data = pd.DataFrame()
    
    # processing
    # filename_ls = ['ua0001.dat']
    for filename in filename_ls:
        path = folder + "/" + filename
        dicts = {'Filename': os.path.splitext(filename)[0]}
        
        with open(path) as file:
            heads = [next(file) for x in range(16)]
        
        for i in range(len(pattern_ls)):
            pattern = re.compile(pattern_ls[i])
            line = heads[i]
            match = pattern.fullmatch(line)
            dict1 = match.groupdict()
            dicts = dicts | dict1
            
        # update dataFrame
        df_data = pd.concat([df_data, pd.DataFrame([dicts])])

    return df_data


folder = "example"
df = DATA_Processing(folder)
df.reset_index(drop=True, inplace=True)
df.to_csv(f"{folder}_list.csv")
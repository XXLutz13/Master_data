import pandas as pd
import numpy as np
import re
import os


def clean_inline_data(df):
    # rename columns to identical names from LEB setups
    df = df.rename(columns={'VIN': 'Vin', '-Ch1 IIN': 'Iin', '-Ch1 IOUT': 'Iout', '-Ch2 VINS': 'VinS', '-Ch3 VOUTS -Ch4': 'VoutS'})

    # iterate over all cells to manully remove and handle units + add leading 0
    for col in df.columns:
        for index, val in enumerate(df[col]):
            # scaling factor per row
            multiplier = 1.0
            if 'mA' in val:
                multiplier = 1e-3
            elif 'uA' in val:
                multiplier = 1e-6

            # remove units 
            clean_val = val.replace('V', '').replace('mA', '').replace('uA', '').replace(' ', '')
            # convert unit if needed (mA / uA)
            # df[col][index] = float(clean_val) * multiplier
            df.loc[index, col] = float(clean_val) * multiplier
    # convert to float
    df = df.apply(pd.to_numeric, errors='coerce')

    df['delta_V'] = df['VinS'] - df['VoutS']
    return df


def get_r_inner(foldername):
    # get r_inner from folder name => is equal in all subfolders
    match = re.search(r"\[ri=(\d+)\]", foldername)
    if match:
        r_inner = int(match.group(1))   # or float(...)
        return r_inner
        print(r_inner)
    else:
        raise ValueError("No r_inner found")    

class TLMREADER:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def readTLMData(self):
        # iterate over all files in the folder
        list_of_measurements = {}
        for file in os.listdir(self.folder_path):
            if file.endswith('.roh'):
                
                # old data
                try:
                    data = pd.read_csv(os.path.join(self.folder_path, file), delimiter='\t', skiprows=12, header=1, encoding='ISO-8859-1')
                    data['delta_V'] = data['VinS'] - data['VoutS']
                    
                    limit = 0.1  # 100mA
                    # Keep only rows where compliance limit is not reached
                    data = data[data['Iin'].abs() < limit].reset_index(drop=True)
                    
                    list_of_measurements[int(os.path.splitext(os.path.basename(file))[0])] = data

                except Exception as e:
                    
                    # inline data
                    try:
                        data = pd.read_csv(os.path.join(self.folder_path, file), delimiter=r'\s{2,}', skiprows=24, encoding='ISO-8859-1', engine='python')
                        data = clean_inline_data(data)
                        
                        limit = 0.1  # 100mA
                        # Keep only rows where compliance limit is not reached
                        data = data[data['Iin'].abs() < limit].reset_index(drop=True)

                        list_of_measurements[int(os.path.splitext(os.path.basename(file))[0])] = data
                        
                    except Exception as e:
                        print(f"Error reading file {file}: {e}")
                        continue
        
        return list_of_measurements
    

    def get_r_inner(self):
        # get r_inner from folder name => is equal in all subfolders
        match = re.search(r"\[ri=(\d+)\]", self.folder_path)
        if match:
            r_inner = int(match.group(1))   # or float(...)
            return r_inner
            print(r_inner)
        else:
            raise ValueError("No r_inner found")    
# -*- coding: utf-8 -*-
"""
This is the main file of the DispaSET pre-processing tool. It comprises a single function that generated the DispaSET simulation environment.

@author: S. Quoilin, edited by M. Zech
"""

import datetime as dt
import logging
import os
import shutil
import sys

import numpy as np
import pandas as pd
try:
    from future.builtins import int
except ImportError:
    logging.warning("Couldn't import future package. Numeric operations may differ among different versions due to incompatible variable types")
    pass

from .data_check import check_units, check_chp, check_sto, check_heat_demand, check_df, isStorage, check_MinMaxFlows,check_AvailabilityFactors, check_clustering
from .utils import clustering, interconnections, incidence_matrix
from .data_handler import UnitBasedTable,NodeBasedTable,merge_series, \
        define_parameter, write_to_excel, load_csv, load_config_excel, load_config_yaml

from ..misc.gdx_handler import write_variables
from ..common import commons  # Load fuel types, technologies, timestep, etc:

def build_simulation():
    dm = DispaModel(...)

GMS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'GAMS')

# TODO Move to utils
def get_git_revision_tag():
    """Get version of DispaSET used for this run. tag + commit hash"""
    from subprocess import check_output
    try:
        return check_output(["git", "describe", "--tags", "--always"]).strip()
    except:
        return 'NA'

def get_indices(config):
    # Indexes of the simulation:
    idx_std = pd.DatetimeIndex(pd.date_range(start=pd.datetime(*config['StartDate']),
                                            end=pd.datetime(*config['StopDate']),
                                            freq=commons['TimeStep'])
                            )
    idx_utc_noloc = idx_std - dt.timedelta(hours=1)
    idx_utc = idx_utc_noloc.tz_localize('UTC')
    # Indexes for the whole year considered in StartDate
    idx_utc_year_noloc = pd.DatetimeIndex(pd.date_range(start=pd.datetime(*(config['StartDate'][0],1,1,0,0)),
                                                        end=pd.datetime(*(config['StartDate'][0],12,31,23,59,59)),
                                                        freq=commons['TimeStep'])
                                        )
    return idx_utc, idx_utc_noloc, idx_utc_year_noloc

class DispaModel(object):

    # consists of 
    # 1) data 
    # 2) model


    def __init__(self, excel_path=None, yaml_path=None): # TODO constructor
        
        if excel_path:
            self.config = load_config_excel(excel_path)
        elif yaml_path:
            self.config = load_config_yaml(yaml_path)
        else:
            logging.error("Only yaml and excel files are supported")
            sys.exit(1)

        
        self.version = str(get_git_revision_tag())
        #self.CEP = config['CEP'] == 1
        #self.LP = config['SimulationType'] == 'LP' or config['SimulationType'] == 'LP clustered'
        self.idx_utc, self.idx_utc_noloc, idx_utc_year_noloc = get_indices(self.config)
        self.time_range = (self.idx_utc[-1] - self.idx_utc[0]).days 
        if not isinstance(self.config['default']['CostLoadShedding'],(float,int)):
            self.config['default']['CostLoadShedding'] = 1000
        if not isinstance(self.config['default']['CostHeatSlack'],(float,int)):
            self.config['default']['CostHeatSlack'] = 50

        # self.__dag = {'clustering': [self.build_model, None], #TODO
        #             'CEP': ['C', 'D'],
        #             'C': ['D'],
        #             'D': ['C'],
        #             'E': ['F'],
        #             'F': ['C']
        #             }
       #self.model.sets = load_sets()
        #self.model.params = load_params()


    def __str__(self):
        """Return a descriptive string for this instance, invoked by print() and str()"""

        return ('Dispa-SET model: \n -> %s to %s \n -> %i days' % \
             (str(self.idx_utc[0]), str(self.idx_utc[-1]), self.time_range)) #TODO

    __repr__ = __str__ # usage in jupyter notebooks

    def edit_config(self, key, new_value): #TODO
        """Edit the config file (practical for simulating multiple variations)
        
        Args:
            key (str): the parameter name inside the config name
            new_value (Any): new value for the parameter inside config
        """
        try:
            self.config[key] = new_value
            #update_DAG(key) 
        except KeyError as e: 
            print("Key not found")

    def _update_config(self, config): #TODO
        print("reevaluating ...")
        

    def solve_model(self, language="GAMS"):
        pass
    

    def build_simulation(self):
        """
        This method reads the DispaSET config, loads the specified data,
        processes it when needed, and formats it in the proper DispaSET format.
        The output of the function is a directory with all inputs and simulation files required to run a DispaSET simulation

        :param config: Dictionary with all the configuration fields loaded from the excel file. Output of the 'LoadConfig' function.
        :param plot_load: Boolean used to display a plot of the demand curves in the different zones
        """
        if self.config["SimulationDirectory"]:
            self.data = DataLoader(self.config)
            self.model = DispaModelFormulation(self.config)

        else:
            pass

    # def update_DAG(self):
    #     pass

# graph = {'clustering': ['B', 'C'],
#             'CEP': ['C', 'D'],
#             'C': ['D'],
#             'D': ['C'],
#             'E': ['F'],
#             'F': ['C']}

# class DAG():

#     def __init__(self, structure): 
#         self.structure = structure

# def define_parameter(sets_param, parameters, sets, var, indices, default_value, values):
#     sets_param[var] = indices
#     parameters[var] = define_parameter(sets_param[var], sets, value=default_value)
#     parameters[var]["val"] =  values

def define_parameters(DataLoader): 
    pass


class DataLoader(object):
    def __init__(self, config):
        self.config = config
        self.idx_utc, self.idx_utc_noloc, self.idx_utc_year_noloc = get_indices(self.config)
        self.load_loads()
        self.load_interconnections()
        self.load_load_shedding()
        

    def load_loads(self):
        config = self.config 
        self.Load = NodeBasedTable(self.config['Demand'], self.idx_utc_noloc, self.config['countries'], tablename='Demand')
        # For the peak load, the whole year is considered:
        self.PeakLoad = NodeBasedTable(self.config['Demand'], self.idx_utc_year_noloc, self.config['countries'], tablename='PeakLoad').max()
        if self.config['modifiers']['Demand'] != 1:
            logging.info('Scaling load curve by a factor ' + str(self.config['modifiers']['Demand']))
            self.Load = self.Load * self.config['modifiers']['Demand']
            self.PeakLoad = self.PeakLoad * self.config['modifiers']['Demand']

    def load_interconnections(self):
        # Interconnections:
        config = self.config 
        if os.path.isfile(config['Interconnections']):
            self.flows = load_csv(config['Interconnections'], index_col=0, parse_dates=True).fillna(0)
        else:
            logging.warning('No historical flows will be considered (no valid file provided)')
            self.flows = pd.DataFrame(index=self.idx_utc_noloc)
        if os.path.isfile(self.config['NTC']):
            self.NTC = load_csv(self.config['NTC'], index_col=0, parse_dates=True).fillna(0)
        else:
            logging.warning('No NTC values will be considered (no valid file provided)')
            self.NTC = pd.DataFrame(index=self.idx_utc_noloc)
        
        # Interconnections:
        [Interconnections_sim, Interconnections_RoW, Interconnections] = interconnections(config['countries'], self.NTC, self.flows)

        if len(Interconnections_sim.columns) > 0:
            self.NTCs = Interconnections_sim.reindex(self.idx_utc_noloc)
        else:
            self.NTCs = pd.DataFrame(index=self.idx_utc_noloc)
        self.Inter_RoW = Interconnections_RoW.reindex(self.idx_utc_noloc)

    def load_load_shedding(self):
        config = self.config
        # Load Shedding:
        self.LoadShedding = NodeBasedTable(config['LoadShedding'],self.idx_utc_noloc,config['countries'],tablename='LoadShedding',default=config['default']['LoadShedding'])
        self.CostLoadShedding = NodeBasedTable(config['CostLoadShedding'],self.idx_utc_noloc,config['countries'],tablename='CostLoadShedding',default=config['default']['CostLoadShedding'])

    def load_plants(self):
        config = self.config
        # Power plants:
        plants = pd.DataFrame()
        if os.path.isfile(config['PowerPlantData']):
            plants = load_csv(config['PowerPlantData'])
        elif '##' in config['PowerPlantData']:
            for c in config['countries']:
                path = config['PowerPlantData'].replace('##', str(c))
                tmp = load_csv(path)
                plants = plants.append(tmp, ignore_index=True)
        plants = plants[plants['Technology'] != 'Other']
        plants = plants[pd.notnull(plants['PowerCapacity'])]
        plants.index = range(len(plants))
        # Some columns can be in two format (absolute or per unit). If not specified, they are set to zero:
        for key in ['StartUpCost','NoLoadCost']:
            if key in plants:
                pass
            elif key+'_pu' in plants:
                plants[key] = plants[key+'_pu'] * plants['PowerCapacity']
            else:
                plants[key] = 0
        # check plant list:
        check_units(config, plants)
        # If not present, add the non-compulsory fields to the units table:
        for key in ['CHPPowerLossFactor','CHPPowerToHeat','CHPType','STOCapacity','STOSelfDischarge','STOMaxChargingPower','STOChargingEfficiency', 'CHPMaxHeat']:
            if key not in plants.columns:
                plants[key] = np.nan
        self.plants = plants
        self.plants_chp = plants[[str(x).lower() in commons['types_CHP'] for x in plants['CHPType']]] # Defining the CHPs
        plants_sto = self.plants[[u in self.commons['tech_storage'] for u in self.plants['Technology']]]
        check_sto(self.config, plants_sto)
        self.plants_sto = plants_sto


    def load_fuel_prices(self):
        # Fuel prices:
        fuels = ['PriceOfNuclear', 'PriceOfBlackCoal', 'PriceOfGas', 
        'PriceOfFuelOil', 'PriceOfBiomass', 'PriceOfCO2', 'PriceOfLignite', 
        'PriceOfPeat']

        FuelPrices = pd.DataFrame(columns=fuels, index=self.idx_utc_noloc)
        for fuel in fuels:
            if os.path.isfile(config[fuel]):
                tmp = load_csv(config[fuel], header=None, index_col=0, parse_dates=True)
                self.FuelPrices[fuel] = tmp[1][self.idx_utc_noloc].values
            elif isinstance(config['default'][fuel], (int, float, complex)):
                logging.warning('No data file found for "' + fuel + '. Using default value ' + str(self.config['default'][fuel]) + ' EUR')
                self.FuelPrices[fuel] = pd.Series(config['default'][fuel], index=self.idx_utc_noloc)
            # Special case for lignite and peat, for backward compatibility
            elif fuel == 'PriceOfLignite':
                logging.warning('No price data found for "' + fuel + '. Using the same value as for Black Coal')
                self.FuelPrices[fuel] = FuelPrices['PriceOfBlackCoal']
            elif fuel == 'PriceOfPeat':
                logging.warning('No price data found for "' + fuel + '. Using the same value as for biomass')
                self.FuelPrices[fuel] = FuelPrices['PriceOfBiomass']
            else:
                logging.warning('No data file or default value found for "' + fuel + '. Assuming zero marginal price!')
                self.FuelPrices[fuel] = pd.Series(0, index=self.idx_utc_noloc)


    def load_cep_parameters(self):
        all_cost = load_csv('Database/CapacityExpansion/techs_cost.csv')
        expandable_units = ['HRD-STUR', 'LIG-STUR', 'NUC-STUR','OIL-STUR', 'GAS-GTUR'] #TODO
        plant_new = load_csv('Database/CapacityExpansion/techs_cap.csv')
        plant_new = plant_new[plant_new.Unit.isin(expandable_units)]
        # create variables (cartesian product of tech x country)
        n_countries = len(config['countries'])
        n_technologies = plant_new.shape[0]
        plant_new = pd.concat([plant_new] * n_countries) # for each zone
        plant_new['Zone'] = np.repeat(config['countries'], n_technologies) # create zone column
        plant_new['Unit'] = plant_new.apply(lambda x:  x['Zone'] + "-" + x['Unit'], axis=1) # naming
        plant_new = plant_new.set_index('Unit', drop=False)
        
        ## Cost of new technologies
        index = plant_new[['Fuel', 'Technology']].reset_index().set_index('Unit', drop=False)
        Plants_merged = Plants_merged.merge(index[['Fuel', 'Technology']],  how='outer', on = ['Fuel', 'Technology'], 
            indicator=True).query('_merge == "left_only"')
        del Plants_merged['_merge']
        Plants_merged = Plants_merged.set_index('Unit', drop=False)
        Plants_merged = Plants_merged.append(plant_new)
        plant_new_cost = all_cost[all_cost.Unit.isin(expandable_units)]
        df_expanded = pd.merge(index, plant_new_cost, on=['Fuel', 'Technology'], how='left')


    def cluster_plants(self):
    
        # Clustering of the plants:
        Plants_merged, mapping = clustering(self.plants, method=config['SimulationType'])
        # Check clustering:
        check_clustering(plants, Plants_merged)
        self.plants = plants
        self.Plants_merged = Plants_merged

        
    def get_unit_based_tables(self):
        
        self.Outages = UnitBasedTable(plants,config['Outages'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Technology'],tablename='Outages')
        self.AF = UnitBasedTable(plants,config['RenewablesAF'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Technology'],tablename='AvailabilityFactors',default=1,RestrictWarning=commons['tech_renewables'])
        self.ReservoirLevels = UnitBasedTable(plants_sto,config['ReservoirLevels'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Technology','Zone'],tablename='ReservoirLevels',default=0)
        self.ReservoirScaledInflows = UnitBasedTable(plants_sto,config['ReservoirScaledInflows'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Technology','Zone'],tablename='ReservoirScaledInflows',default=0)
        self.HeatDemand = UnitBasedTable(plants_chp,config['HeatDemand'],idx_utc_noloc,config['countries'],fallbacks=['Unit'],tablename='HeatDemand',default=0)
        self.CostHeatSlack = UnitBasedTable(plants_chp,config['CostHeatSlack'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Zone'],tablename='CostHeatSlack',default=config['default']['CostHeatSlack'])
        check_AvailabilityFactors(self.plants, self.AF)
        check_heat_demand(self.plants, self.HeatDemand)



    def merge_time_series(self, mapping): 
        # Merging the time series relative to the clustered power plants:
        self.ReservoirScaledInflows_merged = merge_series(self.plants, self.ReservoirScaledInflows, mapping, method='WeightedAverage', tablename='ScaledInflows')
        self.ReservoirLevels_merged = merge_series(self.plants, self.ReservoirLevels, mapping, tablename='ReservoirLevels')
        self.Outages_merged = merge_series(self.plants, self.Outages, mapping, tablename='Outages')
        self.HeatDemand_merged = merge_series(self.plants, self.HeatDemand, mapping, tablename='HeatDemand',method='Sum')
        self.AF_merged = merge_series(self.plants, self.AF, mapping, tablename='AvailabilityFactors')
        self.CostHeatSlack_merged = merge_series(self.plants, self.CostHeatSlack, mapping, tablename='CostHeatSlack')


    def check_dfs(self): 
        first_hour_no_loc = self.idx_utc_noloc[0]
        last_hour_no_loc = self.idx_utc_noloc[-1],
        check_df(self.Load, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc, name='Load')
        check_df(self.AF_merged, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc,
                name='AF_merged')
        check_df(self.Outages_merged, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc, name='Outages_merged')
        check_df(self.Inter_RoW, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc, name='Inter_RoW')
        check_df(self.FuelPrices, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc, name='FuelPrices')
        check_df(self.NTCs, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc, name='NTCs')
        check_df(self.ReservoirLevels_merged, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc,
                name='ReservoirLevels_merged')
        check_df(self.ReservoirScaledInflows_merged, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc,
                name='ReservoirScaledInflows_merged')
        check_df(self.HeatDemand_merged, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc,
                name='HeatDemand_merged')
        check_df(self.CostHeatSlack_merged, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc,
                name='CostHeatSlack_merged')
        check_df(self.LoadShedding, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc,
                name='LoadShedding')
        check_df(self.CostLoadShedding, StartDate=first_hour_no_loc, StopDate=last_hour_no_loc,
                name='CostLoadShedding')


    def rename_plant_columns(self):
            # Renaming the columns to ease the production of parameters:
        self.Plants_merged.rename(columns={'StartUpCost': 'CostStartUp',
                                    'RampUpMax': 'RampUpMaximum',
                                    'RampDownMax': 'RampDownMaximum',
                                    'MinUpTime': 'TimeUpMinimum',
                                    'MinDownTime': 'TimeDownMinimum',
                                    'RampingCost': 'CostRampUp',
                                    'STOCapacity': 'StorageCapacity',
                                    'STOMaxChargingPower': 'StorageChargingCapacity',
                                    'STOChargingEfficiency': 'StorageChargingEfficiency',
                                    'STOSelfDischarge': 'StorageSelfDischarge',
                                    'CO2Intensity': 'EmissionRate'}, inplace=True)

    def extend(self):
        #todo testing
        attributes2extend = [
            'Load','AF_merged','Inter_RoW','NTCs','FuelPrices','Load','Outages_merged','ReservoirLevels_merged',
            'ReservoirScaledInflows_merged','LoadShedding','CostLoadShedding']
        map(attributes2extend, lambda x: setattr(self, x, getattr(x).reindex(idx_long, method='nearest').fillna(method='bfill')))
        

    def extend_data_with_lookahead(self):
        # Extending the data to include the look-ahead period (with constant values assumed)
        #TODO
        enddate_long = idx_utc_noloc[-1] + dt.timedelta(days=config['LookAhead'])
        idx_long = pd.DatetimeIndex(pd.date_range(start=idx_utc_noloc[0], end=enddate_long, freq=commons['TimeStep']))
        Nhours_long = len(idx_long)

        # re-indexing with the longer index and filling possibly missing data at the beginning and at the end::
        self.Load = self.Load.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.AF_merged = self.AF_merged.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.Inter_RoW = self.Inter_RoW.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.NTCs = self.NTCs.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.FuelPrices = self.FuelPrices.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.Load = self.Load.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.Outages_merged = self.Outages_merged.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.ReservoirLevels_merged = self.ReservoirLevels_merged.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.ReservoirScaledInflows_merged = self.ReservoirScaledInflows_merged.reindex(idx_long, method='nearest').fillna(
            method='bfill')
        self.LoadShedding = self.LoadShedding.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.CostLoadShedding = self.CostLoadShedding.reindex(idx_long, method='nearest').fillna(method='bfill')
        #    for tr in Renewables:
        #        Renewables[tr] = Renewables[tr].reindex(idx_long, method='nearest').fillna(method='bfill')


    def finish_preprocessing(self):

        Plants_merged = self.Plants_merged
        for key in ['TimeUpMinimum','TimeDownMinimum']:
            if any([not x.is_integer() for x in Plants_merged[key].fillna(0).values.astype('float')]):
                logging.warning(key + ' in the power plant data has been rounded to the nearest integer value')
                Plants_merged.loc[:,key] = Plants_merged[key].fillna(0).values.astype('int32')

            if not len(Plants_merged.index.unique()) == len(Plants_merged):
                # Very unlikely case:
                logging.error('plant indexes not unique!')
                sys.exit(1)

            # Apply scaling factors:
            if config['modifiers']['Solar'] != 1:
                logging.info('Scaling Solar Capacity by a factor ' + str(config['modifiers']['Solar']))
                for u in Plants_merged.index:
                    if Plants_merged.Technology[u] == 'PHOT':
                        Plants_merged.loc[u, 'PowerCapacity'] = Plants_merged.loc[u, 'PowerCapacity'] * config['modifiers']['Solar']
            if config['modifiers']['Wind'] != 1:
                logging.info('Scaling Wind Capacity by a factor ' + str(config['modifiers']['Wind']))
                for u in Plants_merged.index:
                    if Plants_merged.Technology[u] == 'WTON' or Plants_merged.Technology[u] == 'WTOF':
                        Plants_merged.loc[u, 'PowerCapacity'] = Plants_merged.loc[u, 'PowerCapacity'] * config['modifiers']['Wind']
            if config['modifiers']['Storage'] != 1:
                logging.info('Scaling Storage Power and Capacity by a factor ' + str(config['modifiers']['Storage']))
                for u in Plants_merged.index:
                    if isStorage(Plants_merged.Technology[u]):
                        Plants_merged.loc[u, 'PowerCapacity'] = Plants_merged.loc[u, 'PowerCapacity'] * config['modifiers']['Storage']
                        Plants_merged.loc[u, 'StorageCapacity'] = Plants_merged.loc[u, 'StorageCapacity'] * config['modifiers']['Storage']
                        Plants_merged.loc[u, 'StorageChargingCapacity'] = Plants_merged.loc[u, 'StorageChargingCapacity'] * config['modifiers']['Storage']

            # Defining the hydro storages:
            Plants_sto = Plants_merged[[u in commons['tech_storage'] for u in Plants_merged['Technology']]]
            # check storage plants:
            check_sto(config, Plants_sto,raw_data=False)
            # Defining the CHPs:
            Plants_chp = Plants_merged[[x.lower() in commons['types_CHP'] for x in Plants_merged['CHPType']]].copy()
            # check chp plants:
            check_chp(config, Plants_chp)
            # For all the chp plants correct the PowerCapacity, which is defined in cogeneration mode in the inputs and in power generation model in the optimization model
            for u in Plants_chp.index:
                PowerCapacity = Plants_chp.loc[u, 'PowerCapacity']

                if Plants_chp.loc[u,'CHPType'].lower() == 'p2h':
                    PurePowerCapacity = PowerCapacity
                else:
                    if pd.isnull(Plants_chp.loc[u,'CHPMaxHeat']):  # If maximum heat is not defined, then it is defined as the intersection between two lines
                        MaxHeat = PowerCapacity / Plants_chp.loc[u,'CHPPowerToHeat']
                        Plants_chp.loc[u, 'CHPMaxHeat'] = 'inf'
                    else:
                        MaxHeat = Plants_chp.loc[u, 'CHPMaxHeat']
                    PurePowerCapacity = PowerCapacity + Plants_chp.loc[u,'CHPPowerLossFactor'] * MaxHeat
                Plants_merged.loc[u,'PartLoadMin'] = Plants_merged.loc[u,'PartLoadMin'] * PowerCapacity / PurePowerCapacity  # FIXME: Is this correct?
                Plants_merged.loc[u,'PowerCapacity'] = PurePowerCapacity
                
            # Get the hydro time series corresponding to the original plant list: #FIXME Unused variable ?
            #StorageFormerIndexes = [s for s in plants.index if
            #                        plants['Technology'][s] in commons['tech_storage']]

            # Same with the CHPs:
            # Get the heat demand time series corresponding to the original plant list:
            CHPFormerIndexes = [s for s in plants.index if
                                    plants['CHPType'][s] in commons['types_CHP']]
            for s in CHPFormerIndexes:  # for all the old plant indexes
                # get the old plant name corresponding to s:
                oldname = plants['Unit'][s]
                # newname = mapping['NewIndex'][s] #FIXME Unused variable ?
                if oldname not in HeatDemand:
                    logging.warning('No heat demand profile found for CHP plant "' + str(oldname) + '". Assuming zero')
                    HeatDemand[oldname] = 0
                if oldname not in CostHeatSlack:
                    logging.warning('No heat cost profile found for CHP plant "' + str(oldname) + '". Assuming zero')
                    CostHeatSlack[oldname] = 0
        
            # merge the outages:
            for i in plants.index:  # for all the old plant indexes
                # get the old plant name corresponding to s:
                oldname = plants['Unit'][i]
                newname = mapping['NewIndex'][i]


    def data_to_pickle(self): 
        pass
        
    def data_from_pickle(self, path): 
        pass

    
def get_model_horizon(): pass

def load_model_data(): pass

def add_capacity_expansion(): pass

def prepare_model_formulation(): pass

def build_model(): pass

def write_to_dest_folder(): pass

def cluster_power_plants(): pass

def write_pickle(): pass

def write_gdx(): pass



class DispaModelFormulation(object):

    def __init__(self, config):

        self.LP = config['SimulationType'] == 'LP' or config['SimulationType'] == 'LP clustered'
        self.CEP = config['CEP'] == 1
        self.load_sets()
        self.parameters = load_params()

    def load_sets(self):
        sets = {}
        sets['h'] = [str(x + 1) for x in range(Nhours_long)]
        sets['z'] = [str(x + 1) for x in range(Nhours_long - config['LookAhead'] * 24)]
        sets['mk'] = ['DA', '2U', '2D']
        sets['n'] = config['countries']
        sets['u'] = Plants_merged.index.tolist()
        sets['l'] = Interconnections
        sets['f'] = commons['Fuels']
        sets['p'] = ['CO2']
        sets['s'] = Plants_sto.index.tolist()
        sets['chp'] = Plants_chp.index.tolist()
        sets['t'] = commons['Technologies']
        sets['tr'] = commons['tech_renewables']
        self.sets = sets 

    def load_params(): 
        sets_param = {}
        sets_param['AvailabilityFactor'] = ['u', 'h']
        sets_param['CHPPowerToHeat'] = ['chp']
        sets_param['CHPPowerLossFactor'] = ['chp']
        sets_param['CHPMaxHeat'] = ['chp']
        sets_param['CostFixed'] = ['u']
        sets_param['CostHeatSlack'] = ['chp','h']
        sets_param['CostLoadShedding'] = ['n','h']
        sets_param['CostRampUp'] = ['u']
        sets_param['CostRampDown'] = ['u']
        sets_param['CostShutDown'] = ['u']
        sets_param['CostStartUp'] = ['u']
        sets_param['CostVariable'] = ['u', 'h']
        sets_param['Curtailment'] = ['n']
        sets_param['Demand'] = ['mk', 'n', 'h']
        sets_param['Efficiency'] = ['u']
        sets_param['EmissionMaximum'] = ['n', 'p']
        sets_param['EmissionRate'] = ['u', 'p']
        sets_param['FlowMaximum'] = ['l', 'h']
        sets_param['FlowMinimum'] = ['l', 'h']
        sets_param['Fuel'] = ['u', 'f']
        sets_param['HeatDemand'] = ['chp','h']
        sets_param['LineNode'] = ['l', 'n']
        sets_param['LoadShedding'] = ['n','h']
        sets_param['Location'] = ['u', 'n']
        sets_param['Markup'] = ['u', 'h']
        sets_param['Nunits'] = ['u']
        sets_param['OutageFactor'] = ['u', 'h']
        sets_param['PartLoadMin'] = ['u']
        sets_param['PowerCapacity'] = ['u']
        sets_param['PowerInitial'] = ['u']
        sets_param['PriceTransmission'] = ['l', 'h']
        sets_param['RampUpMaximum'] = ['u']
        sets_param['RampDownMaximum'] = ['u']
        sets_param['RampStartUpMaximum'] = ['u']
        sets_param['RampShutDownMaximum'] = ['u']
        sets_param['Reserve'] = ['t']
        sets_param['StorageCapacity'] = ['u']
        sets_param['StorageChargingCapacity'] = ['s']
        sets_param['StorageChargingEfficiency'] = ['s']
        sets_param['StorageDischargeEfficiency'] = ['s']
        sets_param['StorageSelfDischarge'] = ['u']
        sets_param['StorageInflow'] = ['s', 'h']
        sets_param['StorageInitial'] = ['s']
        sets_param['StorageMinimum'] = ['s']
        sets_param['StorageOutflow'] = ['s', 'h']
        sets_param['StorageProfile'] = ['s', 'h']
        sets_param['Technology'] = ['u', 't']
        sets_param['TimeUpMinimum'] = ['u']
        sets_param['TimeDowninimum'] = ['u']
        return sets_param

    def __build_parameters(self):
        parameters=dict()

        sets_param = self.sets_param
        Plants_merged = self.Plants_merged
        Plants_sto = self.Plants_sto
        Plants_chp = self.Plants_chp

        
        # Define all the parameters and set a default value of zero:
        for var in sets_param:
            parameters[var] = define_parameter(sets_param[var], sets, value=0)
        
        for var in ["Investment", "EconomicLifetime"]:
            parameters[var] = define_parameter(sets_param[var], sets, value=0)
            if CEP:
                parameters[var]["val"] =  df_expanded[var].values

        Plants_merged['FixedCost'] = pd.merge(Plants_merged, all_cost, how='left', on=['Fuel', 'Technology'])['FixedCost'].values
        Nunits = len(Plants_merged)

        for var in ["CostFixed"]:
            sets_param[var] = ['u']
            parameters[var] = define_parameter(sets_param[var], sets, value=0)
            parameters[var]["val"] =  Plants_merged['FixedCost'].values


        # List of parameters whose default value is 1
        for var in ['AvailabilityFactor', 'Efficiency', 'Curtailment', 'StorageChargingEfficiency',
                    'StorageDischargeEfficiency', 'Nunits']:
            parameters[var] = define_parameter(sets_param[var], sets, value=1)

        # List of parameters whose default value is very high
        for var in ['RampUpMaximum', 'RampDownMaximum', 'RampStartUpMaximum', 'RampShutDownMaximum',
                    'EmissionMaximum']:
            parameters[var] = define_parameter(sets_param[var], sets, value=1e7)

        # Boolean parameters:
        for var in ['Technology', 'Fuel', 'Reserve', 'Location']:
            parameters[var] = define_parameter(sets_param[var], sets, value='bool')

        # %%
        # List of parameters whose value is known, and provided in the dataframe Plants_merged.
        for var in ['Efficiency', 'PowerCapacity', 'PartLoadMin', 'TimeUpMinimum', 'TimeDownMinimum', 'CostStartUp',
                    'CostRampUp','StorageCapacity', 'StorageSelfDischarge']:
            parameters[var]['val'] = Plants_merged[var].values

        # List of parameters whose value is not necessarily specified in the dataframe Plants_merged
        for var in ['Nunits']:
            if var in Plants_merged:
                parameters[var]['val'] = Plants_merged[var].values


        # List of parameters whose value is known, and provided in the dataframe Plants_sto.
        for var in ['StorageChargingCapacity', 'StorageChargingEfficiency']:
            parameters[var]['val'] = Plants_sto[var].values

        # The storage discharge efficiency is actually given by the unit efficiency:
        parameters['StorageDischargeEfficiency']['val'] = Plants_sto['Efficiency'].values
        
        # List of parameters whose value is known, and provided in the dataframe Plants_chp
        for var in ['CHPPowerToHeat','CHPPowerLossFactor', 'CHPMaxHeat']:
            parameters[var]['val'] = Plants_chp[var].values

        # Storage profile and initial state:
        for i, s in enumerate(sets['s']):
            if s in ReservoirLevels_merged:
                # get the time
                parameters['StorageInitial']['val'][i] = ReservoirLevels_merged[s][idx_long[0]] * \
                                                        Plants_sto['StorageCapacity'][s] * Plants_sto['Nunits'][s]
                parameters['StorageProfile']['val'][i, :] = ReservoirLevels_merged[s][idx_long].values
                if any(ReservoirLevels_merged[s] > 1):
                    logging.warning(s + ': The reservoir level is sometimes higher than its capacity!')
            else:
                logging.warning( 'Could not find reservoir level data for storage plant ' + s + '. Assuming 50% of capacity')
                parameters['StorageInitial']['val'][i] = 0.5 * Plants_sto['StorageCapacity'][s]
                parameters['StorageProfile']['val'][i, :] = 0.5

        # Storage Inflows:
        for i, s in enumerate(sets['s']):
            if s in ReservoirScaledInflows_merged:
                parameters['StorageInflow']['val'][i, :] = ReservoirScaledInflows_merged[s][idx_long].values * \
                                                        Plants_sto['PowerCapacity'][s]
        # CHP time series:
        for i, u in enumerate(sets['chp']):
            if u in HeatDemand_merged:
                parameters['HeatDemand']['val'][i, :] = HeatDemand_merged[u][idx_long].values
                parameters['CostHeatSlack']['val'][i, :] = CostHeatSlack_merged[u][idx_long].values

        # Ramping rates are reconstructed for the non dimensional value provided (start-up and normal ramping are not differentiated)
        parameters['RampUpMaximum']['val'] = Plants_merged['RampUpRate'].values * Plants_merged['PowerCapacity'].values * 60
        parameters['RampDownMaximum']['val'] = Plants_merged['RampDownRate'].values * Plants_merged[
            'PowerCapacity'].values * 60
        parameters['RampStartUpMaximum']['val'] = Plants_merged['RampUpRate'].values * Plants_merged[
            'PowerCapacity'].values * 60
        parameters['RampShutDownMaximum']['val'] = Plants_merged['RampDownRate'].values * Plants_merged[
            'PowerCapacity'].values * 60

        # If Curtailment is not allowed, set to 0:
        if config['AllowCurtailment'] == 0:
            parameters['Curtailment'] = define_parameter(sets_param['Curtailment'], sets, value=0)

        # Availability Factors
        if len(AF_merged.columns) != 0:
            for i, u in enumerate(sets['u']):
                if u in AF_merged.columns:
                    parameters['AvailabilityFactor']['val'][i, :] = AF_merged[u].values


        # Demand
        # Dayahead['NL'][1800:1896] = Dayahead['NL'][1632:1728]
        reserve_2U_tot = {i: (np.sqrt(10 * PeakLoad[i] + 150 ** 2) - 150) for i in Load.columns}
        reserve_2D_tot = {i: (0.5 * reserve_2U_tot[i]) for i in Load.columns}

        values = np.ndarray([len(sets['mk']), len(sets['n']), len(sets['h'])])
        for i in range(len(sets['n'])):
            values[0, i, :] = Load[sets['n'][i]]
            values[1, i, :] = reserve_2U_tot[sets['n'][i]]
            values[2, i, :] = reserve_2D_tot[sets['n'][i]]
        
        parameters['Demand'] = {'sets': sets_param['Demand'], 'val': values}
        # Emission Rate:
        parameters['EmissionRate']['val'][:, 0] = Plants_merged['EmissionRate'].values

        # Load Shedding:
        for i, c in enumerate(sets['n']):
            parameters['LoadShedding']['val'][i] = LoadShedding[c] * PeakLoad[c]
            parameters['CostLoadShedding']['val'][i] = CostLoadShedding[c]

        # %%#################################################################################################################################################################################################
        # Variable Cost
        # Equivalence dictionary between fuel types and price entries in the config sheet:
        FuelEntries = {'BIO':'PriceOfBiomass', 'GAS':'PriceOfGas', 'HRD':'PriceOfBlackCoal', 'LIG':'PriceOfLignite', 'NUC':'PriceOfNuclear', 'OIL':'PriceOfFuelOil', 'PEA':'PriceOfPeat'}
        for unit in range(Nunits):
            found = False
            for FuelEntry in FuelEntries:
                if Plants_merged['Fuel'][unit] == FuelEntry:
                    parameters['CostVariable']['val'][unit, :] = FuelPrices[FuelEntries[FuelEntry]] / Plants_merged['Efficiency'][unit] + \
                                                                Plants_merged['EmissionRate'][unit] * FuelPrices['PriceOfCO2']
                    found = True
            # Special case for biomass plants, which are not included in EU ETS:
            if Plants_merged['Fuel'][unit] == 'BIO':
                parameters['CostVariable']['val'][unit, :] = FuelPrices['PriceOfBiomass'] / Plants_merged['Efficiency'][
                    unit]
                found = True
            if not found:
                logging.warning('No fuel price value has been found for fuel ' + Plants_merged['Fuel'][unit] + ' in unit ' + \
                    Plants_merged['Unit'][unit] + '. A null variable cost has been assigned')

        # %%#################################################################################################################################################################################################

        # Maximum Line Capacity
        for i, l in enumerate(sets['l']):
            if l in NTCs.columns:
                parameters['FlowMaximum']['val'][i, :] = NTCs[l]
            if l in Inter_RoW.columns:
                parameters['FlowMaximum']['val'][i, :] = Inter_RoW[l]
                parameters['FlowMinimum']['val'][i, :] = Inter_RoW[l]
        # Check values:
        check_MinMaxFlows(parameters['FlowMinimum']['val'],parameters['FlowMaximum']['val'])
        
        parameters['LineNode'] = incidence_matrix(sets, 'l', parameters, 'LineNode')

        # Outage Factors
        if len(Outages_merged.columns) != 0:
            for i, u in enumerate(sets['u']):
                if u in Outages_merged.columns:
                    parameters['OutageFactor']['val'][i, :] = Outages_merged[u].values
                else:
                    logging.warning('Outages factors not found for unit ' + u + '. Assuming no outages')

        # Participation to the reserve market
        values = np.array([s in config['ReserveParticipation'] for s in sets['t']], dtype='bool')
        parameters['Reserve'] = {'sets': sets_param['Reserve'], 'val': values}

        # Technologies
        for unit in range(Nunits):
            idx = sets['t'].index(Plants_merged['Technology'][unit])
            parameters['Technology']['val'][unit, idx] = True

        # Fuels
        for unit in range(Nunits):
            idx = sets['f'].index(Plants_merged['Fuel'][unit])
            parameters['Fuel']['val'][unit, idx] = True

        # Location
        for i in range(len(sets['n'])):
            parameters['Location']['val'][:, i] = (Plants_merged['Zone'] == config['countries'][i]).values

        # CHPType parameter:
        sets['chp_type'] = ['Extraction','Back-Pressure', 'P2H']
        parameters['CHPType'] = define_parameter(['chp','chp_type'],sets,value=0)
        for i,u in enumerate(sets['chp']):
            if u in Plants_chp.index:
                if Plants_chp.loc[u,'CHPType'].lower() == 'extraction':
                    parameters['CHPType']['val'][i,0] = 1
                elif Plants_chp.loc[u,'CHPType'].lower() == 'back-pressure':
                    parameters['CHPType']['val'][i,1] = 1
                elif Plants_chp.loc[u,'CHPType'].lower() == 'p2h':
                    parameters['CHPType']['val'][i,2] = 1
                else:
                    logging.error('CHPType not valid for plant ' + u)
                    sys.exit(1)

        # Initial Power
        if 'InitialPower' in Plants_merged:
            parameters['PowerInitial']['val'] = Plants_merged['InitialPower'].values
        else:
            for i in range(Nunits):
                # Nuclear and Fossil Gas greater than 350 MW are up (assumption):
                if Plants_merged['Fuel'][i] in ['GAS', 'NUC'] and Plants_merged['PowerCapacity'][i] > 350:
                    parameters['PowerInitial']['val'][i] = (Plants_merged['PartLoadMin'][i] + 1) / 2 * \
                                                        Plants_merged['PowerCapacity'][i]
                # Config variables:
        sets['x_config'] = ['FirstDay', 'LastDay', 'RollingHorizon Length', 'RollingHorizon LookAhead','ValueOfLostLoad','QuickStartShare','CostOfSpillage','WaterValue']
        sets['y_config'] = ['year', 'month', 'day', 'val']
        dd_begin = idx_long[4]
        dd_end = idx_long[-2]

    #TODO: integrated the parameters (VOLL, Water value, etc) from the excel config file
        values = np.array([
            [dd_begin.year, dd_begin.month, dd_begin.day, 0],
            [dd_end.year, dd_end.month, dd_end.day, 0],
            [0, 0, config['HorizonLength'], 0],
            [0, 0, config['LookAhead'], 0],
            [0, 0, 0, 1e5],     # Value of lost load
            [0, 0, 0, 0.5],       # allowed Share of quick start units in reserve
            [0, 0, 0, 1],       # Cost of spillage (EUR/MWh)
            [0, 0, 0, 100],       # Value of water (for unsatisfied water reservoir levels, EUR/MWh)
        ])
        parameters['Config'] = {'sets': ['x_config', 'y_config'], 'val': values}

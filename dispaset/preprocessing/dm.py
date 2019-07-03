# -*- coding: utf-8 -*-
"""
This is the main file of the DispaSET pre-processing tool. It comprises a single function that generated the DispaSET simulation environment.

@author: S. Quoilin, edited by M. Zech
"""

#todo check indices

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


GMS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'GAMS')

# TODO Move to utils
def get_git_revision_tag():
    """Get version of DispaSET used for this run. tag + commit hash"""
    from subprocess import check_output
    try:
        return check_output(["git", "describe", "--tags", "--always"]).strip()
    except:
        return 'NA'

def build_simulation(config):
    dm = DispaModel(config)
    dm.build_model_parameters()
    return dm.build_sim_dir()


def get_indices(config):
    # Indexes of the simulation:
    idx_std = pd.DatetimeIndex(pd.date_range(start=pd.datetime(*config['StartDate']),
                                            end=pd.datetime(*config['StopDate']),
                                            freq=commons['TimeStep'])
                            ) #todo check brackets on master

    idx_utc_noloc = idx_std - dt.timedelta(hours=1)
    idx_utc = idx_utc_noloc.tz_localize('UTC')
    # Indexes for the whole year considered in StartDate
    idx_utc_year_noloc = pd.DatetimeIndex(pd.date_range(start=pd.datetime(*(config['StartDate'][0],1,1,0,0)),
                                                        end=pd.datetime(*(config['StartDate'][0],12,31,23,59,59)),
                                                        freq=commons['TimeStep'])
                                        )
    return idx_utc, idx_utc_noloc, idx_utc_year_noloc

def _define_default_values(config):
    if not isinstance(config['default']['CostLoadShedding'],(float,int)):
        config['default']['CostLoadShedding'] = 1000
    if not isinstance(config['default']['CostHeatSlack'],(float,int)):
        config['default']['CostHeatSlack'] = 50


class DispaModel(object):
    """
    Usage: DispaModel(config_dict) or by building the dictionaries through DispaModel.from_excel(), DispaModel.from_yaml()
    
    """
    def __init__(self, config): # TODO constructor
        if type(config) != dict:
            raise TypeError("Either pass a dictionary or use the loader functions DispaModel.from_excel(), DispaModel.from_yaml()")
        self.config = config
        _define_default_values(self.config)

        self.LP = config['SimulationType'] == 'LP' or config['SimulationType'] == 'LP clustered'
        self.CEP = config['CEP'] == 1
        self.data = DataLoader(config)

        # load sets
        self.idx_utc, self.idx_utc_noloc, self.idx_utc_year_noloc = get_indices(self.config) #todo do i really need you all?
        enddate_long = self.idx_utc_noloc[-1] + dt.timedelta(days=config['LookAhead'])
        self.idx_long = pd.DatetimeIndex(pd.date_range(start=self.idx_utc_noloc[0], end=enddate_long, freq=commons['TimeStep']))
        
        self.sets = load_sets(
            # todo create model object
            Nhours_long = len(self.idx_long), 
            look_ahead = self.data.config['LookAhead'], 
            plants_index = self.data.Plants_merged.index.tolist(),
            plants_sto_index = self.data.plants_sto.index.tolist(), 
            Plants_chp_index = self.data.plants_sto.index.tolist(), 
            countries = self.data.config['countries'], 
            Interconnections = self.data.Interconnections,
            plants_uc = self.data.plants_expanded.index.tolist()
        )

        self.sets_param = load_params() # the parameters with their formal structure without data
        self.version = str(get_git_revision_tag())
        self.time_range = (self.idx_utc[-1] - self.idx_utc[0]).days 
        self.sim = config['SimulationDirectory']
        self.dispa_version = str(get_git_revision_tag())
        self.SimData = {'sets': self.sets, 'parameters': self.sets_param, 'config': self.config, 'units': self.data.Plants_merged, 'version': self.dispa_version}

    @classmethod
    def from_excel(cls, excel_path):
        dict_ = load_config_excel(excel_path)
        return cls(dict_)

    @classmethod
    def from_yaml(cls, yaml_path):
        dict_ = load_config_yaml(yaml_path)
        return cls(dict_)

    def __str__(self):
        """Return a descriptive string for this instance, invoked by print() and str()"""
        no_days = (self.idx_utc[-1] - self.idx_utc[0]).days 
        no_plants = self.data.plants.shape[0]
        return ('Dispa-SET model with: \
                \n -> Simulationtype: %s \
                \n -> CEP: %r \
                \n -> LP: %r \
                \n -> %s to %s \
                \n -> %i days  \
                \n -> %i plants' % \
             (self.config['SimulationType'], self.LP, self.CEP, str(self.idx_utc_noloc[0]), str(self.idx_utc_noloc[-1]), no_days, no_plants))

    __repr__ = __str__ # pretty printing for usage in jupyter notebooks & print

    def edit_config(self, key, new_value): #TODO

        try:
            self.config[key] = new_value
        except KeyError as e: 
            print("Key not found")

    def build_model_parameters(self):
        parameters=dict()
        sets = self.sets
        sets_param = self.sets_param
        plants = self.data.plants
        Plants_merged = self.data.Plants_merged
        Plants_sto = self.data.plants_sto
        Plants_chp = self.data.plants_chp
        ReservoirLevels = self.data.ReservoirLevels
        
        idx_long = self.idx_long
        config = self.data.config
        
        # Define all the parameters and set a default value of zero:
        for var in sets_param:
            parameters[var] = define_parameter(sets_param[var], sets, value=0)
        
        for var in ["Investment", "EconomicLifetime"]:
            parameters[var] = define_parameter(sets_param[var], sets, value=0)
            if self.CEP & len(sets["uc"]) > 0: # ! serious todo
                parameters[var]["val"] =  self.data.plants_expanded[var].values
                Plants_merged['FixedCost'] = pd.merge(Plants_merged, self.data.all_cost, how='left', on=['Fuel', 'Technology'])['FixedCost'].values
                for var in ["CostFixed"]:
                    sets_param[var] = ['u']
                    parameters[var] = define_parameter(sets_param[var], sets, value=0)
                    parameters[var]["val"] =  Plants_merged['FixedCost'].values
        
        Nunits = len(Plants_merged)

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
            if s in ReservoirLevels:
                # get the time
                parameters['StorageInitial']['val'][i] = ReservoirLevels[s][idx_long[0]] * \
                                                        Plants_sto['StorageCapacity'][s] * Plants_sto['Nunits'][s]
                parameters['StorageProfile']['val'][i, :] = ReservoirLevels[s][idx_long].values
                if any(ReservoirLevels[s] > 1):
                    logging.warning(s + ': The reservoir level is sometimes higher than its capacity!')
            else:
                logging.warning( 'Could not find reservoir level data for storage plant ' + s + '. Assuming 50% of capacity')
                parameters['StorageInitial']['val'][i] = 0.5 * Plants_sto['StorageCapacity'][s]
                parameters['StorageProfile']['val'][i, :] = 0.5

        # Storage Inflows:
        for i, s in enumerate(sets['s']):
            if s in self.data.ReservoirScaledInflows:
                parameters['StorageInflow']['val'][i, :] = self.data.ReservoirScaledInflows[s][idx_long].values * \
                                                        Plants_sto['PowerCapacity'][s]
        # CHP time series:
        for i, u in enumerate(sets['chp']):
            if u in self.data.HeatDemand:
                parameters['HeatDemand']['val'][i, :] = self.data.HeatDemand[u][idx_long].values
                parameters['CostHeatSlack']['val'][i, :] = self.data.CostHeatSlack[u][idx_long].values

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
        if len(self.data.AF.columns) != 0:
            for i, u in enumerate(sets['u']):
                if u in self.data.AF.columns:
                    parameters['AvailabilityFactor']['val'][i, :] = self.data.AF[u].values

        # Demand
        # Dayahead['NL'][1800:1896] = Dayahead['NL'][1632:1728]
        reserve_2U_tot = {i: (np.sqrt(10 * self.data.PeakLoad[i] + 150 ** 2) - 150) for i in self.data.Load.columns}
        reserve_2D_tot = {i: (0.5 * reserve_2U_tot[i]) for i in self.data.Load.columns}

        values = np.ndarray([len(sets['mk']), len(sets['n']), len(sets['h'])])
        for i in range(len(sets['n'])):
            values[0, i, :] = self.data.Load[sets['n'][i]]
            values[1, i, :] = reserve_2U_tot[sets['n'][i]]
            values[2, i, :] = reserve_2D_tot[sets['n'][i]]
        
        parameters['Demand'] = {'sets': sets_param['Demand'], 'val': values}
        # Emission Rate:
        parameters['EmissionRate']['val'][:, 0] = Plants_merged['EmissionRate'].values

        # Load Shedding:
        for i, c in enumerate(sets['n']):
            parameters['LoadShedding']['val'][i] = self.data.LoadShedding[c] * self.data.PeakLoad[c]
            parameters['CostLoadShedding']['val'][i] = self.data.CostLoadShedding[c]

        # %%#################################################################################################################################################################################################
        # Variable Cost
        # Equivalence dictionary between fuel types and price entries in the config sheet:
        FuelEntries = {'BIO':'PriceOfBiomass', 'GAS':'PriceOfGas', 'HRD':'PriceOfBlackCoal', 'LIG':'PriceOfLignite', 'NUC':'PriceOfNuclear', 'OIL':'PriceOfFuelOil', 'PEA':'PriceOfPeat'}
        for unit in range(Nunits):
            found = False
            for FuelEntry in FuelEntries:
                if Plants_merged['Fuel'][unit] == FuelEntry:
                    parameters['CostVariable']['val'][unit, :] = self.data.FuelPrices[FuelEntries[FuelEntry]] / Plants_merged['Efficiency'][unit] + \
                                                                Plants_merged['EmissionRate'][unit] * self.data.FuelPrices['PriceOfCO2']
                    found = True
            # Special case for biomass plants, which are not included in EU ETS:
            if Plants_merged['Fuel'][unit] == 'BIO':
                parameters['CostVariable']['val'][unit, :] = self.data.FuelPrices['PriceOfBiomass'] / Plants_merged['Efficiency'][
                    unit]
                found = True
            if not found:
                logging.warning('No fuel price value has been found for fuel ' + Plants_merged['Fuel'][unit] + ' in unit ' + \
                    Plants_merged['Unit'][unit] + '. A null variable cost has been assigned')

        # %%#################################################################################################################################################################################################

        # Maximum Line Capacity
        for i, l in enumerate(sets['l']):
            if l in self.data.NTCs.columns:
                parameters['FlowMaximum']['val'][i, :] = self.data.NTCs[l]
            if l in self.data.Inter_RoW.columns:
                parameters['FlowMaximum']['val'][i, :] = self.data.Inter_RoW[l]
                parameters['FlowMinimum']['val'][i, :] = self.data.Inter_RoW[l]
        # Check values:
        check_MinMaxFlows(parameters['FlowMinimum']['val'], parameters['FlowMaximum']['val'])
        parameters['LineNode'] = incidence_matrix(sets, 'l', parameters, 'LineNode')

        # Outage Factors
        if len(self.data.Outages.columns) != 0:
            for i, u in enumerate(sets['u']):
                if u in self.data.Outages.columns:
                    parameters['OutageFactor']['val'][i, :] = self.data.Outages[u].values
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
        self.parameters = parameters

    def build_sim_dir(self):

        config = self.config
        gdx_out = "Inputs.gdx"
        sim = self.sim

        #print(self.parameters)

        if config['WriteGDX']:
            write_variables(config['GAMS_folder'], gdx_out, [self.sets, self.parameters])

        # if the sim variable was not defined:
        if 'sim' not in locals():
            logging.error('Please provide a path where to store the DispaSET inputs (in the "sim" variable)')
            sys.exit(1)

        if not os.path.exists(sim):
            os.makedirs(sim)

        def replace_text_by_dict(text, dic):
            """Replace dictionary items in text"""
            for i, j in dic.items():
                text = text.replace(i, j)
            return text
        
        gams_file_changes = {'LP':self.LP, 'CEP':self.CEP}
        changes_infile_string = {'LP': ('$setglobal LPFormulation 0','$setglobal LPFormulation 1'), 'CEP': ('$setglobal CEPFormulation 0', '$setglobal CEPFormulation 1')}
        gams_file_changes_list = {changes_infile_string[k][0]: changes_infile_string[k][1] for k,v in gams_file_changes.items() if v == True}  #filter based on selection
        if len(gams_file_changes_list)>0:
            fin = open(os.path.join(GMS_FOLDER, 'UCM_h.gms'))
            fout = open(os.path.join(sim,'UCM_h.gms'), "wt")
            for line in fin:
                fout.write(replace_text_by_dict(line, gams_file_changes_list))
            fin.close()
            fout.close()
        else:
            shutil.copyfile(os.path.join(GMS_FOLDER, 'UCM_h.gms'),
                            os.path.join(sim, 'UCM_h.gms'))

        gmsfile = open(os.path.join(sim, 'UCM.gpr'), 'w')
        gmsfile.write(
            '[PROJECT] \n \n[RP:UCM_H] \n1= \n[OPENWINDOW_1] \nFILE0=UCM_h.gms \nFILE1=UCM_h.gms \nMAXIM=1 \nTOP=50 \nLEFT=50 \nHEIGHT=400 \nWIDTH=400')
        gmsfile.close()
        shutil.copyfile(os.path.join(GMS_FOLDER, 'writeresults.gms'),
                        os.path.join(sim, 'writeresults.gms'))
        # Create cplex option file
        cplex_options = {'epgap': 0.05, # TODO: For the moment hardcoded, it has to be moved to a config file
                        'numericalemphasis': 0,
                        'scaind': 1,
                        'lpmethod': 0,
                        'relaxfixedinfeas': 0,
                        'mipstart':1,
                        'epint':0}

        lines_to_write = ['{} {}'.format(k, v) for k, v in cplex_options.items()]
        with open(os.path.join(sim, 'cplex.opt'), 'w') as f:
            for line in lines_to_write:
                f.write(line + '\n')

        logging.debug('Using gams file from ' + GMS_FOLDER)
        if config['WriteGDX']:
            shutil.copy(gdx_out, sim + '/')
            os.remove(gdx_out)
        # Copy bat file to generate gdx file directly from excel:
        shutil.copy(os.path.join(GMS_FOLDER, 'makeGDX.bat'),
                    os.path.join(sim, 'makeGDX.bat'))

        if config['WriteExcel']:
            write_to_excel(sim, [sets, parameters])

        if config['WritePickle']:
            try:
                import cPickle as pickle
            except ImportError:
                import pickle
            with open(os.path.join(sim, 'Inputs.p'), 'wb') as pfile:
                pickle.dump(SimData, pfile, protocol=pickle.HIGHEST_PROTOCOL)
        logging.info('Build finished')
        
        if os.path.isfile(commons['logfile']):
            shutil.copy(commons['logfile'], os.path.join(sim, 'warn_preprocessing.log'))
        return SimData


def load_loads(config, idx_utc_noloc, idx_utc_year_noloc):

    # Load :
    Load = NodeBasedTable(config['Demand'],idx_utc_noloc,config['countries'],tablename='Demand')
    # For the peak load, the whole year is considered:
    PeakLoad = NodeBasedTable(config['Demand'],idx_utc_year_noloc,config['countries'],tablename='PeakLoad').max()
    if config['modifiers']['Demand'] != 1:
        logging.info('Scaling load curve by a factor ' + str(config['modifiers']['Demand']))
        Load = Load * config['modifiers']['Demand']
        PeakLoad = PeakLoad * config['modifiers']['Demand']
    return Load, PeakLoad

def load_interconnections(config, idx_utc_noloc):
    
    # Interconnections:
    if os.path.isfile(config['Interconnections']):
        flows = load_csv(config['Interconnections'], index_col=0, parse_dates=True).fillna(0)
    else:
        logging.warning('No historical flows will be considered (no valid file provided)')
        flows = pd.DataFrame(index=idx_utc_noloc)
    if os.path.isfile(config['NTC']):
        NTC = load_csv(config['NTC'], index_col=0, parse_dates=True).fillna(0)
    else:
        logging.warning('No NTC values will be considered (no valid file provided)')
        NTC = pd.DataFrame(index=idx_utc_noloc)

    # Interconnections:
    [Interconnections_sim, Interconnections_RoW, Interconnections] = interconnections(config['countries'], NTC, flows)

    if len(Interconnections_sim.columns) > 0:
        NTCs = Interconnections_sim.reindex(idx_utc_noloc)
    else:
        NTCs = pd.DataFrame(index=idx_utc_noloc)
    Inter_RoW = Interconnections_RoW.reindex(idx_utc_noloc)
    return flows, NTC, Interconnections, NTCs, Inter_RoW

def load_load_shedding(config, idx_utc_noloc):
    # Load Shedding:
    LoadShedding = NodeBasedTable(config['LoadShedding'],idx_utc_noloc,config['countries'],tablename='LoadShedding',default=config['default']['LoadShedding'])
    CostLoadShedding = NodeBasedTable(config['CostLoadShedding'],idx_utc_noloc,config['countries'],tablename='CostLoadShedding',default=config['default']['CostLoadShedding'])
    return LoadShedding, CostLoadShedding

def load_fuel_prices(config, idx_utc_noloc):

    # Fuel prices:
    fuels = ['PriceOfNuclear', 'PriceOfBlackCoal', 'PriceOfGas', 'PriceOfFuelOil', 'PriceOfBiomass', 'PriceOfCO2', 'PriceOfLignite', 'PriceOfPeat']
    FuelPrices = pd.DataFrame(columns=fuels, index=idx_utc_noloc)
    for fuel in fuels:
        if os.path.isfile(config[fuel]):
            tmp = load_csv(config[fuel], header=None, index_col=0, parse_dates=True)
            FuelPrices[fuel] = tmp[1][idx_utc_noloc].values
        elif isinstance(config['default'][fuel], (int, float, complex)):
            logging.warning('No data file found for "' + fuel + '. Using default value ' + str(config['default'][fuel]) + ' EUR')
            FuelPrices[fuel] = pd.Series(config['default'][fuel], index=idx_utc_noloc)
        # Special case for lignite and peat, for backward compatibility
        elif fuel == 'PriceOfLignite':
            logging.warning('No price data found for "' + fuel + '. Using the same value as for Black Coal')
            FuelPrices[fuel] = FuelPrices['PriceOfBlackCoal']
        elif fuel == 'PriceOfPeat':
            logging.warning('No price data found for "' + fuel + '. Using the same value as for biomass')
            FuelPrices[fuel] = FuelPrices['PriceOfBiomass']
        else:
            logging.warning('No data file or default value found for "' + fuel + '. Assuming zero marginal price!')
            FuelPrices[fuel] = pd.Series(0, index=idx_utc_noloc)
    return FuelPrices


#todo NOT ACTIVE
def add_cap_expansion_cart_prod():
    return None
    logging.info("Capacity Expansion used!")
    all_cost = load_csv('Database/CapacityExpansion/techs_cost.csv') #TODO
    expandable_units = ['HRD-STUR', 'LIG-STUR', 'NUC-STUR','OIL-STUR', 'GAS-GTUR'] #TODO
    plant_new = load_csv('Database/CapacityExpansion/techs_cap.csv') #TODO
    plant_new = plant_new[plant_new.Unit.isin(expandable_units)]
    # create variables (cartesian product of tech x country)
    n_countries = len(config['countries'])
    n_technologies = plant_new.shape[0]
    plant_new = pd.concat([plant_new] * n_countries) # for each zone create new uc
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
    return df_expanded

def load_cep_parameters(config, Plants_merged):
    
    df_cap = Plants_merged[Plants_merged['ExtendableCapacity']>0] #todo put into csv sheets
    techs_cost = load_csv(config["CapCosts"]) 
    if df_cap.shape[0] > 0: #any extendable power plant technology
        logging.info("Capacity Expansion used!")
        df_expanded = df_cap[:]
    else: 
        df_expanded = pd.DataFrame() # empty dataframe -> empty set

    return df_expanded, techs_cost

def cluster_plants(config, plants):

    # Clustering of the plants:
    Plants_merged, mapping = clustering(plants, method=config['SimulationType'])
    # Check clustering:
    check_clustering(plants, Plants_merged)
    return Plants_merged, mapping
    
def get_unit_based_tables(idx_utc_noloc, config, plants, plants_sto, plants_chp):
    
    Outages = UnitBasedTable(plants,config['Outages'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Technology'],tablename='Outages')
    AF = UnitBasedTable(plants,config['RenewablesAF'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Technology'],tablename='AvailabilityFactors',default=1,RestrictWarning=commons['tech_renewables'])
    ReservoirLevels = UnitBasedTable(plants_sto,config['ReservoirLevels'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Technology','Zone'],tablename='ReservoirLevels',default=0)
    ReservoirScaledInflows = UnitBasedTable(plants_sto,config['ReservoirScaledInflows'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Technology','Zone'],tablename='ReservoirScaledInflows',default=0)
    HeatDemand = UnitBasedTable(plants_chp,config['HeatDemand'],idx_utc_noloc,config['countries'],fallbacks=['Unit'],tablename='HeatDemand',default=0)
    CostHeatSlack = UnitBasedTable(plants_chp,config['CostHeatSlack'],idx_utc_noloc,config['countries'],fallbacks=['Unit','Zone'],tablename='CostHeatSlack',default=config['default']['CostHeatSlack'])

    # data checks:
    check_AvailabilityFactors(plants, AF)
    check_heat_demand(plants, HeatDemand)
    return Outages, AF, ReservoirLevels, ReservoirScaledInflows, HeatDemand, CostHeatSlack


def load_plants(config):
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


    # Defining the hydro storages:
    plants_sto = plants[[u in commons['tech_storage'] for u in plants['Technology']]]
    # check storage plants:
    check_sto(config, plants_sto)
    plants_chp = plants[[str(x).lower() in commons['types_CHP'] for x in plants['CHPType']]]

    return plants, plants_sto, plants_chp

class DataLoader(object):
    
    def __rename_plant_columns(self):
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
                                    
    def __init__(self, config):

        # loading/assigning basic data 
        self.config = config
        self.idx_utc, self.idx_utc_noloc, self.idx_utc_year_noloc = get_indices(self.config) #todo do i really need you all?
        self.Load, self.PeakLoad = load_loads(self.config, self.idx_utc_noloc, self.idx_utc_year_noloc)
        self.flows, self.NTC, self.Interconnections, self.NTCs, self.Inter_RoW = load_interconnections(config, self.idx_utc_noloc)
        self.LoadShedding = NodeBasedTable(config['LoadShedding'],self.idx_utc_noloc,config['countries'],tablename='LoadShedding',default=config['default']['LoadShedding'])
        self.CostLoadShedding = NodeBasedTable(config['CostLoadShedding'],self.idx_utc_noloc,config['countries'],tablename='CostLoadShedding',default=config['default']['CostLoadShedding'])
        #self.LoadShedding, self.CostLoadShedding = load_load_shedding(self.config, self.idx_utc_noloc)
        self.plants, self.plants_sto, self.plants_chp = load_plants(self.config)
        self.FuelPrices = load_fuel_prices(self.config, self.idx_utc_noloc)
        self.Plants_merged, self.mapping = cluster_plants(self.config, self.plants)
        self.Outages, self.AF, self.ReservoirLevels, self.ReservoirScaledInflows, self.HeatDemand, self.CostHeatSlack = get_unit_based_tables(self.idx_utc_noloc, self.config, self.plants, self.plants_sto, self.plants_chp)
        
        # preprocess data
        self.__rename_plant_columns()
        self.__merge_time_series()
        self.__check_plants()
        self.__check_dfs()
        self.__extend_data_with_lookahead()
        self.__prepare_plant_data()

        # adding cep
        self.plants_expanded, self.techs_cost = load_cep_parameters(config, self.Plants_merged)


    def __check_plants(self):
        # data checks:
        check_AvailabilityFactors(self.plants, self.AF)
        check_heat_demand(self.plants, self.HeatDemand)

    def __merge_time_series(self): 

        plants = self.plants
        mapping = self.mapping
        # Merging the time series relative to the clustered power plants:
        self.ReservoirScaledInflows = merge_series(plants, self.ReservoirScaledInflows, mapping, method='WeightedAverage', tablename='ScaledInflows')
        self.ReservoirLevels = merge_series(plants, self.ReservoirLevels, mapping, tablename='ReservoirLevels')
        self.Outages = merge_series(plants, self.Outages, mapping, tablename='Outages')
        self.HeatDemand = merge_series(plants, self.HeatDemand, mapping, tablename='HeatDemand',method='Sum')
        self.AF = merge_series(plants, self.AF, mapping, tablename='AvailabilityFactors')
        self.CostHeatSlack = merge_series(plants, self.CostHeatSlack, mapping, tablename='CostHeatSlack')
        #return ReservoirScaledInflows, self.ReservoirLevels, Outages, HeatDemand, AF, CostHeatSlack


    def __check_dfs(self): 
        # checking data
        idx_utc_noloc = self.idx_utc_noloc

        check_df(self.Load, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='Load')
        check_df(self.AF, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='AF')
        check_df(self.Outages, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='Outages')
        check_df(self.Inter_RoW, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='Inter_RoW')
        check_df(self.FuelPrices, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='FuelPrices')
        check_df(self.NTCs, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='NTCs')
        check_df(self.ReservoirLevels, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='ReservoirLevels')
        check_df(self.ReservoirScaledInflows, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='ReservoirScaledInflows')
        check_df(self.HeatDemand, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='HeatDemand')
        check_df(self.CostHeatSlack, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='CostHeatSlack')
        check_df(self.LoadShedding, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='LoadShedding')
        check_df(self.CostLoadShedding, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='CostLoadShedding')


    def __map_extend_data_with_lookahead(self):
        enddate_long = self.idx_utc_noloc[-1] + dt.timedelta(days=self.config['LookAhead'])
        idx_long = pd.DatetimeIndex(pd.date_range(start=self.idx_utc_noloc[0], end=enddate_long, freq=commons['TimeStep']))
        #Nhours_long = len(idx_long)

        #todo testing
        datasets = [
            'Load','AF','Inter_RoW','NTCs','FuelPrices','Load','Outages','ReservoirLevels',
            'ReservoirScaledInflows','LoadShedding','CostLoadShedding']

        def extend_lookahead(dataset): 
            setattr(self, dataset, getattr(self, dataset)).reindex(idx_long, method='nearest').fillna(method='bfill')

        map(extend_lookahead, datasets)
        

    def __extend_data_with_lookahead(self):

        # Extending the data to include the look-ahead period (with constant values assumed)
        enddate_long = self.idx_utc_noloc[-1] + dt.timedelta(days=self.config['LookAhead'])
        idx_long = pd.DatetimeIndex(pd.date_range(start=self.idx_utc_noloc[0], end=enddate_long, freq=commons['TimeStep']))
        Nhours_long = len(idx_long)

        # re-indexing with the longer index and filling possibly missing data at the beginning and at the end::
        self.Load = self.Load.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.AF = self.AF.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.Inter_RoW = self.Inter_RoW.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.NTCs = self.NTCs.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.FuelPrices = self.FuelPrices.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.Load = self.Load.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.Outages = self.Outages.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.ReservoirLevels = self.ReservoirLevels.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.ReservoirScaledInflows = self.ReservoirScaledInflows.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.LoadShedding = self.LoadShedding.reindex(idx_long, method='nearest').fillna(method='bfill')
        self.CostLoadShedding = self.CostLoadShedding.reindex(idx_long, method='nearest').fillna(method='bfill')
    #    for tr in Renewables:
    #        Renewables[tr] = Renewables[tr].reindex(idx_long, method='nearest').fillna(method='bfill')

    def __prepare_plant_data(self):

        # using references for prettier coding
        config = self.config  
        plants = self.plants  
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
            self.plants_sto = Plants_merged[[u in commons['tech_storage'] for u in Plants_merged['Technology']]]
            # check storage plants:
            check_sto(config, self.plants_sto, raw_data=False)
            # Defining the CHPs:
            self.plants_chp = Plants_merged[[x.lower() in commons['types_CHP'] for x in Plants_merged['CHPType']]].copy()
            # check chp plants:
            check_chp(config, self.plants_chp)
            # For all the chp plants correct the PowerCapacity, which is defined in cogeneration mode in the inputs and in power generation model in the optimization model
            for u in self.plants_chp.index:
                PowerCapacity = self.plants_chp.loc[u, 'PowerCapacity']

                if self.plants_chp.loc[u,'CHPType'].lower() == 'p2h':
                    PurePowerCapacity = PowerCapacity
                else:
                    if pd.isnull(self.plants_chp.loc[u,'CHPMaxHeat']):  # If maximum heat is not defined, then it is defined as the intersection between two lines
                        MaxHeat = PowerCapacity / self.plants_chp.loc[u,'CHPPowerToHeat']
                        self.plants_chp.loc[u, 'CHPMaxHeat'] = 'inf'
                    else:
                        MaxHeat = self.plants_chp.loc[u, 'CHPMaxHeat']
                    PurePowerCapacity = PowerCapacity + self.plants_chp.loc[u,'CHPPowerLossFactor'] * MaxHeat
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
                if oldname not in self.HeatDemand:
                    logging.warning('No heat demand profile found for CHP plant "' + str(oldname) + '". Assuming zero')
                    self.HeatDemand[oldname] = 0
                if oldname not in self.CostHeatSlack:
                    logging.warning('No heat cost profile found for CHP plant "' + str(oldname) + '". Assuming zero')
                    self.CostHeatSlack[oldname] = 0

            # merge the outages:
            for i in plants.index:  # for all the old plant indexes
                # get the old plant name corresponding to s:
                oldname = plants['Unit'][i]
                newname = self.mapping['NewIndex'][i]
    

def load_sets(Nhours_long, look_ahead, plants_index, plants_sto_index, Plants_chp_index, countries, Interconnections, plants_uc=None):
    sets = {
        'h' : [str(x + 1) for x in range(Nhours_long)],
        'z' : [str(x + 1) for x in range(Nhours_long - look_ahead * 24)],
        'mk' : ['DA', '2U', '2D'],
        'n' : countries,
        'u' : plants_index,
        'l' : Interconnections,
        'f' : commons['Fuels'],
        'p' : ['CO2'],
        's' : plants_sto_index,
        'chp' : Plants_chp_index,
        't' : commons['Technologies'],
        'tr' : commons['tech_renewables'],
        'uc': plants_uc
    }

    return sets

def load_params(): 

    sets_param = {
        'AvailabilityFactor': ['u', 'h'],
        'CHPPowerToHeat' : ['chp'],
        'CHPPowerLossFactor' : ['chp'],
        'CHPMaxHeat' : ['chp'],
        'CostFixed' : ['u'],
        'CostHeatSlack' : ['chp','h'],
        'CostLoadShedding' : ['n','h'],
        'CostRampUp' : ['u'],
        'CostRampDown' : ['u'],
        'CostShutDown' : ['u'],
        'CostStartUp' : ['u'],
        'CostVariable' : ['u', 'h'],
        'Curtailment' : ['n'],
        'Demand' : ['mk', 'n', 'h'],
        'Efficiency' : ['u'],
        'EmissionMaximum' : ['n', 'p'],
        'EmissionRate' : ['u', 'p'],
        'FlowMaximum' : ['l', 'h'],
        'FlowMinimum' : ['l', 'h'],
        'Fuel' : ['u', 'f'],
        'HeatDemand' : ['chp','h'],
        'Investment' : ['uc'],
        'EconomicLifetime' : ['uc'],
        'LineNode' : ['l', 'n'],
        'LoadShedding' : ['n', 'h'],
        'Location' : ['u', 'n'],
        'Markup' : ['u', 'h'],
        'Nunits' : ['u'],
        'OutageFactor' : ['u', 'h'],
        'PartLoadMin' : ['u'],
        'PowerCapacity' : ['u'],
        'PowerInitial' : ['u'],
        'PriceTransmission' : ['l', 'h'],
        'RampUpMaximum' : ['u'],
        'RampDownMaximum' : ['u'],
        'RampStartUpMaximum' : ['u'],
        'RampShutDownMaximum' : ['u'],
        'Reserve' : ['t'],
        'StorageCapacity' : ['u'],
        'StorageChargingCapacity' : ['s'],
        'StorageChargingEfficiency' : ['s'],
        'StorageDischargeEfficiency' : ['s'],
        'StorageSelfDischarge' : ['u'],
        'StorageInflow' : ['s', 'h'],
        'StorageInitial' : ['s'],
        'StorageMinimum' : ['s'],
        'StorageOutflow' : ['s', 'h'],
        'StorageProfile' : ['s', 'h'],
        'Technology' : ['u', 't'],
        'TimeUpMinimum' : ['u'],
        'TimeDownMinimum' : ['u'],
    }

    return sets_param

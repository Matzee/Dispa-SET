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


from .DataLoader import DataLoader


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
    dm.build_sim_dir()
    return dm.SimData


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
    if not isinstance(config['default']['CostLoadShedding'], (float, int)):
        config['default']['CostLoadShedding'] = 1000
    if not isinstance(config['default']['CostHeatSlack'], (float, int)):
        config['default']['CostHeatSlack'] = 50


class DispaModel(object):
    """
    Construct by DispaModel(config_dict) or by building the dictionaries through DispaModel.from_excel(), DispaModel.from_yaml()

    """
    def __init__(self, config): # TODO constructor
        if type(config) != dict:
            raise TypeError("Either pass a dictionary DispaModel(config_dict) or use the loader functions DispaModel.from_excel(), DispaModel.from_yaml()")
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
            Plants_chp_index = self.data.plants_chp.index.tolist(),
            countries = self.data.config['countries'],
            Interconnections = self.data.Interconnections,
            plants_uc = self.data.plants_expanded.index.tolist()
        )

        self.sets_param = load_params()  # the parameters with their formal structure without data
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
                \n -> config: %s \
                \n -> Simulationtype: %s \
                \n -> CEP: %r \
                \n -> LP: %r \
                \n -> %s to %s \
                \n -> %i days  \
                \n -> %i plants' % \
             (str(self.config), self.config['SimulationType'], self.LP, self.CEP, str(self.idx_utc_noloc[0]), str(self.idx_utc_noloc[-1]), no_days, no_plants))

    __repr__ = __str__  # pretty printing for usage in jupyter notebooks & print

    def edit_config(self, key, new_value): #TODO

        try:
            self.config[key] = new_value
        except KeyError as e:
            print("Key not found")

    def build_model_parameters(self):

        parameters=dict()
        sets = self.sets
        sets_param = self.sets_param
        #plants = self.data.plants
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
                    parameters[var]["val"] = Plants_merged['FixedCost'].values

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
                logging.warning('Could not find reservoir level data for storage plant ' + s + '. Assuming 50% of capacity')
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
        self.SimData['parameters'] = parameters #todo

    def build_sim_dir(self):

        config = self.config
        gdx_out = "Inputs.gdx"
        sim = self.sim

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
                pickle.dump(self.SimData, pfile, protocol=pickle.HIGHEST_PROTOCOL)
        logging.info('Build finished')

        if os.path.isfile(commons['logfile']):
            shutil.copy(commons['logfile'], os.path.join(sim, 'warn_preprocessing.log'))




def load_sets(Nhours_long, look_ahead, plants_index, plants_sto_index, Plants_chp_index, countries, Interconnections, plants_uc=None):
    sets = {
        'h': [str(x + 1) for x in range(Nhours_long)],
        'z': [str(x + 1) for x in range(Nhours_long - look_ahead * 24)],
        'mk': ['DA', '2U', '2D'],
        'n': countries,
        'u': plants_index,
        'l': Interconnections,
        'f': commons['Fuels'],
        'p': ['CO2'],
        's': plants_sto_index,
        'chp': Plants_chp_index,
        't': commons['Technologies'],
        'tr': commons['tech_renewables'],
        'uc': plants_uc
    }

    return sets

def load_params():

    sets_param = {
        'AvailabilityFactor': ['u', 'h'],
        'CHPPowerToHeat': ['chp'],
        'CHPPowerLossFactor': ['chp'],
        'CHPMaxHeat': ['chp'],
        'CostFixed': ['u'],
        'CostHeatSlack': ['chp', 'h'],
        'CostLoadShedding': ['n', 'h'],
        'CostRampUp': ['u'],
        'CostRampDown': ['u'],
        'CostShutDown': ['u'],
        'CostStartUp': ['u'],
        'CostVariable': ['u', 'h'],
        'Curtailment': ['n'],
        'Demand': ['mk', 'n', 'h'],
        'Efficiency': ['u'],
        'EmissionMaximum': ['n', 'p'],
        'EmissionRate': ['u', 'p'],
        'FlowMaximum': ['l', 'h'],
        'FlowMinimum': ['l', 'h'],
        'Fuel': ['u', 'f'],
        'HeatDemand': ['chp', 'h'],
        'Investment': ['uc'],
        'EconomicLifetime': ['uc'],
        'LineNode': ['l', 'n'],
        'LoadShedding': ['n', 'h'],
        'Location': ['u', 'n'],
        'Markup': ['u', 'h'],
        'Nunits': ['u'],
        'OutageFactor': ['u', 'h'],
        'PartLoadMin': ['u'],
        'PowerCapacity': ['u'],
        'PowerInitial': ['u'],
        'PriceTransmission': ['l', 'h'],
        'RampUpMaximum': ['u'],
        'RampDownMaximum': ['u'],
        'RampStartUpMaximum': ['u'],
        'RampShutDownMaximum': ['u'],
        'Reserve': ['t'],
        'StorageCapacity': ['u'],
        'StorageChargingCapacity': ['s'],
        'StorageChargingEfficiency': ['s'],
        'StorageDischargeEfficiency': ['s'],
        'StorageSelfDischarge': ['u'],
        'StorageInflow': ['s', 'h'],
        'StorageInitial': ['s'],
        'StorageMinimum': ['s'],
        'StorageOutflow': ['s', 'h'],
        'StorageProfile': ['s', 'h'],
        'Technology': ['u', 't'],
        'TimeUpMinimum': ['u'],
        'TimeDownMinimum': ['u'],
    }

    return sets_param

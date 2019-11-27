### Testing the DispaModel class


import dispaset as ds 
import os
import pytest
from dispaset.preprocessing.data_loader import DataLoader
from dispaset.preprocessing.preprocessing import  build_simulation
import pandas as pd
import decorator



conf_file = os.path.abspath('./tests/conf.yml')
unit_file = os.path.abspath('./tests/dummy_data/Units_testcase.csv')
config = ds.load_config_yaml(conf_file)
config["WriteGDX"] = 0


# python -m pytest tests/test_DispaModel.py -v 


######################################## Single tests

def insert_cap_csv():
    plants = pd.read_csv(unit_file, index_col=0)
    plants.loc["Maasvlakte", "Extendable"] = "x"
    plants.to_csv(unit_file, index=True)

def revert_cap_csv():
    plants = pd.read_csv(unit_file, index_col=0)
    plants.loc["Maasvlakte", "Extendable"] = ""
    plants.to_csv(unit_file, index=True)


def build_simulation_cep(config):
    insert_cap_csv()
    data = DataLoader(config)
    revert_cap_csv()
    return data

def test_SimData_set():
    #testing the sets

    SimData = build_simulation(config)
    sets = SimData["sets"]
    assert len(sets['h']) == 745
    assert len(sets['z']) == 721
    assert len(sets['mk']) == 3
    assert len(sets['n']) == 2
    assert len(sets['u']) == 16
    assert len(sets['l']) == 4
    assert len(sets['f']) == 13
    assert len(sets['p']) == 1
    assert len(sets['s']) == 2
    assert len(sets['chp']) == 1
    assert len(sets['t']) == 15
    assert len(sets['tr']) == 4
    assert len(sets['uc']) == 0
    assert len(sets['chp_type']) == 3
    assert len(sets['x_config']) == 8
    assert len(sets['y_config']) == 4


def test_SimData_set_CEP():
    #testing the sets
    insert_cap_csv()
    SimData = build_simulation(config)
    revert_cap_csv()
    sets = SimData["sets"]
    assert len(sets['h']) == 745
    assert len(sets['z']) == 721
    assert len(sets['mk']) == 3
    assert len(sets['n']) == 2
    assert len(sets['u']) == 16
    assert len(sets['l']) == 4
    assert len(sets['f']) == 13
    assert len(sets['p']) == 1
    assert len(sets['s']) == 2
    assert len(sets['chp']) == 1
    assert len(sets['t']) == 15
    assert len(sets['tr']) == 4
    assert len(sets['uc']) == 1
    assert len(sets['chp_type']) == 3
    assert len(sets['x_config']) == 8
    assert len(sets['y_config']) == 4
    

def test_DataLoader_missing_values():

    pars = [
        'AF',
        'CostHeatSlack',
        'CostLoadShedding',
        'FuelPrices',
        'HeatDemand',
        'Inter_RoW',
        'Interconnections',
        'Load',
        'LoadShedding',
        'NTC',
        'NTCs',
        'Outages',
        'PeakLoad',
        'Plants_merged',
        'ReservoirLevels',
        'ReservoirScaledInflows',
    ]

    dl = DataLoader(config)

    for par in pars:
        df = getattr(dl, par)
        if type(df) == pd.DataFrame and par != "Plants_merged": 
            assert df.isnull().sum().sum() == 0  # sum over all columns and rows
        elif type(df) == list:
            assert sum(x is None for x in df) == 0


######################################## Tests for all permutations (simtypes x cep)

SIMULATION_TYPES = ['MILP', 'LP']
CEP = [0, 1]

@pytest.mark.parametrize('sim_type', SIMULATION_TYPES)
@pytest.mark.parametrize('cep', CEP)
class TestDataLoader:
    
    def test_DispaLaoder_build(self, sim_type, cep):
        config['SimulationType'] = sim_type
        config['CEP'] = cep
        data = DataLoader(config)

    def test_cap_expansion(self, sim_type, cep):
        config['SimulationType'] = sim_type
        config['CEP'] = cep

        SimData = build_simulation_cep(config)
        idx_dim = len(SimData.plants_expanded.index.tolist())
        assert(idx_dim == 1)
        assert(SimData.plants_expanded["Extendable"].values[0] == "x")

        # revert to old status and test
        data = DataLoader(config)
        idx_dim = len(data.plants_expanded.index.tolist())
        assert(idx_dim == 0)

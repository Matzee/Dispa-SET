### Testing the DispaModel class


import dispaset as ds 
import os
import pytest
from dispaset.preprocessing.dm import DataLoader, DispaModel
from dispaset.preprocessing.dm import build_simulation
import pandas as pd


conf_file = os.path.abspath('./tests/conf.yml')
unit_file = os.path.abspath('./tests/dummy_data/Units_testcase.csv')
config = ds.load_config_yaml(conf_file)
config["WriteGDX"] = 0



######################################## Tests



def test_DataLoader_all():
    # DataLoder building by config
    dl = DataLoader(config)

def test_DataLoader():
    # model building from yaml
    dl = DataLoader(config)


def test_DispaModel_yaml_all():
    # model building from yaml
    dm = DispaModel.from_yaml(conf_file)


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
        if type(df) == pd.DataFrame and par != "Plants_merged":  # todo which columns are required for plants?
            assert df.isnull().sum().sum() == 0




######################################## Tests for all permutations simtypes x cep

SIMULATION_TYPES = ['MILP', 'LP']
CEP = [0, 1]

@pytest.mark.parametrize('sim_type', SIMULATION_TYPES)
@pytest.mark.parametrize('cep', CEP)
class TestDataModel:

    def test_DispaModel_all(self, sim_type, cep):
        config['SimulationType'] = sim_type
        config['CEP'] = cep
        dm = DispaModel(config)


    def test_cap_expansion(self, sim_type, cep):
        import pandas as pd
        
        config['SimulationType'] = sim_type
        config['CEP'] = cep
        plants = pd.read_csv(unit_file, index_col=0)
        plants.loc["Maasvlakte", "ExtendableCapacity"] = 2
        plants.to_csv(unit_file, index=True)
        dm = DispaModel(config)
        idx_dim = len(dm.data.plants_expanded.index.tolist())
        assert(idx_dim == 1)
        assert(dm.data.plants_expanded["ExtendableCapacity"].values[0] == 2)

        # revert to old status and test
        plants = pd.read_csv(unit_file, index_col=0)
        plants.loc["Maasvlakte", "ExtendableCapacity"] = 0
        plants.to_csv(unit_file, index=True)
        dm = DispaModel(config)
        idx_dim = len(dm.data.plants_expanded.index.tolist())
        assert(idx_dim == 0)


    def test_SimData(self, sim_type, cep):
        config['SimulationType'] = sim_type
        config['CEP'] = cep
        config["WriteGDX"] = 0
        SimData = build_simulation(config)
        sets = SimData["sets"]

        ### is the dimension of the data the same as the parameter for all parameters
        for name, vals in SimData["parameters"].items():
            assert vals["val"].shape == tuple(len(sets[i]) for i in vals["sets"])

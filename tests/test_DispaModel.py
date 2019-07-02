### Testing the DispaModel object 


import dispaset as ds 
import os
import pytest
from dispaset.preprocessing.dm import DataLoader, DispaModel
from dispaset.preprocessing.preprocessing import build_simulation

conf_file = os.path.abspath('./tests/conf.yml')
unit_file = os.path.abspath('./tests/dummy_data/Units_testcase.csv')

SIMULATION_TYPES = ['MILP', 'LP']
CEP = [0, 1]

def test_DispaModel_yaml_all():
    dm = DispaModel.from_yaml(conf_file)

def test_DataLoader_all():
    dl = DataLoader(config)


config = ds.load_config_yaml(conf_file)

# declaration & class are used to get all permutations shared between the tests
@pytest.mark.parametrize('sim_type', SIMULATION_TYPES)
@pytest.mark.parametrize('cep', CEP)
class TestParametrized:

    def test_DispaModel_all(self, sim_type, cep):
        config['SimulationType'] = sim_type
        config['CEP'] = cep
        dl = DispaModel(config)

    # def test_(self, sim_type, cep):
    #     config['SimulationType'] = sim_type
    #     config['CEP'] = cep
    #     dm = DispaModel(config)
    #     sim_values = dm.SimData.values()
    #     assert(len(sim_values) == 5)
    #     #assert(any([len(x) == 0 for x in dm.SimData["sets"].values()])) # all sets have values in the test case

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

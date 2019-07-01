### Testing the DispaModel object 



import dispaset as ds 
import os
import pytest
from dispaset.preprocessing.dm import DataLoader, DispaModel
from dispaset.preprocessing.preprocessing import build_simulation

conf_file = os.path.abspath('./tests/conf.yml')

SIMULATION_TYPES = ['MILP', 'LP']

@pytest.fixture(scope='module',
                params=SIMULATION_TYPES,
                )
def config(request):
    """Generate some data for testing"""
    config = ds.load_config_yaml(conf_file)
    assert isinstance(config, dict)
    config['SimulationType'] = request.param
    return config


def test_DataLoader_all(config):

    dl = DataLoader(config)

def test_DispaModel_all(config):

    dl = DispaModel(config)

def test_DispaModel_yaml_all(config):

    dl = DispaModel()


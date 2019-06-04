
def build_simulation():
    dm = DispaModel(...)


# TODO Move to utils
def get_git_revision_tag():
    """Get version of DispaSET used for this run. tag + commit hash"""
    from subprocess import check_output
    try:
        return check_output(["git", "describe", "--tags", "--always"]).strip()
    except:
        return 'NA'


class DispaModel(object):

    def __init__(self, config): # TODO constructor
        self.config = config
        self.time_range = None # TODO
        self.version = str(get_git_revision_tag())
        self.data = None
        self.model.sets = load_sets()
        self.model.params = load_params() 

        self._dag = {} # reevaluate based on dag


    def __str__(self):
        """Return a descriptive string for this instance, invoked by print() and str()"""

        return ('A Dispa-SET model with ...') #TODO


    def edit_configuration(self, key, new_value):
        """Edit the config file (practical for simulating multiple variations)
        
        Args:
            key (str): the parameter name inside the config name
            new_value (Any): new value for the parameter inside config
        """
        try:
            self.config[key] = new_value
        except KeyError as e: 
            print("Key not found")


    def _update_config(self, config):
        print("reevaluating ...")
        

    def build_model(self, target_dir=""):
        if self.config["SimulationDirectory"]:
            pass
        else:
            pass


def get_model_horizon(): pass


def load_model_data(): pass

def add_capacity_expansion(): pass

def check_dfs(): 
    check_df(Load, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='Load')
    check_df(AF_merged, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1],
             name='AF_merged')
    check_df(Outages_merged, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='Outages_merged')
    check_df(Inter_RoW, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='Inter_RoW')
    check_df(FuelPrices, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='FuelPrices')
    check_df(NTCs, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1], name='NTCs')
    check_df(ReservoirLevels_merged, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1],
             name='ReservoirLevels_merged')
    check_df(ReservoirScaledInflows_merged, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1],
             name='ReservoirScaledInflows_merged')
    check_df(HeatDemand_merged, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1],
             name='HeatDemand_merged')
    check_df(CostHeatSlack_merged, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1],
             name='CostHeatSlack_merged')
    check_df(LoadShedding, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1],
             name='LoadShedding')
    check_df(CostLoadShedding, StartDate=idx_utc_noloc[0], StopDate=idx_utc_noloc[-1],
             name='CostLoadShedding')

def prepare_model_formulation(): pass

def build_model(): pass

def write_to_dest_folder(): pass

def cluster_power_plants(): pass

def write_pickle(): pass

def write_gdx(): pass

class DispaModelFormulation():

    def __init__():
        self.sets = load_sets()
        self.parameters = load_params()

def load_sets(): 
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
    return sets

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
    sets_param['TimeDownMinimum'] = ['u']
    return sets_param


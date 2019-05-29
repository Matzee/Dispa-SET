class DispaModel():

    def __init__(self, config): # TODO constructor
        self.config = config
        self.time_range = None # TODO
        self.model = DispaModelFormulation()

    def edit_configuration(self, parameter, new_value):
        """Edit the config file (practical for simulating multiple variations)
        
        Args:
            parameter (str): the parameter name inside the config name
            new_value (Any): new value for the parameter inside config
        """
        try:
            self.config[parameter] = new_value
        except KeyError as e: 
            print("Key not found")

def get_model_horizon(): pass

def load_model_data(): pass

def add_capacity_expansion(): pass

def check_dfs(): pass

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


def load_sets(): pass
def load_params(): pass
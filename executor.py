import yaml
from train import train
from inference import predict
from utils.misc_utils import limit_gpu

from timeit import default_timer as timer
from datetime import datetime
now = datetime.now().strftime('%d-%m-%Y')

# Getting all parameters from config.yaml
with open('./config.yaml', 'r') as file:
    config_main = yaml.safe_load(file)
    
def executor(locals_dict):
    # Updating all user parameters 
    start = timer()
    global a
    a = 0
    def update_config(current_path,config_main ):
        _dict = {}
        global a
        for key,value in config_main.items():
            if key in locals_dict:
                _dict[key] = locals_dict[key]
            elif (current_path + "__" + key) in locals_dict:
                _dict[key] = locals_dict[(current_path + "__"+key)]
                print(current_path + "__"+key)
            elif isinstance(value, dict):
                if a == 1:
                    if len(current_path)>0:
                        _dict[key] = update_config(current_path + "__" + key, value)
                    else:
                        _dict[key] = update_config(current_path + key, value)
                else:
                    a = 1
                    _dict[key] = update_config(current_path , value)
                    a = 0
            else:
                _dict[key] = config_main[key]
        return _dict
    current_config = update_config("",config_main)
    
    with open(f'./assets/config-{now}.yaml', 'w') as file:
        yaml.safe_dump(current_config, file)
    with open('config.yaml', 'w') as config_data:
        yaml.safe_dump(current_config ,config_data)
        
    if current_config['limit_gpu'] is not False:
        limit_gpu()
        
    if current_config['mode'] == 'training':
        print("[INFO]...Starting Training Job")
        train(current_config)
        
    if current_config['mode'] =='inference':
        print("[INFO]...Starting Inference Job")
        predict(current_config)
        
    end = timer()
    print(f"[INFO]...Time taken by {current_config['mode']} is {(end - start)/60:.2f} min(s)")
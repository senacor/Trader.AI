'''
Created on 15.11.2017

Utility functions

@author: jtymoszuk
'''
import os
from keras.models import Sequential
from keras.models import model_from_json
from definitions import ROOT_DIR


def save_keras_sequential(model: Sequential, relative_path: str, file_name_without_extension: str) -> bool:
    """
    Saves a Keras Sequential in File System
    
    Args:
        model : Sequential to save
        relative_path : relative path in project
        file_name_without_extension : file name without extension, will be used for json with models and h5 with weights.
    Returns:
        True if successful, False otherwise, never None
    """
    try:
        model_as_json = model.to_json()
        
        json_file = open(os.path.join(ROOT_DIR, relative_path, file_name_without_extension + '.json'), "w")
        json_file.write(model_as_json)
        json_file.close()
        
        model.save_weights(os.path.join(ROOT_DIR, relative_path, file_name_without_extension + '.h5'))
        return True
    except:
        print(f"save_keras_sequential: Writing of Sequential as file failed")
        return False


def load_keras_sequential(relative_path: str, filename: str) -> Sequential:
    """
    Loads a Keras Sequential from File System
    
    Args:
        model : Sequential to save
        relative_path : relative path in project
    Returns:
        Sequential, or None if nothing found or error
    """
   
    model_filename_with_path = os.path.join(ROOT_DIR, relative_path, filename + '.json')
    weights_filenme_with_path = os.path.join(ROOT_DIR, relative_path, filename + '.h5')
    
    if os.path.exists(model_filename_with_path) and os.path.exists(weights_filenme_with_path):
        try:             
            json_file = open(model_filename_with_path, 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            model = model_from_json(loaded_model_json)
            model.load_weights(weights_filenme_with_path)
            return model
        except:
            print(f"load_keras_sequential: Loading of Sequential {model_filename_with_path} failed!")
            return False   
    else:
        print(f"load_keras_sequential: model File {model_filename_with_path} or weights file {weights_filenme_with_path} not found!")
        return None

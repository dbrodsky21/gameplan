import pandas as pd
import numpy as np

import gameplan.helpers as hp


class Collection():
    def __init__(self, collection_type, objects={}):
        self.collection_type = collection_type
        if [x for x in objects.values() if not isinstance(x, collection_type)]:
            raise ValueError(f"All objects must be of type {collection_type}")
        self.contents = objects


    def add_object(self, object, label=None, if_exists='error'):
        if not isinstance(object, self.collection_type):
            raise ValueError(f"Object must be a {self.collection_type} object.")

        default_label = f"item_{len(self.contents) + 1}"
        label = label if label else getattr(object, 'name', default_label)
        if label in self.contents:
            error_message = (
                f"Label '{label}' already exists. "
                f"If you want to overwrite it, set if_exists to 'overwrite'"
            )
            warning_message = (
                f"Label '{label}' already exists. Will overwrite."
            )
            if if_exists == 'error':
                raise ValueError(error_message)
            elif if_exists == 'overwrite':
                warnings.warn(warning_message)
            else:
                raise ValueError(error_message)

        self.contents[label] = object


    def remove_object(self, label, verbose=True):
        if label in self.contents:
            del self.contents[label]
        elif verbose:
            warnings.warn(f"No object w/ label '{label}' exists.")

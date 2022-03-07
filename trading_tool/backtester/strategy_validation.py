import numpy as np
import pandas as pd

def walk_forward_validation_split(data, windows, test_blocks, train_blocks=None, train_with_later_data=False, window_buffer = 1, unique_validation_sets=False):
  # first break the dataframe into the blocks
  data_blocks = np.array_split(data, windows)
  training_sets, validation_sets = [],[]
  increment = test_blocks if unique_validation_sets else 1
  if train_blocks is None:
    window_ranges = range(1,windows-test_blocks, increment)
  else:
    window_ranges = range(train_blocks,windows-test_blocks,increment)
  for i in window_ranges:
    if not train_blocks is None:
      training_sets.append(pd.concat(data_blocks[i-train_blocks:i]))
    else:
      if not train_with_later_data:
        training_sets.append(pd.concat(data_blocks[:i]))
      else:
        training_sets.append(pd.concat(data_blocks[:i]+data_blocks[i+test_blocks+window_buffer:]))
    validation_sets.append(pd.concat(data_blocks[i:i+test_blocks]))
  return training_sets, validation_sets

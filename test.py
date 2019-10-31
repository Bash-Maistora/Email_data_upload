'''
Task:
The peak memory usage of this script is too high and runs out of memory on users machines.
How can you fix the memory usage without breaking the test?
You should be able to relatively easily reduce the memory usage by _at least_ 25%
'''
import os
import resource
import pandas as pd
from pandas.util import hash_pandas_object
import hashlib
import typing
import random

# Deterministic randomness for the assert at the end
random.seed(42)

TRANSFORMS = 10

ROWS = 20000000

DATA = [random.random() for _ in range(ROWS)]

def update_df(df_orig: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
    return pd.concat((df_orig, df_new), axis=1)

class Transform:
    '''A transform that adds a column of random data'''
    def __init__(self, var: str):
        self.var = var
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = pd.DataFrame({self.var: DATA})
        df_new = df_new.astype('float32')
        return update_df(df, df_new)

class Pipeline:
    def __init__(self):
        self.df = pd.DataFrame()
        self.transforms = [Transform(f'v{i}') for i in range(TRANSFORMS)]
    def run(self):
        for t in self.transforms:
            self.df = t.transform(self.df)
        return self.df

if __name__ == '__main__':
    pipe = Pipeline()
    df = pipe.run()
    # Dont break the test
    print(df.memory_usage(deep=True) / 1024 ** 2)
    assert hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest() == "867567dc7d46f77af2bca9804ac366a5165d27612de100461b699bd23094ab90"
    print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

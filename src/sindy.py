# https://humaticlabs.com/blog/sindy-guide/
# https://bea.stollnitz.com/blog/sindy-lorenz/

import click
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso, ridge_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler



def load_dataset():
    df = pd.read_csv('reprocessing/final_dataset.csv')
    print(df.head())

def build_theta():
    pass

def lasso():
    pass

def stlsq():
    pass

def plot_pareto_lasso():
    pass

def plot_pareto_stlsq():
    pass

def predict():
    pass
import numpy as np

def logarithmic_fn(x, a, b, c):
    return a + b*np.log(x + c)

def logistic_fn(x, a, b, c):
    return a / (1 + b*np.e**(-c * (x)))

def exponential_fn(x, a, b):
    """Alternatively: a * np.exp(b*x)"""
    return a * (1 + b)**x

def linear_fn(x, a, b):
    return a + b*x

# def sigmoid(x, x0, k):
#     y = 1 / (1 + np.exp(-k*(x-x0))) + 1
#     return
#
# def fsigmoid(x, a, b):
#     return 1.0 / (1.0 + np.exp(-a*(x-b)))

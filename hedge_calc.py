#workflow
# the algorithm works like a Markwitz optimisation problem. Instead of optimising return and volatility, we optimise the greek exposure. 
# After we select the contracts we want to short and the contracts we use to hedge. The optimising goal is to maintain delta, gamma and vega neutral while keeping most of the theta. The utility function incoporates penalty terms to avoid concentration of position

import pandas as pd
import os
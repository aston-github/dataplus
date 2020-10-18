import pandas as pd
import numpy as np
from scipy.stats import iqr
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity

df = pd.read_csv("first ap connection durations_all dates.csv")
data = df['connection_duration'].to_numpy().reshape(-1,1)
q3 = np.quantile(data,0.75)
cutoff = 1.5 * iqr(data) + q3
print(cutoff)

newDF = pd.DataFrame(columns=['connection_duration'])
for i in range(len(df)):
    if df['connection_duration'][i] <= cutoff:
        newDF = newDF.append({'connection_duration': df['connection_duration'][i]}, ignore_index=True)
x = newDF['connection_duration'].to_numpy().reshape(-1,1)
x = np.sort(x,axis=0)
print(x.size)
print(np.unique(x))
print(x[:5])

scotts_factor = (x.size)**(-1./(1+4))
print(scotts_factor)
kde = KernelDensity(bandwidth=scotts_factor, kernel='gaussian').fit(x)

# Mean - Monte Carlo
n_samples = 1000000
samples = kde.sample(n_samples)
mean_mc = samples.mean()
print(mean_mc)

#logprob = kde.score_samples(x)
#print(logprob[:5])

#plt.plot(x, np.exp(logprob), alpha=0.5)
#plt.hist(x,bins=np.linspace(0,300,300))
#plt.show()


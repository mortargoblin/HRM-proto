import math

def rmssd(ppi): # RMSSD, or Root Mean Square of Successive Differences, is a key Heart Rate Variability (HRV) metric. 
    if len(ppi) < 2:
        return 0

    diffs = []
    for i in range(len(ppi)-1):
        d = ppi[i+1] - ppi[i]
        diffs.append(d * d)

    mean_sq = sum(diffs) / len(diffs)
    return round(math.sqrt(mean_sq))


def sdnn(ppi): # SDNN (Standard Deviation of NN Intervals) is a key Heart Rate Variability (HRV) metric, measuring the total variation in time between normal heartbeats (NN intervals) over a period of time.
    if len(ppi) < 2:
        return 0

    mean = sum(ppi) / len(ppi)

    var_sum = 0
    for x in ppi:
        var_sum += (x - mean) ** 2

    variance = var_sum / (len(ppi) - 1)
    return round(math.sqrt(variance))


import math

#--------------------------------------------------------# 
# Class for calculating MEAN BPM, MEAN PPI, RMSSD & SDNN #
#--------------------------------------------------------#
class HRV:
    def calc_hrv(self, avg_bpm_list, ppi_list):
        self.avg_bpm_list = avg_bpm_list
        self.ppi_list = ppi_list
        return [self.avg_bpm(), self.avg_ppi(), self.rmssd(), self.sdnn()]

    def avg_bpm(self):
        return int(sum(self.avg_bpm_list) / len(self.avg_bpm_list))
        
    
    def avg_ppi(self):
        return int(sum(self.ppi_list) / len(self.ppi_list))

    # RMSSD, or Root Mean Square of Successive Differences, is a key Heart Rate Variability (HRV) metric.
    def rmssd(self):  
        if len(self.ppi_list) < 2:
            return 0

        diffs = []
        for i in range(len(self.ppi_list)-1):
            d = self.ppi_list[i+1] - self.ppi_list[i]
            diffs.append(d * d)

        mean_sq = sum(diffs) / len(diffs)
        return round(math.sqrt(mean_sq))
    
    # SDNN (Standard Deviation of NN Intervals) is a key Heart Rate Variability (HRV) metric, measuring the total variation in time between normal heartbeats (NN intervals) over a period of time.
    def sdnn(self):       
        if len(self.ppi_list) < 2:
            return 0

        mean = sum(self.ppi_list) / len(self.ppi_list)

        var_sum = 0
        for x in self.ppi_list:
            var_sum += (x - mean) ** 2

        variance = var_sum / (len(self.ppi_list) - 1)
        return round(math.sqrt(variance))
import numpy as np
import scipy.signal as signal
from scipy import sparse
from scipy.sparse.linalg import spsolve
import pandas as pd



# asymmetric least squares baseline correction
def baseline_als(y, lam=1e5, p=0.01, niter=10):
    L = len(y)
    D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2), dtype=None)
    w = np.ones(L)
    for i in range(niter):
        W = sparse.spdiags(w,0,L,L)
        Z = W + lam * D.dot(D.transpose())
        z = spsolve(Z, w*y)
        w = p * (y > z) + (1-p) * (y < z)
    return z


def process_XRD_data(data,
                    roi: bool = False,
                    roi_start: float = 64.5,
                    roi_end: float = 66.5):

    if roi:
        # use a reagion of interest to isolate the SiC peak (64.5 - 66.5)
        silicide_part = data[data['Angle'] < roi_start].copy()
        substrate_part = data[(data['Angle'] >= roi_start) & (data['Angle'] <= roi_end)].copy()
        tail_part = data[data['Angle'] > roi_end].copy()

        # process silicide part
        silicide_part['baseline'] = baseline_als(silicide_part['Intensity'])
        silicide_part['corrected'] = silicide_part['Intensity'] - silicide_part['baseline']
        silicide_part['filtered'] = signal.savgol_filter(silicide_part['corrected'], 11, 3)

        # process tail part
        tail_part['baseline'] = baseline_als(tail_part['Intensity'])
        tail_part['corrected'] = tail_part['Intensity'] - tail_part['baseline']
        tail_part['filtered'] = signal.savgol_filter(tail_part['corrected'], 11, 3)

        # normalize everything to the silicides strongest peak
        scale_factor = silicide_part['filtered'].max()

        silicide_part['intensity_norm'] = silicide_part['filtered'] / scale_factor
        substrate_part['intensity_norm'] = substrate_part['Intensity'] / scale_factor # Substrate will be > 1.0
        tail_part['intensity_norm'] = tail_part['filtered'] / scale_factor

        # find peaks in silicide and tail parts
        sil_peaks_idx, _ = signal.find_peaks(silicide_part['filtered'], prominence=0.05 * silicide_part['filtered'].max(), width=5)
        sil_actual_indices = silicide_part.index[sil_peaks_idx]
        tail_peaks_idx, _ = signal.find_peaks(tail_part['filtered'], prominence=0.05 * silicide_part['filtered'].max(), width=5)
        tail_actual_indices = tail_part.index[tail_peaks_idx]

        all_peak_indices = np.concatenate([sil_actual_indices, tail_actual_indices])

        # combine back together
        full_processed = pd.concat([silicide_part, substrate_part, tail_part]).sort_values('Angle')
        full_processed['log_intensity'] = np.log10(full_processed['intensity_norm'] + 1)

        peak_angles = full_processed.loc[all_peak_indices, 'Angle']
        print(peak_angles)
        
    else:
        full_processed = data.copy()
        # process silicide part
        full_processed['baseline'] = baseline_als(full_processed['Intensity'])
        full_processed['corrected'] = full_processed['Intensity'] - full_processed['baseline']
        full_processed['filtered'] = signal.savgol_filter(full_processed['corrected'], 11, 3)

        # normalize everything to the silicides strongest peak
        scale_factor = full_processed['filtered'].max()
        full_processed['intensity_norm'] = full_processed['filtered'] / scale_factor

        # find peaks in silicide and tail parts
        peaks_idx, _ = signal.find_peaks(full_processed['filtered'], prominence=0.05 * full_processed['filtered'].max(), width=5)


        peak_angles = full_processed.loc[peaks_idx, 'Angle']
        print(peak_angles)
        

    return full_processed, peak_angles
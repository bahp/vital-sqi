from pyedflib import highlevel
from wfdb import rdsamp, wrsamp
import numpy as np
import pandas as pd
import datetime as dt
from vital_sqi.common import generate_timestamp, utils
from vital_sqi.data.signal_sqi_class import SignalSQI


def ECG_reader(file_name, file_type=None, channel_num=None,
               channel_name=None, sampling_rate=None, start_datetime=None):
    """

    Parameters
    ----------
    file_name :
        
    file_type :
        (Default value = None)
    channel_num : frm 0
        (Default value = None)
    channel_name :
        (Default value = None)
    sampling_rate :
         (Default value = None)
    start_datetime : optional
         (Default value = None)

    Returns
    -------

    
    """
    if file_type == 'edf':
        signals, signal_headers, header = highlevel.read_edf(
                edf_file=file_name,
                ch_nrs=channel_num,
                ch_names=channel_name)
        if not isinstance(sampling_rate, (int, float)):
            try:
                sampling_rate = signal_headers[0]['sample_rate']
            except KeyError:
                print("sampling_rate is not defined and could not be "
                      "inferred from the signal's header.")
        if sampling_rate <= 0:
            raise ValueError("Invalid sampling rate value}")
        if start_datetime is None:
            try:
                start_datetime = header['startdate']
            except KeyError:
                start_datetime = None
        signals = signals.transpose()
        info = [header, signal_headers]
        out = SignalSQI(signals = signals,
                        wave_type = 'ecg',
                        sampling_rate = sampling_rate,
                        start_datetime = start_datetime,
                        info = info)
    elif file_type == 'mit':
        signals, info = rdsamp(record_name=file_name,
                               channels=channel_num,
                               channel_names=channel_name,
                               warn_empty=True,
                               return_res=64)
        sampling_rate = info['fs']
        date = info['base_date']
        time = info['base_time']
        if date is not None and isinstance(date, dt.date):
            start_datetime = dt.datetime(year= date.year, month=date.month,
                                         day=date.day, hour=0, minute=0,
                                         second=0, microsecond=0)
            if time is not None and isinstance(time, dt.time):
                start_datetime.hour = time.hour
                start_datetime.minute = time.minute
                start_datetime.second = time.second
                start_datetime.microsecond = time.microsecond
        else:
            start_datetime = None
        out = SignalSQI(signals=signals, wave_type='ecg',
                        sampling_rate=sampling_rate,
                        start_datetime = start_datetime,
                        info=info)
    elif file_type == 'csv':
        use_cols = None
        if channel_name is not None:
            use_cols = channel_name
        if channel_name is not None:
            use_cols = channel_num
        out = pd.read_csv(file_name,
                          usecols=use_cols,
                          skipinitialspace=True)
        try:
            v_str_to_datetime = np.vectorize(dt.datetime.strptime)
            timestamps = v_str_to_datetime(timestamps, '%Y-%m-%d '
                                                       '%H:%M:%S.%f')
            start_datetime = timestamps[0]
        except Exception:
            pass
        if not (isinstance(sampling_rate, int) or
                isinstance(sampling_rate, float)):
            timestamps = out.iloc[:, 0].to_numpy()
            sampling_rate = utils.calculate_sampling_rate(timestamps)
        if sampling_rate is None:
            raise Exception("Sampling rate not found nor inferred")
        signals = out.drop(0).to_numpy()
        out = SignalSQI(signals=signals, wave_type='ecg',
                        sampling_rate=sampling_rate,
                        start_datetime=start_datetime)
    else:
        raise ValueError("File type {0} not supported".format(file_type))

    return out


def ECG_writer(signal_sqi, file_name, file_type, info=None):
    """

    Parameters
    ----------
    signal_sqi : SignalSQI object containing signals, sampling rate and sqi

    file_name : name of file to write, with extension. For edf file_type,
    possible extensions are edf, edf+, bdf, bdf+. For mit file_type,
    possible extensions are... :
        
    file_type : edf or mit or csv
        
    info : list
        In case of writing edf file: A list containing signal_headers and
        header (in
        order). signal_headers is a list of dict with one signal header for
        each signal channel. header (dict) contain ecg file information.
        In case of writing wfdb record (mit file): A dict containing header
        as defined in .hea file.
        (Default value = None)

    Returns
    -------
    """
    signals = signal_sqi.signals
    sampling_rate = signal_sqi.sampling_rate
    start_datetime = signal_sqi.start_datetime
    if file_type == 'edf':
        if info is not None:
            signal_headers = info[0]
            header = info[1]
            highlevel.write_edf(file_name, signals, signal_headers,
                                header, file_type=-1, digital=False,
                                block_size=-1)
        else:
            highlevel.write_edf_quick(file_name, signals, sampling_rate)
    if file_type == 'mit':
        if info is None:
            raise Exception("Header dict needed")
        else:
            wrsamp(record_name=file_name,
                   fs=sampling_rate,
                   units=info['units'],
                   sig_name=info['sig_name'],
                   p_signal=signals,
                   base_date=info['base_date'],
                   base_time=info['base_time'],
                   comments=info['comments'])
    if file_type == 'csv':
        timestamps = generate_timestamp(start_datetime, sampling_rate,
                                        signals.shape[0])
        signals = pd.DataFrame(np.hstack((np.array(timestamps).reshape(-1, 1),
                                          signals)))
        signals.to_csv(path_or_buf=file_name, index=False, header=True)
    return True


def PPG_reader(file_name, signal_idx, timestamp_idx, sampling_rate):
    """

    Parameters
    ----------
    file_name :
        

    Returns
    -------

    """
    signals = pd.read_csv(file_name, usecols = [timestamps, signal_idx])

out = ECG_reader('/Users/haihb/Documents/Work/Oucru/innovation/vital_sqi/tests'
            '/test_data/ecg_test_w.csv', 'csv', sampling_rate = 100)
# ECG_writer(out, '/Users/haihb/Documents/Work/Oucru/innovation/vital_sqi/tests'
#             '/test_data/ecg_test_w.csv', 'csv')
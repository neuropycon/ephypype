"""Preprocessing functions.

Authors: Dmitrii Altukhov <dm-altukhov@ya.ru>
         Annalisa Pascarella <a.pascarella@iac.cnr.it>
"""

import os
import sys
import numpy as np
import glob
import os.path as op

from mne import pick_types, read_epochs, Epochs, read_events, find_events
from mne import write_evokeds, set_bipolar_reference
from mne.io import read_raw_fif, read_raw_brainvision, read_raw_eeglab
from mne.preprocessing import ICA
from mne.preprocessing import create_ecg_epochs, create_eog_epochs
from mne.report import Report
from mne.time_frequency import psd_multitaper
from mne.channels import read_custom_montage, make_standard_montage

from nipype.utils.filemanip import split_filename


def _preprocess_fif(
        fif_file, data_type='fif', l_freq=None, h_freq=None, down_sfreq=None,
        montage=None, misc=None, eog_ch=None, ch_new_names=None,
        bipolar=None):
    """Filter and downsample data."""
    _, basename, ext = split_filename(fif_file)

    if data_type == 'fif':
        raw = read_raw_fif(fif_file, preload=True)
    elif data_type == 'eeg':
        if ext == '.vhdr':
            raw = read_raw_brainvision(fif_file, preload=True)
        elif ext == '.set':  # EEGLAB
            raw = read_raw_eeglab(fif_file, preload=True)
        ext = '.fif'
        if misc:
            for ch in misc:
                raw.set_channel_types({ch: 'misc'})
        # channels = eog_ch.replace(' ', '').split(',')

        try:
            montage = read_custom_montage(montage)
        except:
            # when raw is read from EEGLAB some channels name has different
            # name from the one in the standard montage
            if ch_new_names:
                raw.rename_channels(ch_new_names)
            montage = make_standard_montage(montage)
        raw.set_montage(montage, on_missing='ignore')

        if bipolar:
            for key in bipolar.keys():
                raw = set_bipolar_reference(
                    raw, anode=bipolar[key][0], cathode=bipolar[key][1], ch_name=key)  # noqa
        print(raw.info['ch_names'])
        for ch in eog_ch:
            raw.set_channel_types({ch: 'eog'})

    filt_str, down_str = '', ''

#    select_sensors = pick_types(raw.info, meg=True, ref_meg=False, eeg=False)

    if l_freq or h_freq:
        raw.filter(l_freq=l_freq, h_freq=h_freq,
                   picks=None, fir_design='firwin')
        filt_str = '_filt'
    if down_sfreq:
        raw.resample(sfreq=down_sfreq, npad=0)
        down_str = '_dsamp'

    savename = os.path.abspath(basename + filt_str + down_str + ext)
    raw.save(savename)
    return savename


def _compute_ica(fif_file, raw_fif_file, data_type,
                 ecg_ch_name, eog_ch_name, n_components, reject):
    """Compute ica solution."""
    subj_path, basename, ext = split_filename(fif_file)
    orig_raw = read_raw_fif(raw_fif_file, preload=True)
    raw = read_raw_fif(fif_file, preload=True)

    # select sensors
    if data_type == 'eeg':
        select_sensors = pick_types(raw.info, eeg=True, exclude='bads')
    else:
        select_sensors = pick_types(
            raw.info, meg=True, ref_meg=False, exclude='bads')

    # 1) Fit ICA model using the FastICA algorithm
    # Other available choices are `infomax` or `extended-infomax`
    # We pass a float value between 0 and 1 to select n_components based on the
    # percentage of variance explained by the PCA components.
    orig_raw.filter(l_freq=1., h_freq=None)

    flat = dict(mag=1e-13, grad=1e-13)

    ica = ICA(n_components=n_components, method='fastica', max_iter='auto')
    ica.fit(orig_raw, picks=select_sensors, reject=reject, flat=flat)
    del orig_raw
    # -------------------- Save ica timeseries ---------------------------- #
    ica_ts_file = os.path.abspath(basename + "_ica-tseries.fif")
    ica_src = ica.get_sources(raw)
    ica_src.save(ica_ts_file, overwrite=True)
    ica_src = None
    # --------------------------------------------------------------------- #

    # 2) identify bad components by analyzing latent sources.
    # generate ECG epochs use detection via phase statistics

    # if we just have exclude channels we jump these steps
    n_max_ecg = 3
    n_max_eog = 3

    # check if ecg_ch_name is in the raw channels
    if ecg_ch_name in raw.info['ch_names']:
        raw.set_channel_types({ecg_ch_name: 'ecg'})
    else:
        ecg_ch_name = None

    # set ref_meg to 'auto'
    if data_type != "eeg":
        select_sensors = pick_types(raw.info, meg=True,
                                    ref_meg='auto', exclude='bads')
        ecg_epochs = create_ecg_epochs(raw, tmin=-0.5, tmax=0.5,
                                       picks=select_sensors,
                                       ch_name=ecg_ch_name)

        ecg_inds, ecg_scores = ica.find_bads_ecg(ecg_epochs, method='ctps')

        ecg_evoked = ecg_epochs.average()
        ecg_epochs = None

        ecg_inds = ecg_inds[:n_max_ecg]
        ica.exclude += ecg_inds
    else:
        ecg_inds = []
        ecg_evoked = []
        ecg_scores = []

    # eog_ch_name = eog_ch_name.replace(' ', '')
    if set(eog_ch_name).issubset(set(raw.info['ch_names'])):
        print('*** EOG CHANNELS FOUND ***')
        eog_inds, eog_scores = ica.find_bads_eog(raw, ch_name=eog_ch_name)
        eog_inds = eog_inds[:n_max_eog]
        ica.exclude += eog_inds
        eog_evoked = create_eog_epochs(raw, tmin=-0.5, tmax=0.5,
                                       baseline=(-0.5, -0.2),
                                       picks=select_sensors,
                                       ch_name=eog_ch_name).average()
    else:
        print('*** NO EOG CHANNELS FOUND!!! ***')
        eog_inds = eog_scores = eog_evoked = None

    report_file = _generate_report(raw=raw, ica=ica, subj_name=fif_file,
                                   basename=basename,
                                   ecg_evoked=ecg_evoked,
                                   ecg_scores=ecg_scores,
                                   ecg_inds=ecg_inds,
                                   ecg_ch_name=ecg_ch_name,
                                   eog_evoked=eog_evoked,
                                   eog_scores=eog_scores,
                                   eog_inds=eog_inds,
                                   eog_ch_name=eog_ch_name)
    report_file = os.path.abspath(report_file)
    ica_sol_file = os.path.abspath(basename + '_ica_solution.fif')
    ica.save(ica_sol_file)
    raw_ica = ica.apply(raw)
    raw_ica_file = os.path.abspath(basename + '_ica' + ext)
    raw_ica.save(raw_ica_file, overwrite=True)

    return raw_ica_file, ica_sol_file, ica_ts_file, report_file


def _preprocess_set_ica_comp_fif_to_ts(fif_file, subject_id, n_comp_exclude,
                                       is_sensor_space):
    """Preprocess ICA fif to ts."""
    import os
    from nipype.utils.filemanip import split_filename as split_f
    from mne.io import read_raw_fif
    from mne.preprocessing import read_ica
    from ephypype.fif2array import _get_raw_array

    subj_path, basename, ext = split_f(fif_file)
    (data_path, sbj_name) = os.path.split(subj_path)

    print('*** SBJ {} ***'.format(subject_id))

    # Read raw
    current_dir = os.getcwd()
    print('*************************** {}'.format(current_dir))
    if os.path.exists(os.path.join(current_dir, '../ica',
                                   basename + '_ica' + ext)):
        raw_ica_file = os.path.join(
            current_dir, '../ica', basename + '_ica' + ext)
    elif os.path.exists(os.path.join(current_dir, '../ica',
                                     basename + '_filt_ica' + ext)):
        raw_ica_file = os.path.join(
            current_dir, '../ica', basename + '_filt_ica' + ext)
    elif os.path.exists(os.path.join(current_dir, '../ica',
                                     basename + '_filt_dsamp_ica' + ext)):
        raw_ica_file = os.path.join(
            current_dir, '../ica', basename + '_filt_dsamp_ica' + ext)
    else:
        # it will work only for pytest
        current_dir = subj_path
        raw_ica_file = fif_file

    print('*** raw_ica_file {} ***'.format(raw_ica_file))
    raw = read_raw_fif(raw_ica_file, preload=True)

    # load ICA
    if os.path.exists(os.path.join(current_dir, '../ica',
                                   basename + '_ica_solution.fif')):
        ica_sol_file = os.path.join(
            current_dir, '../ica', basename + '_ica_solution.fif')
    elif os.path.exists(os.path.join(current_dir, '../ica',
                                     basename + '_filt_ica_solution.fif')):
        ica_sol_file = os.path.join(
            current_dir, '../ica', basename + '_filt_ica_solution.fif')
    elif os.path.exists(os.path.join(current_dir, '../ica',
                                     basename + "_filt_dsamp_ica_solution."
                                     "fif")):
        ica_sol_file = os.path.join(
            current_dir, '../ica', basename + '_filt_dsamp_ica_solution.fif')
    else:
        # it will work only for pytest
        ica_sol_file = os.path.join(current_dir, basename + '_solution.fif')

    if os.path.exists(ica_sol_file) is False:
        print('$$$ Warning, no {} found'.format(ica_sol_file))
        sys.exit()
    else:
        ica = read_ica(ica_sol_file)

    print('\n *** ica.exclude before set components= {}'.format(ica.exclude))
    if subject_id in n_comp_exclude:
        print('*** ICA to be excluded for sbj {}'.format(subject_id))
        print(' {} ***'.format(n_comp_exclude[subject_id]))
        session_dict = n_comp_exclude[subject_id]
        session_names = list(session_dict.keys())

        componentes = []
        for s in session_names:
            componentes = session_dict[s]

        if len(componentes) == 0:
            print('!!! no ICA to be excluded !!! \n')
        else:
            print('\n *** ICA to be excluded for session {}'.format(s))
            print(' {} ***'.format(componentes))

    ica.exclude = componentes

    print(('*** ica.exclude after set components = {}'.format(ica.exclude)))

    # apply ICA to raw data
    new_raw_ica_file = os.path.abspath(basename + '_ica' + ext)
    raw_ica = ica.apply(raw)

    raw_ica.save(new_raw_ica_file, overwrite=True)

    # save ICA solution
    print(ica_sol_file)
    ica.save(ica_sol_file)

    (ts_file, channel_coords_file, channel_names_file,
     raw.info['sfreq']) = _get_raw_array(new_raw_ica_file)

    if is_sensor_space:
        return (ts_file, channel_coords_file, channel_names_file,
                raw.info['sfreq'])
    else:
        return (raw_ica, channel_coords_file, channel_names_file,
                raw.info['sfreq'])


def _get_raw_info(raw_fname):
    """Get info from raw."""
    from mne.io import read_raw_fif

    raw = read_raw_fif(raw_fname, preload=True)
    return raw.info


def _get_epochs_info(raw_fname):
    """Get epoch info."""
    from mne import read_epochs

    epochs = read_epochs(raw_fname)
    return epochs.info


def get_raw_sfreq(raw_fname):
    """Get raw sfreq."""
    try:
        data = read_raw_fif(raw_fname)
    except:  # noqa
        data = read_epochs(raw_fname)
    return data.info['sfreq']


def _create_reject_dict(raw_info, data_type='meg'):
    """Create reject dir."""
    picks_eog, picks_eeg, picks_grad, picks_mag = [], [], [], []
    picks_eog = pick_types(raw_info, meg=False, ref_meg=False, eog=True)

    if data_type == 'meg':
        picks_mag = pick_types(raw_info, meg='mag', ref_meg=False)
        picks_grad = pick_types(raw_info, meg='grad', ref_meg=False)
    elif data_type == 'eeg':
        picks_eeg = pick_types(raw_info, eeg=True)

    reject = dict()
    if len(picks_mag) > 0:
        reject['mag'] = 4e-12
    if len(picks_grad) > 0:
        reject['grad'] = 4000e-13
    if len(picks_eog) > 0:
        reject['eog'] = 250e-6
    if len(picks_eeg) > 0:
        reject['eeg'] = 150e-6
    print(reject)
    return reject


def _generate_report(raw, ica, subj_name, basename,
                     ecg_evoked, ecg_scores, ecg_inds, ecg_ch_name,
                     eog_evoked, eog_scores, eog_inds, eog_ch_name):
    """Generate report for ica solution."""
    import matplotlib.pyplot as plt

    report = Report()

    ica_title = 'Sources related to %s artifacts (red)'
    is_show = False

    # ------------------- Generate report for ECG ------------------------ #
    if len(ecg_scores) > 0:
        fig_ecg_scores = ica.plot_scores(ecg_scores,
                                         exclude=ecg_inds,
                                         title=ica_title % 'ecg',
                                         show=is_show)

        # Pick the five largest ecg_scores and plot them
        show_picks = np.abs(ecg_scores).argsort()[::-1][:5]

        # Plot estimated latent sources given the unmixing matrix.
        fig_ecg_ts = ica.plot_sources(raw, show_picks,
                                      title=ica_title % 'ecg' + ' in 30s',
                                      start=0, stop=30, show=is_show)

        # topoplot of unmixing matrix columns
        fig_ecg_comp = ica.plot_components(show_picks,
                                           title=ica_title % 'ecg',
                                           colorbar=True, show=is_show)

        # plot ECG sources + selection
        fig_ecg_src = ica.plot_sources(ecg_evoked, show=is_show)
        fig = [fig_ecg_scores, fig_ecg_ts, fig_ecg_comp, fig_ecg_src]
        report.add_figs_to_section(fig,
                                   captions=['Scores of ICs related to ECG',
                                             'Time Series plots of ICs (ECG)',
                                             'TopoMap of ICs (ECG)',
                                             'Time-locked ECG sources'],
                                             section='ICA - ECG')
    # -------------------- end generate report for ECG ---------------------- #

    # -------------------------- Generate report for EoG -------------------- #
    # check how many EoG ch we have
    if set(eog_ch_name).issubset(set(raw.info['ch_names'])):
        fig_eog_scores = ica.plot_scores(eog_scores, exclude=eog_inds,
                                         title=ica_title % 'eog', show=is_show)

        report.add_figs_to_section(fig_eog_scores,
                                   captions=['Scores of ICs related to EOG'],
                                   section='ICA - EOG')

        n_eogs = np.shape(eog_scores)
        if len(n_eogs) > 1:
            n_eog0 = n_eogs[0]
            show_picks = [np.abs(eog_scores[i][:]).argsort()[::-1][:5]
                          for i in range(n_eog0)]
            for i in range(n_eog0):
                fig_eog_comp = ica.plot_components(show_picks[i][:],
                                                   title=ica_title % 'eog',
                                                   colorbar=True, show=is_show)

                fig = [fig_eog_comp]
                report.add_figs_to_section(fig,
                                           captions=['Scores of EoG ICs'],
                                           section='ICA - EOG')
        else:
            show_picks = np.abs(eog_scores).argsort()[::-1][:5]
            fig_eog_comp = ica.plot_components(show_picks,
                                               title=ica_title % 'eog',
                                               colorbar=True, show=is_show)

            fig = [fig_eog_comp]
            report.add_figs_to_section(fig, captions=['TopoMap of ICs (EOG)'],
                                       section='ICA - EOG')

        fig_eog_src = ica.plot_sources(eog_evoked,
                                       show=is_show)

        fig = [fig_eog_src]
        report.add_figs_to_section(fig, captions=['Time-locked EOG sources'],
                                   section='ICA - EOG')
    # ----------------- end generate report for EoG ---------- #
    ic_nums = list(range(ica.n_components_))
    fig = ica.plot_components(picks=ic_nums, show=False)
    report.add_figs_to_section(fig, captions=['All IC topographies'],
                               section='ICA - muscles')

    fig = ica.plot_sources(raw, start=0, stop=None, show=False,
                           title='All IC time series')
    report.add_figs_to_section(fig, captions=['All IC time series'],
                               section='ICA - muscles')

    psds_fig = []
    captions_psd = []
    ica_src = ica.get_sources(raw)
    for i_ic in ic_nums:

        psds, freqs = psd_multitaper(ica_src, picks=i_ic, fmax=140,
                                     tmax=60)
        psds = np.squeeze(psds)

        f, ax = plt.subplots()
        psds = 10 * np.log10(psds)

        ax.plot(freqs, psds, color='k')
        ax.set(title='PSD', xlabel='Frequency',
               ylabel='Power Spectral Density (dB)')

        psds_fig.append(f)
        captions_psd.append('IC #' + str(i_ic))

    report.add_figs_to_section(figs=psds_fig, captions=captions_psd,
                               section='ICA - muscles')

    report_filename = os.path.join(basename + "-report.html")
    print(('******* ' + report_filename))
    report.save(report_filename, open_browser=False, overwrite=True)
    return report_filename


def _create_events(raw, epoch_length):
    """Create events to split raw into epochs."""
    file_length = raw.n_times
    first_samp = raw.first_samp
    sfreq = raw.info['sfreq']
    n_samp_in_epoch = int(epoch_length * sfreq)

    n_epochs = int(file_length // n_samp_in_epoch)

    events = []
    for i_epoch in range(n_epochs):
        events.append([first_samp + i_epoch * n_samp_in_epoch, int(0), int(0)])
    events = np.array(events)
    return events


def _create_epochs(fif_file, ep_length):
    """Split raw .fif file into epochs.

    Splitted epochs have a length ep_length with rejection criteria.
    """
    flat = None
    reject = None

    raw = read_raw_fif(fif_file)
    picks = pick_types(raw.info, meg=True, ref_meg=False, eeg=False)
    if raw.times[-1] >= ep_length:
        events = _create_events(raw, ep_length)
    else:
        raise Exception('File {} is too short!'.format(fif_file))

    epochs = Epochs(raw, events=events, tmin=0, tmax=ep_length,
                    preload=True, picks=picks, proj=False,
                    flat=flat, reject=reject, baseline=None)

    _, base, ext = split_filename(fif_file)
    savename = os.path.abspath(base + '-epo' + ext)
    epochs.save(savename, overwrite=True)
    return savename


def _define_epochs(
        fif_file, t_min, t_max, events_id, events_file='',
        decim=1, data_type='meg', baseline=(None, 0)):
    """Split raw .fif file into epochs depending on events file.

    Splitted epochs have a length ep_length with rejection criteria.
    """
    raw = read_raw_fif(fif_file, preload=True)
    raw.set_eeg_reference(ref_channels='average', projection=True)

    reject = _create_reject_dict(raw.info, data_type)
    if data_type == 'meg':
        picks = pick_types(raw.info, meg=True, ref_meg=False, eog=True,
                           stim=True, exclude='bads')
    elif data_type == 'eeg':
        picks = pick_types(raw.info, meg=False, eeg=True, eog=True,
                           stim=False, exclude='bads')

    data_path, base, ext = split_filename(fif_file)

    if events_file:
        events_fpath = glob.glob(op.join(data_path, events_file))
        print('*** {} ***'.format(events_fpath[0]))
        events = read_events(events_fpath[0])
    else:
        events = find_events(raw)

    # TODO -> use autoreject ?
    # reject_tmax = 0.8  # duration we really care about
    epochs = Epochs(raw, events, events_id, t_min, t_max, proj=True,
                    picks=picks, baseline=baseline, decim=decim, preload=True)
    epochs.drop_bad(reject=reject)
    fig = epochs.plot_drop_log(show=False)
    fig_fpath = os.path.abspath(base + '-epo-dropped.jpg')

    fig.savefig(fig_fpath, facecolor='black')
    
    good_events_file = os.path.join(data_path, 'good_events.txt')
    np.savetxt(good_events_file, epochs.events)

    # TODO -> decide where to save...
    savename = os.path.abspath(base + '-epo' + ext)
    # savename = os.path.join(data_path, base + '-epo' + ext)
    print(epochs.info)
    epochs.save(savename, overwrite=True)

    return savename


def _compute_evoked(fif_file, events_id, condition=None):
    """Compute evoked data depending on events file."""
    epochs = read_epochs(fif_file)
    # info = epochs.info

    if events_id != condition and condition:
        events_name = condition
    else:
        events_name = events_id

    print('*************** {}'.format(condition))
    print('*************** {}'.format(events_name))
    evoked = [epochs[k].average() for k in events_name]

    _, basename, _ = split_filename(fif_file)
    if 'epo' in basename:
        basename = basename.replace('-epo', '')

    savename = op.abspath(basename + '-ave.fif')
    write_evokeds(savename, evoked)

    return savename

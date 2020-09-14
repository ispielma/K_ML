from labscript_utils import import_or_reload
from labscript import *
from labscriptlib.common.functions import *

import_or_reload('labscriptlib.rb_chip_mainline.connectiontable')

from labscriptlib.rb_chip_mainline.scripts import stage, pulse_beam

from labscriptlib.rb_chip_mainline.transport import (
    Transport,
    piecewise_minjerk_and_coast,
    make_coils,
    lru_cache,
    linear,
    solve_two_coil,
)

from scipy.interpolate import interp1d

coils = make_coils(
    MOT_coils_spacing_factor=MOT_coils_spacing_factor,
    science_coils_spacing_factor=science_coils_spacing_factor,
    inner_coils_spacing_factors=(
        inner_coils_0_spacing_factor,
        inner_coils_1_spacing_factor,
        inner_coils_2_spacing_factor,
        inner_coils_3_spacing_factor,
    ),
    outer_coils_spacing_factors=(
        outer_coils_0_spacing_factor,
        outer_coils_1_spacing_factor,
        outer_coils_2_spacing_factor,
        outer_coils_3_spacing_factor,
        outer_coils_4_spacing_factor,
    ),
)

transport_trajectory = piecewise_minjerk_and_coast(
    0,
    transport_time,
    0,
    coils['science'].y - move_y_final_offset,
    1.0,  # Relative duration of initial accelerating segment, 1 by definition
    (move_dt_rel_1, 1.0),  # vrel in first coasting segment, 1 by definition
    move_dt_rel_2,
    (move_dt_rel_3, move_v_rel_3),
    move_dt_rel_4,
    (move_dt_rel_5, move_v_rel_5),
    move_dt_rel_6,
)

# The final transport gradient is parametrised by the current required to produce it.
# This is to ensure optimisation cannot change the actual gradient here by manipulating
# the modelled coil spacing.
move_grad_final = coils['science'].dB(coils['science'].r0, move_final_current, 'z')[2]

transport_gradient_ramp = interp1d(
    np.linspace(0, transport_time, 10),
    [
        move_grad_0,
        move_grad_1,
        move_grad_2,
        move_grad_3,
        move_grad_4,
        move_grad_5,
        move_grad_6,
        move_grad_7,
        move_grad_8,
        move_grad_final,
    ],
    'cubic',
    fill_value='extrapolate',
)

transport = Transport(
    coils=coils,
    y_of_t=transport_trajectory,
    t_final=transport_time,
    dBz_dz_of_t=transport_gradient_ramp,
    initial_switch_y_frac=initial_switch_y_frac,
    d2beta_initial_dy2_0=d2beta_initial_dy2_0,
    d2beta_initial_dy2_1=d2beta_initial_dy2_1,
    final_switch_y_frac=final_switch_y_frac,
    d2beta_final_dy2_1=d2beta_final_dy2_1,
    d2beta_final_dy2_0=d2beta_final_dy2_0,
)


@stage
def prep(t, **kwargs):
    """Define initial state of system. All settable Hardware 
    should be set here with no exceptions. """
    # UV Soak -- build Rb partial pressure before MOT
    UV_LED.go_high(t)
    
    # Prepare cooling + repump with AOMs + shutters
    AOM_MOT_repump.go_high(t)
    shutter_MOT_repump.go_high(t)
    AOM_MOT_cooling.go_high(t)
    shutter_MOT_cooling.go_high(t)
    AOM_probe_2.go_high(t)
    
    # All cameras trigger on "falling" so...
    camera_trigger_0.go_high(t)    
    camera_trigger_1.go_high(t)
    camera_trigger_2.go_high(t)
    camera_trigger_3.go_high(t)

    # Kepco control mode:
    #   0 & 0 = Both off
    #   0 & 1 = Top bias control
    #   1 & 0 = Both off
    #   1 & 1 = Bottom bias control
    kepco_enable_0.go_high(t)
    kepco_enable_1.go_high(t)
    
    # Enable bias fields
    x_bias.constant(t, idle_x_bias, units='A')
    y_bias.constant(t, idle_y_bias, units='A')
    z_bias.constant(t, idle_z_bias, units='A')
    offset.constant(t, idle_z_offset)  
    
    # Beam intensity controls
    MOT_repump.constant(t,  idle_repump_intensity)
    MOT_cooling.constant(t, idle_cooling_intensity)
    # The following beams need their AOMs to settle (warmup)
    probe_1.constant(t, probe_1_intensity) 
    probe_2.constant(t, probe_2_intensity) 
    long_trap.constant(t, 0.0) 
    dipole_intensity.constant(t, idle_dipole_intensity)
    dipole_split.constant(t, idle_dipole_split)
    dipole_switch.go_low(t) 
    
    # Select MOT quadrupole supply lines
    curent_supply_2_select_line0.go_low(t)
    curent_supply_2_select_line1.go_low(t)  
    
    # Enable MOT agilent supply, set currents
    curent_supply_1_enable.go_low(t)
    curent_supply_2_enable.go_high(t)
    curent_supply_3_enable.go_low(t)
    curent_supply_4_enable.go_low(t)  
    transport_current_1.constant(t, 0.0, units='A')
    transport_current_2.constant(t, idle_MOT_quad_current, units='A')
    transport_current_3.constant(t, 0.0, units='A')
    transport_current_4.constant(t, 0.0, units='A')
    
   
    # shutter_greenbeam.go_high(t)
    green_beam.go_low(t)
    AOM_green_beam.constant(t, 0.0)
    green_servo_trigger.go_low(t)
    long_trap_switch.go_low(t)
    
    # Frequency lock offsets
    MOT_lock.setfreq(t,  idle_beatnote_freq, units='MHz')
    MOT_lock.setamp(t,  0.7077) # 0 dBm
    
    # Raman detunings
    AOM_Raman_1.setfreq(t, 80, units='MHz')
    AOM_Raman_1.setamp(t, 0.5)

    #static channel
    AOM_Raman_2.setfreq(80, units='MHz')
    AOM_Raman_2.setamp(0.7077)


    mixer_raman_1.constant(t,0.0)
    mixer_raman_2.constant(t,0.0)
    raman_1.go_low(t)
    raman_2.go_low(t) 

    shutter_raman1.go_low(t)
    shutter_raman2.go_low(t)
    
    # RF + uWave drives
    RF_evap.setfreq(t,  rf_evaporation_initial_frequency, units='MHz')
    RF_evap.setamp(t, 0.0)
    uwave1.setfreq(t, 100, units='MHz')
    uwave1.setamp(t, 0.0)
    
    # RF + uWave fields (switches and mixers)
    RF_switch_0.go_low(t)
    RF_mixer1.constant(t, 0)
    RF_mixer3.constant(t, 0)
    
    uWave_switch_0.go_low(t)
    microwave_attenuator.constant(t, 6.0) # Fully attenuated

    # Acquisition triggers
    scope_trigger_0.go_low(t)
    scope_trigger_1.go_high(t)
    fluxgate_trig.go_low(t)

    andor_ccd_trigger.go_low(t)

    return prep_time

@stage
def MOT(t, **kwargs):
    """ Load a MOT with a fraction of the time having UV shone"""
    if make_small_MOT:
        duration = MOT_time / 100
    else:
        duration = MOT_time
  
    transport_current_2.constant(t, MOT_quad_current, units='A')

    if not UV_soak:
        UV_LED.go_low(t + UV_MOT_fraction * duration)

    # Sample MOT fluorescence before and during MOT loading
    # scope_trigger_0.go_high(t)
    return duration
    
@stage    
def compressed_MOT(t, **kwargs):
    """ Starting with a MOT, load into the compressed MOT by enabling the quadrupole
    field, preps for subDoppler cooling """
    # Ramp cooling + repump down (why?)    
    if make_small_MOT:
        duration = compressed_MOT_time / 100
    else:
        duration = compressed_MOT_time

    MOT_repump.customramp(t, 
        duration, 
        CubicRamp, 
        MOT_repump_intensity, 
        compressed_MOT_repump_intensity, 
        samplerate=1/compressed_MOT_step,
    )
    MOT_cooling.constant(t, compressed_MOT_cooling_intensity)
    
    # Raise quad fields and set center with bias fields:
    transport_current_2.customramp(t, 
        duration, 
        CubicRamp, 
        idle_MOT_quad_current,
        compressed_MOT_quad_current,
        initial_deriv=0,
        final_deriv=compressed_MOT_quad_current_final_deriv,
        samplerate=1/compressed_MOT_step, 
        units='A',
    )
    
    x_bias.customramp(
        t,
        duration,
        CubicRamp,
        idle_x_bias,
        compressed_MOT_x_bias,
        samplerate=1/compressed_MOT_step, 
        units='A',
    )
    y_bias.customramp(
        t,
        duration,
        CubicRamp,
        idle_y_bias,
        compressed_MOT_y_bias,
        samplerate=1/compressed_MOT_step, 
        units='A',
    )
    z_bias.customramp(
        t,
        duration,
        CubicRamp,
        idle_z_bias,
        compressed_MOT_z_bias,
        samplerate=1/compressed_MOT_step, 
        units='A',
    )

    # Prepare frequency for optical molasses
    MOT_lock.frequency.customramp(t, 
        duration, 
        CubicRamp, 
        compressed_MOT_frequency, 
        molasses_start_frequency, 
        samplerate=1/compressed_MOT_step, 
        units='MHz')

    return duration
    
@stage
def optical_molasses(t, **kwargs):
    """ Sub-Doppler cooling stage, starting from a cMOT, 
    drop the quadrupole field down to 0 and allow molasses 
    to take place by sweeping the detuning """ 
    # Drop quadrupole current and reposition center in 
    # preparation for magnetic trapping (quad supply is disabled)
    curent_supply_2_enable.go_low(t)
    transport_current_2.constant(t, MOT_quad_current, units='A')

    x_bias.constant(t, molasses_x_bias, units='A')
    y_bias.constant(t, molasses_y_bias, units='A')
    z_bias.constant(t, molasses_z_bias, units='A')
    
    # Shine optical molasses
    MOT_repump.constant(t, molasses_repump_intensity)
    MOT_lock.frequency.customramp(t, 
        molasses_time, 
        ExpRamp, 
        molasses_start_frequency, 
        molasses_end_frequency, 
        molasses_detuning_ramp_width, 
        samplerate=1/molasses_step, 
        units='MHz')

    return molasses_time
    
@stage
def prep_optical_pumping(t, **kwargs):
    """ Prepare for optical pumping into 
    F=2, mF=2, before magnetic trap."""
    # Turn all the light down, except for optical_pumping
    # Won't need cooling light until next cycle...
    AOM_MOT_cooling.go_low(t)
    MOT_cooling.constant(t, 0.0)
    shutter_MOT_cooling.go_low(t)
    # Will need repump, so keep AO command up
    AOM_MOT_repump.go_low(t)
    MOT_repump.constant(t, optical_pumping_repump_intensity)

    # Prep optical pumping
    shutter_optical_pumping.go_high(t - srs_shutter_delay_time)
    optical_pumping.constant(t, optical_pumping_intensity)
    
    # Setup bias field (mostly along z)
    x_bias.constant(t, optical_pumping_x_bias, units='A')
    y_bias.constant(t, optical_pumping_y_bias, units='A')
    z_bias.constant(t, optical_pumping_z_bias, units='A')
    
    # Should the frequency change here? 
    #MOT_lock.frequency.constant(t, ResFreq + EndFreqMol, units='MHz')
    MOT_lock.frequency.constant(t, optical_pumping_frequency, units='MHz')

    return optical_pumping_settle_time

@stage
def optical_pump_2_2(t, **kwargs):
    """ Optical pumping into 2, 2 """
    AOM_MOT_repump.go_high(t)
    AOM_optical_pumping.go_high(t)
    return optical_pumping_time
    
@stage
def magnetic_trap(t, **kwargs):
    """ Turn all light off, load 2,2 atoms 
    into a magnetic trap """

    transport_oscilloscope_trigger.trigger(t, duration=0.1)

    # First the repump
    AOM_MOT_repump.go_low(t)
    MOT_repump.constant(t, 0)
    shutter_MOT_repump.go_low(t)
    
    # Then the optical pumping
    # NOTE: The fiber injection for op-pump should be done with a cold AOM
    AOM_optical_pumping.go_low(t)
    shutter_optical_pumping.go_low(t)
    optical_pumping.constant(t, 0.0)
       
    # Ramp magnetic trap
    curent_supply_2_enable.go_high(t)
    curent_supply_3_enable.go_high(t)

    initial_transport_current = 90

    transport_current_2.customramp(
        t,
        magnetic_trap_MOT_time,
        HalfGaussRamp,
        magnetic_trap_MOT_quad_current,
        initial_transport_current,
        magnetic_trap_MOT_ramp_width,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )

    x_bias.customramp(t, 
        magnetic_trap_MOT_time, 
        HalfGaussRamp, 
        magnetic_trap_MOT_x_bias,
        molasses_x_bias, 
        magnetic_trap_MOT_ramp_width, 
        samplerate=1/magnetic_trap_MOT_step, 
        units='A'
    )
    y_bias.customramp(t, 
        magnetic_trap_MOT_time, 
        HalfGaussRamp, 
        magnetic_trap_MOT_y_bias,
        molasses_y_bias, 
        magnetic_trap_MOT_ramp_width,
        samplerate=1/magnetic_trap_MOT_step, 
        units='A'
    )
    z_bias.customramp(t, 
        magnetic_trap_MOT_time, 
        HalfGaussRamp, 
        magnetic_trap_MOT_z_bias,
        molasses_z_bias, 
        magnetic_trap_MOT_ramp_width, 
        samplerate=1/magnetic_trap_MOT_step, 
        units='A'
    )
    
    # These are initially ON to keep AOMs warm, can they be turned off later? 
    AOM_probe_2.go_low(t)
    probe_1.constant(t, 0.0)

    return magnetic_trap_MOT_time


@stage
def magnetic_transport(t, **kwargs):

    transport_oscilloscope_trigger.trigger(t, duration=0.1)

    # Turn off light

    # First the repump
    AOM_MOT_repump.go_low(t)
    MOT_repump.constant(t, 0)
    shutter_MOT_repump.go_low(t)
    
    # Then the optical pumping
    # NOTE: The fiber injection for op-pump should be done with a cold AOM
    AOM_optical_pumping.go_low(t)
    shutter_optical_pumping.go_low(t)
    optical_pumping.constant(t, 0.0)

    # Snap bias filds on for caputure, then ramp them back to their nulling values
    x_bias.customramp(t, 
        magnetic_trap_MOT_time, 
        HalfGaussRamp, 
        magnetic_trap_MOT_x_bias,
        molasses_x_bias, 
        magnetic_trap_MOT_ramp_width, 
        samplerate=1/magnetic_trap_MOT_step, 
        units='A'
    )
    y_bias.customramp(t, 
        magnetic_trap_MOT_time, 
        HalfGaussRamp, 
        magnetic_trap_MOT_y_bias,
        molasses_y_bias, 
        magnetic_trap_MOT_ramp_width,
        samplerate=1/magnetic_trap_MOT_step, 
        units='A'
    )
    z_bias.customramp(t, 
        magnetic_trap_MOT_time, 
        HalfGaussRamp, 
        magnetic_trap_MOT_z_bias,
        molasses_z_bias, 
        magnetic_trap_MOT_ramp_width, 
        samplerate=1/magnetic_trap_MOT_step, 
        units='A'
    )
    
    # These are initially ON to keep AOMs warm, can they be turned off later? 
    AOM_probe_2.go_low(t)
    probe_1.constant(t, 0.0)


    # We don't need current supply 1 yet, since we are not using the push coil.
    curent_supply_2_enable.go_high(t)
    curent_supply_3_enable.go_high(t)
    curent_supply_4_enable.go_high(t)

    t_switch = transport.t_switchover

    # Select which current supply powers which coil(pair) at each switchover time:
    curent_supply_1_select_line0.go_high(t + t_switch[0])
    curent_supply_1_enable.go_high(t + t_switch[0])

    curent_supply_2_select_line0.go_high(t + t_switch[1])

    curent_supply_3_select_line0.go_high(t + t_switch[2])

    curent_supply_4_select_line0.go_high(t + t_switch[3])

    curent_supply_1_select_line0.go_low(t + t_switch[4])
    curent_supply_1_select_line1.go_high(t + t_switch[4])

    curent_supply_2_select_line0.go_low(t + t_switch[5])
    curent_supply_2_select_line1.go_high(t + t_switch[5])

    curent_supply_3_select_line0.go_low(t + t_switch[6])
    curent_supply_3_select_line1.go_high(t + t_switch[6])

    curent_supply_4_select_line0.go_low(t + t_switch[7])
    curent_supply_4_enable.go_low(t + t_switch[7])
    
    # Switch bias field control over to top servo.
    kepco_enable_0.go_low(t + t_switch[7])
    x_bias.customramp(
        t + t_switch[7],
        t_switch[8] - t_switch[7],
        LineRamp,
        molasses_x_bias,
        x_transport_shim_bias,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )
    y_bias.customramp(
        t + t_switch[7],
        t_switch[8] - t_switch[7],
        LineRamp,
        molasses_y_bias,
        y_transport_shim_bias,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )
    z_bias.customramp(
        t + t_switch[7],
        t_switch[8] - t_switch[7],
        LineRamp,
        molasses_z_bias,
        z_transport_shim_bias,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )


    curent_supply_1_select_line1.go_low(t + t_switch[8])
    curent_supply_1_enable.go_low(t + t_switch[8])
    curent_supply_4_select_line0.go_high(t + t_switch[8])
    curent_supply_4_select_line1.go_high(t + t_switch[8])
    curent_supply_4_enable.go_high(t + t_switch[8])

    curent_supply_2_select_line1.go_low(t + t_switch[9])
    curent_supply_2_enable.go_low(t + t_switch[9])

    RF_evap.setfreq(t + t_switch[9],  rf_evaporation_initial_frequency, units='MHz')
    RF_evap.setamp(t + t_switch[9], rf_evaporation_initial_amplitude) #1.000

    # Start slight vertical decompress shift
    y_bias.customramp(
        t + t_switch[9],
        transport_time - t_switch[9],
        LineRamp,
        y_transport_shim_bias,
        y_top_shim_bias,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )

    transport_current_1.customramp(
        t,
        transport_time,
        transport.currents_for_channel,
        1,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )
    transport_current_2.customramp(
        t,
        transport_time,
        transport.currents_for_channel,
        2,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )
    transport_current_3.customramp(
        t,
        transport_time,
        transport.currents_for_channel,
        3,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )
    transport_current_4.customramp(
        t,
        transport_time,
        transport.currents_for_channel,
        4,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )
    
    return transport_time


@stage
def rf_evaporate(t, **kwargs):
          
    # ni_usb_6343_0 analog outputs:
    transport_current_2.constant(t, 0, units='A')

    # Linear ramp to the final position
    magnetic_transport_ramp = linear(
        0,
        rf_evaporation_time,
        coils['science'].y - move_y_final_offset,
        coils['science'].y,
    )

    @lru_cache()
    def current_3(t_rel, duration):
        y = magnetic_transport_ramp(t_rel)
        (current_3_per_grad, _), _ = solve_two_coil(y, coils[-2], coils[-1])
        return current_3_per_grad * move_grad_final

    @lru_cache()
    def current_4(t_rel, duration):
        y = magnetic_transport_ramp(t_rel)
        (_, current_4_per_grad), _ = solve_two_coil(y, coils[-2], coils[-1])
        return current_4_per_grad * move_grad_final

    transport_current_3.customramp(t, rf_evaporation_time, current_3, samplerate=1/rf_evaporation_step, units='A')
    transport_current_4.customramp(t, rf_evaporation_time, current_4, samplerate=1/rf_evaporation_step, units='A')

    # ni_pci_6733_1 analog outputs:
    RF_mixer1.constant(t, rf_evaporation_mixer_voltage)
    RF_switch_0.go_high(t)
    
    # novatechdds9m_1 channel outputs:
    if cripple_rf_evaporation:
        assert cripple_rf_evaporation_time < rf_evaporation_time
        RF_evap.frequency.ramp(
            t,
            cripple_rf_evaporation_time,
            rf_evaporation_initial_frequency,
            rf_evaporation_crippled_frequency,
            samplerate=1 / novatech_min_ramp_step,
            units='MHz',
        )
        RF_evap.frequency.ramp(
            t + cripple_rf_evaporation_time,
            rf_evaporation_time - cripple_rf_evaporation_time,
            rf_evaporation_crippled_frequency,
            rf_evaporation_final_frequency,
            samplerate=1 / rf_evaporation_step,
            units='MHz',
        )
    else:
        RF_evap.frequency.ramp(
            t,
            rf_evaporation_time,
            rf_evaporation_initial_frequency,
            rf_evaporation_final_frequency,
            samplerate=1 / rf_evaporation_step,
            units='MHz',
        )
    
    y_bias.customramp(
        t,
        rf_evaporation_time,
        LineRamp,
        y_top_shim_bias,
        y_rf_shim_bias,
        samplerate=1 / rf_evaporation_step,
        units='A',
    )
    
    if dipole_evaporate:
        dipole_switch.go_high(t)  
        dipole_intensity.constant(t, initial_dipole_intensity)
        dipole_split.constant(t, initial_dipole_split)
    
    return rf_evaporation_time


@stage
def magnetic_trap_off(t, imaging='x', **kwargs):
    transport_current_1.constant(t, -1, units='A')
    transport_current_2.constant(t, -1, units='A')
    transport_current_3.constant(t, -1, units='A')

    # Turn everything off
    dipole_intensity.constant(t, 0.0)
    dipole_switch.go_low(t)

    RF_evap.setfreq(t + 10*ms,  rf_evaporation_initial_frequency)
    RF_evap.setamp(t, 0.000)
    RF_switch_0.go_low(t)
    RF_mixer1.constant(t, 0)

    if use_new_transport:
        # How much current is required to make move_grad_final of gradient using the
        # science coil?
        _, _, gradient_per_amp = coils['science'].dB(
            (0, coils['science'].y, 0), I=1, s='z'
        )
        final_transport_current = move_grad_final / gradient_per_amp
    else:
        final_transport_current = 70

    transport_current_4.ramp(
        t,
        magnetic_trap_off_time,
        final_transport_current,
        30,
        units='A',
        samplerate=1 / novatech_min_ramp_step,
    )

    transport_current_4.constant(t + magnetic_trap_off_time, -1, units='A')

    curent_supply_1_enable.go_low(t + magnetic_trap_off_time)
    curent_supply_2_enable.go_low(t + magnetic_trap_off_time)
    curent_supply_3_enable.go_low(t + magnetic_trap_off_time)
    curent_supply_4_enable.go_low(t + magnetic_trap_off_time)
    curent_supply_3_select_line0.go_low(t)
    curent_supply_3_select_line1.go_low(t)

    # Prepare for imaging:
    if 'x' in imaging:
        imaging_bias = [
            x_top_imaging_x_bias,
            x_top_imaging_y_bias,
            x_top_imaging_z_bias,
        ]
        detuning = x_top_imaging_frequency
    elif 'z' in imaging:
        imaging_bias = [
            z_top_imaging_x_bias,
            z_top_imaging_y_bias,
            z_top_imaging_z_bias,
        ]
        detuning = z_top_imaging_frequency

    kepco_enable_0.go_low(t)
    x_bias.constant(t, imaging_bias[0], units='A')
    y_bias.constant(t, imaging_bias[1], units='A')
    z_bias.constant(t, imaging_bias[2], units='A')

    MOT_lock.frequency.constant(t - beatnote_lock_settle_time, detuning, units='MHz')

    AOM_MOT_repump.go_low(t)
    MOT_repump.constant(t, 0.0)
    AOM_probe_1.go_low(t)
    probe_1.constant(t, 0.0)
    return magnetic_trap_off_time

@stage
def decompress(t, **kwargs):
    decompress_time = 0

    # Stop rf evaporation
    RF_evap.setfreq(t + 10*ms,  rf_evaporation_initial_frequency)
    RF_evap.setamp(t, 0.000)
    RF_switch_0.go_low(t)
    RF_mixer1.constant(t, 0)

    y_bias.customramp(
        t,
        initial_decompress_time,
        LineRamp,
        y_rf_shim_bias,
        y_decompress_initial_bias,
        samplerate=1 / decompress_step,
        units='A',
    )

    transport_current_4.customramp(
        t,
        initial_decompress_time,
        LineRamp,
        move_final_current,
        intermediate_decompress_current,
        samplerate=1 / decompress_step,
        units='A',
    )

    decompress_time += initial_decompress_time

    # Intermediate decompression
    t += initial_decompress_time

    transport_current_4.customramp(
        t,
        intermediate_decompress_time,
        LineRamp,
        intermediate_decompress_current,
        final_decompress_current,
        samplerate=1 / decompress_step,
        units='A',
    )
    
    y_bias.customramp(
        t,
        intermediate_decompress_time,
        LineRamp,
        y_decompress_initial_bias,
        y_decompress_intermediate_bias,
        samplerate=1 / decompress_step,
        units='A',
    )

    decompress_time += intermediate_decompress_time

    # Final decompression
    t += intermediate_decompress_time

    dipole_intensity.customramp(
        t,
        final_decompress_time,
        ExpRamp,
        initial_dipole_intensity,
        intermediate_dipole_intensity,
        initial_dipole_tau,
        samplerate=1 / (2*decompress_step),
    )
    dipole_split.customramp(
        t,
        final_decompress_time,
        ExpRamp,
        initial_dipole_split,
        intermediate_dipole_split,
        initial_dipole_tau,
        samplerate=1 / (2*decompress_step),
    )
        
    transport_current_4.customramp(
        t,
        final_decompress_time,
        ExpRamp,
        final_decompress_current,
        0.0,
        initial_dipole_tau,
        samplerate=1 / (2*decompress_step),
        units='A',
    )
    
    y_bias.customramp(
        t,
        final_decompress_time,
        LineRamp,
        y_decompress_intermediate_bias,
        y_decompress_final_bias,
        samplerate=1 / (2*decompress_step),
        units='A',
    )
    
    decompress_time += final_decompress_time

    t += final_decompress_time
    curent_supply_4_select_line0.go_low(t)
    curent_supply_4_select_line1.go_low(t)
    curent_supply_4_enable.go_low(t)

    z_bias.constant(t, z_transport_shim_bias, units='A')
    decompress_time += bias_settle_time
    t += bias_settle_time

    return decompress_time

@stage
def uwave_arp(t, mode='state_preparation', **kwargs):
    """ Adiabatic rapid passage for 2,2 and 1,1. The 
    'state_preparation' mode turns uwaves off in a ramp
    while any other mode is a snap off. """

    uwave_arp_time = 0

    # Settle initial bias field (prep manifold)
    z_bias.customramp(
        t,
        ramp_arp_bias_time,
        LineRamp,
        idle_z_bias,
        uwave_arp_initial_z_bias,
        samplerate=1 / uwave_arp_step,
        units='A',
    )

    uwave_arp_time += ramp_arp_bias_time
    t += ramp_arp_bias_time

    # Settle uwave fields (open gap)
    uwave1.setfreq(t-200*us, uwave_arp_frequency, units='MHz')
    uwave1.setamp(t-200*us, uwave_arp_amplitude)
    uWave_switch_0.go_high(t)

    microwave_attenuator.customramp(
        t,
        ramp_uwave_on_time,
        LineRamp,
        6.0,
        uwave_attenuation,
        samplerate=1 / uwave_arp_step,
    )

    uwave_arp_time += ramp_uwave_on_time
    t += ramp_uwave_on_time

    uwave_mixer1.customramp(
        t,
        ramp_uwave_on_time,
        LineRamp,
        0.0,
        uwave_mixer_amplitude,
        samplerate=1 / uwave_arp_step,
    )
   
    uwave_arp_time += ramp_uwave_on_time
    t += ramp_uwave_on_time

    # Sweep bias field through resonance (ARP)
    z_bias.customramp(
        t,
        ramp_arp_resonance_time,
        LineRamp,
        uwave_arp_initial_z_bias,
        uwave_arp_final_z_bias,
        samplerate=1 / uwave_arp_step,
        units='A',
    )
  
    uwave_arp_time += ramp_arp_resonance_time
    t += ramp_arp_resonance_time

    # Turn off: for state preparation do ramp down,
    # but for resonance do a snap off

    if mode == 'state_preparation':

        # First the uwave fields (gap)
        uwave_mixer1.customramp(
            t,
            ramp_uwave_off_time,
            LineRamp,
            uwave_mixer_amplitude,
            0.0,
            samplerate=1 / uwave_arp_step,
        )

        uwave_arp_time += ramp_uwave_on_time
        t += ramp_uwave_on_time

        microwave_attenuator.customramp(
            t,
            ramp_uwave_off_time,
            LineRamp,
            uwave_attenuation,
            6.0,
            samplerate=1 / uwave_arp_step,
        )

        uwave_arp_time += ramp_uwave_off_time
        t += ramp_uwave_off_time

        uWave_switch_0.go_low(t)

        # Then the bias field (manifold)
        z_bias.customramp(
            t,
            ramp_arp_bias_time,
            LineRamp,
            uwave_arp_final_z_bias,
            idle_z_bias,
            samplerate=1 / uwave_arp_step,
            units='A',
        )

        uwave_arp_time += ramp_arp_bias_time
        t += ramp_arp_bias_time


    elif mode == 'resonance':
        uwave_arp_time += ramp_arp_bias_time
        t += ramp_arp_bias_time

        microwave_attenuator.constant(t, 6.0)
        uwave_mixer1.constant(t, 0.0)
        uWave_switch_0.go_low(t)

    
    return uwave_arp_time

@stage
def dipole_evaporate(t, **kwargs):
    dipole_intensity.customramp(
        t,
        dipole_evaporation_time,
        LineRamp,
        intermediate_dipole_intensity,
        final_dipole_intensity,
        samplerate=1 / dipole_evaporate_step,
    )
    dipole_split.customramp(
        t,
        dipole_evaporation_time,
        LineRamp,
        intermediate_dipole_split,
        final_dipole_split,
        samplerate=1 / dipole_evaporate_step,
    )

    # x_bias.constant(t, top_zero_x_bias, units='A')
    # y_bias.constant(t, top_zero_y_bias, units='A')
    
    return dipole_evaporation_time

@stage
def rf_arp(t, mode='state_preparation', **kwargs):
    """ Adiabatic rapid passage for mF states. The 
    'state_preparation' mode turns rf off in a ramp
    while any other mode is a snap off. """

    rf_arp_time = 0

    # Settle initial bias field (prep manifold)
    z_bias.customramp(
        t,
        ramp_arp_bias_time,
        LineRamp,
        idle_z_bias,
        rf_arp_initial_z_bias,
        samplerate=1 / rf_arp_step,
        units='A',
    )

    rf_arp_time += ramp_arp_bias_time
    t += ramp_arp_bias_time

    # Settle rf fields (open gap)
    RF_evap.setfreq(t-200*us, rf_arp_frequency, units='MHz')
    RF_evap.setamp(t-200*us, rf_arp_amplitude)
    RF_switch_0.go_high(t)

    RF_mixer1.customramp(
        t,
        ramp_rf_on_time,
        LineRamp,
        0.0,
        rf_mixer_amplitude,
        samplerate=1 / rf_arp_step,
    )
   
    rf_arp_time += ramp_rf_on_time
    t += ramp_rf_on_time

    # Sweep bias field through resonance (ARP)
    z_bias.customramp(
        t,
        ramp_arp_resonance_time,
        LineRamp,
        rf_arp_initial_z_bias,
        rf_arp_final_z_bias,
        samplerate=1 / rf_arp_step,
        units='A',
    )
  
    rf_arp_time += ramp_arp_resonance_time
    t += ramp_arp_resonance_time

    # Turn off: for state preparation do ramp down,
    # but for resonance do a snap off

    if mode == 'state_preparation':

        RF_mixer1.customramp(
            t,
            ramp_rf_off_time,
            LineRamp,
            rf_mixer_amplitude,
            0.0,
            samplerate=1 / rf_arp_step,
        )

        rf_arp_time += ramp_rf_off_time
        t += ramp_rf_off_time

        RF_switch_0.go_low(t)

        # Then the bias field (manifold)
        z_bias.customramp(
            t,
            ramp_arp_bias_time,
            LineRamp,
            rf_arp_final_z_bias,
            z_top_imaging_z_bias,
            samplerate=1 / rf_arp_step,
            units='A',
        )   
        #x_bias.constant(t, z_top_imaging_x_bias, units='A')
        #y_bias.constant(t, z_top_imaging_y_bias, units='A')

        rf_arp_time += ramp_arp_bias_time
        t += ramp_arp_bias_time


    elif mode == 'resonance':
        pass
        # RF_switch_0.go_low(t)
        # RF_mixer1.constant(t, 0.0)

    
    return rf_arp_time

@stage
def uwave_resonance(t, task='ARP', **kwargs):
    """ Adiabatic rapid passage from F = 1 to F = 2 to 
    measure pulse resonance. """

    uwave_arp_time = 0

    # Settle initial bias field (prep manifold)
    z_bias.customramp(
        t,
        ramp_arp_bias_time,
        LineRamp,
        z_top_imaging_z_bias,
        uwave_resonant_z_final_bias,
        samplerate=1 / uwave_arp_step,
        units='A',
    )

    uwave_arp_time += ramp_arp_bias_time
    t += ramp_arp_bias_time

    # Settle uwave fields (open gap)
    uwave1.setfreq(t-bias_settle_time, uwave_pulse_frequency, units='MHz')
    uwave1.setamp(t-bias_settle_time, uwave_arp_amplitude)

    if task =='ARP':
        uWave_switch_0.go_high(t)

        microwave_attenuator.customramp(
            t,
            ramp_uwave_on_time,
            LineRamp,
            6.0,
            uwave_attenuation,
            samplerate=1 / uwave_arp_step,
        )

        uwave_arp_time += ramp_uwave_on_time
        t += ramp_uwave_on_time

        uwave_mixer1.customramp(
            t,
            ramp_uwave_on_time,
            LineRamp,
            0.0,
            uwave_mixer_amplitude,
            samplerate=1 / uwave_arp_step,
        )
       
    uwave_arp_time += ramp_uwave_on_time
    t += ramp_uwave_on_time

    # Sweep bias field through resonance (ARP)

    z_bias.customramp(
        t,
        ramp_arp_resonance_time,
        LineRamp,
        uwave_resonant_z_final_bias,
        uwave_resonant_z_initial_bias,
        samplerate=1 / uwave_arp_step,
        units='A',
    )
  
    uwave_arp_time += ramp_arp_resonance_time
    t += ramp_arp_resonance_time 

    # Turn off after bias has settled:
    uwave_arp_time += ramp_arp_bias_time
    t += ramp_arp_bias_time

    microwave_attenuator.constant(t, 6.0)
    uwave_mixer1.constant(t, 0.0)
    uWave_switch_0.go_low(t)


    return uwave_arp_time


@stage
def load_final_trap(t, **kwargs):
    dipole_intensity.customramp(
        t,
        load_final_trap_time,
        LineRamp,
        final_dipole_intensity,
        elongated_dipole_intensity,
        samplerate=1 / dipole_evaporate_step,
    )
    dipole_split.customramp(
        t,
        load_final_trap_time,
        LineRamp,
        final_dipole_split,
        elongated_dipole_split,
        samplerate=1 / dipole_evaporate_step,
    )

    return load_final_trap_time

@stage
def apply_z_gradient(t):
    ramp_gradient_time = 0

    curent_supply_4_select_line0.go_high(t)
    curent_supply_4_select_line1.go_high(t)
    curent_supply_4_enable.go_high(t)

    transport_current_4.customramp(
        t,
        gradient_settle_time,
        LineRamp,
        0.0,
        slicing_gradient_current,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )

    # Correct for quadrupole induced shift in z-bias
    z_bias.customramp(
        t,
        gradient_settle_time,
        LineRamp,
        uwave_resonant_z_initial_bias,
        uwave_slicing_compensation_z_bias,
        samplerate = 1/magnetic_transport_step,
        units='A',
    )

    y_bias.customramp(
        t,
        gradient_settle_time,
        LineRamp,
        y_decompress_final_bias,
        uwave_slicing_compensation_y_bias,
        samplerate = 1/magnetic_transport_step,
        units='A',
    )
       
    x_bias.customramp(
        t,
        gradient_settle_time,
        LineRamp,
        x_transport_shim_bias,
        uwave_slicing_compensation_x_bias,
        samplerate = 1/magnetic_transport_step,
        units='A',
    )

    offset.customramp(
        t,
        gradient_settle_time,
        LineRamp,
        idle_z_offset,
        uwave_slicing_compensation_z_offset,
        samplerate = 1/magnetic_transport_step,
    )

    t += gradient_settle_time
    ramp_gradient_time += gradient_settle_time

    # Wait equally long for gradient to settle
    t += gradient_settle_time
    ramp_gradient_time += gradient_settle_time

    return ramp_gradient_time

@stage
def remove_z_gradient(t):
    ramp_gradient_time = 0

    transport_current_4.customramp(
        t,
        gradient_settle_time,
        LineRamp,
        slicing_gradient_current,
        0.0,
        samplerate=1 / magnetic_transport_step,
        units='A',
    )
        
    t += gradient_settle_time
    ramp_gradient_time += gradient_settle_time
    
    # Wait equally long for gradient to settle
    curent_supply_4_select_line0.go_low(t)
    curent_supply_4_select_line1.go_low(t)
    curent_supply_4_enable.go_low(t)
    
    t += gradient_settle_time
    ramp_gradient_time += gradient_settle_time

    return ramp_gradient_time

@stage
def uwave_transfer_pulse(t, **kwargs):
    uwave_coupling_duration = 0

    microwave_attenuator.constant(t, uwave_attenuation)
    uWave_switch_0.go_high(t)
    
    t += 5*us
    uwave_coupling_duration += 5*us

    uwave_mixer1.customramp(
        t,
        uwave_pulse_time,
        Blackman,
        0.0,
        uwave_mixer_amplitude,
        samplerate=1 / uwave_arp_step,
    )

    t += uwave_pulse_time
    uwave_coupling_duration += uwave_pulse_time

    uWave_switch_0.go_low(t)
    microwave_attenuator.constant(t, 6.0)

    return uwave_coupling_duration

@stage
def insitu_slice_imaging(t):
    initial_t = t

    # Pulse the probe, no repump, only atoms in F=2 get imaged
    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'thin', 'atoms_hologram')
    # Probe
    t += pulse_beam(
        t,
        probe_1,
        AOM_probe_1,
        [shutter_x, shutter_z],
        z_top_imaging_insitu_probe_intensity,
        0,
        z_top_imaging_insitu_probe_pulse_time,
    )

    t += andor_download_time

    # Blow away pulse
    t += pulse_beam(
        t,
        probe_1,
        AOM_probe_1,
        [shutter_x],
        0.00,
        5*us,
        z_top_imaging_insitu_probe_pulse_time,
    )

    t += z_top_imaging_insitu_probe_pulse_time

    return t - initial_t

@stage 
def complete_insitu_slice_imaging(t):
    initial_t = t

    # Pulse the probe, no repump
    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'thin', 'probe_hologram')
    t += pulse_beam(
        t,
        probe_1,
        AOM_probe_1,
        [shutter_x, shutter_z],
        z_top_imaging_insitu_probe_intensity,
        0,
        z_top_imaging_insitu_probe_pulse_time,
    )

    t += andor_download_time

    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'thin', 'probe')
    t += pulse_beam(
        t,
        probe_1,
        AOM_probe_1,
        [shutter_x],
        z_top_imaging_insitu_probe_intensity,
        0,
        z_top_imaging_insitu_probe_pulse_time,
    )

    t += andor_download_time

    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'thin', 'reference')
    t += pulse_beam(
        t,
        probe_1,
        AOM_probe_1,
        [shutter_z],
        z_top_imaging_insitu_probe_intensity,
        25*us,
        z_top_imaging_insitu_probe_pulse_time,
    )

    t += andor_download_time

    # Dark frame
    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'thin', 'dark')
    t += andor_download_time

    return t - initial_t

@stage
def dipole_trap_off(t, **kwargs):
    dipole_intensity.constant(t, 0.0)
    dipole_switch.go_low(t)

    # x_bias.constant(t, z_top_imaging_x_bias, units='A')
    # y_bias.constant(t, z_top_imaging_y_bias, units='A')
    # z_bias.constant(t, z_top_imaging_z_bias, units='A')

    MOT_lock.frequency.constant(
        t - beatnote_lock_settle_time, z_top_imaging_frequency, units='MHz'
    )

    AOM_MOT_repump.go_low(t-40*ms)
    MOT_repump.constant(t-40*ms, 0.0)
    AOM_probe_1.go_low(t-40*ms)
    probe_1.constant(t-40*ms, 0.0)

    return 0.0

@stage
def stern_gerlach_pulse(t):

    x_bias.constant(t, top_zero_x_bias, units='A')
    y_bias.constant(t, top_zero_y_bias, units='A')
    z_bias.constant(t, top_zero_z_bias, units='A')

    transport_current_4.constant(t, stern_gerlach_current, units='A')
    curent_supply_4_select_line0.go_high(t)
    curent_supply_4_select_line1.go_high(t)
    curent_supply_4_enable.go_high(t)      

    t += stern_gerlach_time

    transport_current_4.constant(t, -1.0, units='A')
    curent_supply_4_select_line0.go_low(t)
    curent_supply_4_select_line1.go_low(t)
    curent_supply_4_enable.go_low(t)

    z_bias.constant(t, z_top_imaging_z_bias, units='A')
    
    return stern_gerlach_time

@stage
def x_insitu_absorption_imaging(t, **kwargs):
    initial_t = t
    #t += 1 * ms # Make sure the AOMs are off before opening the shutters
    for frametype in ['atoms', 'probe']:
        YZ_1_Flea3.expose(t-flea3_exposure_delay_time, 'absorption', frametype)
        # Depump
        _ = pulse_beam(
            t, 
            probe_1, 
            AOM_probe_1, 
            [shutter_x], 
            0.8, 
            5*us,
            x_top_imaging_probe_pulse_time,
        )
        # Probe
        t += pulse_beam(
            t,
            MOT_repump,
            AOM_MOT_repump,
            [shutter_top_repump],
            x_top_imaging_probe_intensity,
            5*us,
            x_top_imaging_probe_pulse_time,
        )
        t += flea3_download_time
    YZ_1_Flea3.expose(t-flea3_exposure_delay_time, 'absorption', 'dark')
    t += flea3_download_time
    return t - initial_t

@stage
def z_time_of_flight_absorption_imaging(t, **kwargs):
    initial_t = t
    t += 1 * ms # Make sure the AOMs are off before opening the shutters
    shot_id = {'atoms':'shot1','probe':'shot2'}
    for frametype in ['atoms', 'probe']:
        XY_1_Flea3.expose(t-flea3_exposure_delay_time, shot_id[frametype], frametype)
        # Probe
        _ = pulse_beam(
            t, 
            probe_2, 
            AOM_probe_2, 
            [shutter_x_insitu], 
            z_top_imaging_TOF_probe_intensity, 
            5*us,
            z_top_imaging_TOF_probe_pulse_time,
        )
        # Repump
        t += pulse_beam(
            t - 5*us,
            MOT_repump,
            AOM_MOT_repump,
            [shutter_top_repump],
            0.8,
            5*us,
            z_top_imaging_TOF_probe_pulse_time,
        )
        t += flea3_download_time
    XY_1_Flea3.expose(t-flea3_exposure_delay_time, 'shot3', 'dark')
    t += flea3_download_time
    return t - initial_t

@stage
def z_insitu_absorption_imaging(t, **kwargs):
    initial_t = t

    for frametype in ['atoms', 'probe']:
        Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'absorption', frametype)
        # Probe
        _ = pulse_beam(
            t,
            probe_1,
            AOM_probe_1,
            [shutter_x],
            z_top_imaging_insitu_probe_intensity,
            5 * us,
            z_top_imaging_insitu_probe_pulse_time,
        )
        # Repump
        t += pulse_beam(
            t - 5*us,
            MOT_repump,
            AOM_MOT_repump,
            [shutter_top_repump],
            0.8,
            5 * us,
            z_top_imaging_insitu_probe_pulse_time,
        )

        t += andor_download_time

    # Dark frame
    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'absorption', 'dark')
    t += andor_download_time

    return t - initial_t



@stage
def z_insitu_holographic_imaging(t, **kwargs):
    initial_t = t

    for frametype in ['atoms_hologram', 'probe_hologram']:
        Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'holographic', frametype)     
    
        # Holograms
        _ = pulse_beam(
            t,
            probe_1,
            AOM_probe_1,
            [shutter_x, shutter_z],
            z_top_imaging_insitu_probe_intensity,
            0.0,
            z_top_imaging_insitu_probe_pulse_time,
        )
        # Repump
        t += pulse_beam(
            t,
            MOT_repump,
            AOM_MOT_repump,
            [shutter_top_repump],
            0.8,
            5 * us,
            z_top_imaging_insitu_probe_pulse_time,
        )

        t += andor_download_time

    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'holographic', 'probe')
    # Probe
    _ = pulse_beam(
        t,
        probe_1,
        AOM_probe_1,
        [shutter_x],
        z_top_imaging_insitu_probe_intensity,
        0.0,
        z_top_imaging_insitu_probe_pulse_time,
    )
    # Repump
    t += pulse_beam(
        t,
        MOT_repump,
        AOM_MOT_repump,
        [shutter_top_repump],
        0.8,
        5 * us,
        z_top_imaging_insitu_probe_pulse_time,
    )

    t += andor_download_time

    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'holographic', 'reference')
    # Reference
    _ = pulse_beam(
        t,
        probe_1,
        AOM_probe_1,
        [shutter_z, reference_beam_shutter],
        z_top_imaging_insitu_probe_intensity,
        0.0,
        z_top_imaging_insitu_probe_pulse_time,
    )
    # Repump
    t += pulse_beam(
        t,
        MOT_repump,
        AOM_MOT_repump,
        [shutter_top_repump],
        0.8,
        5 * us,
        z_top_imaging_insitu_probe_pulse_time,
    )

    t += andor_download_time

    # Dark frame
    Andor_iXon_ultra.expose(t - andor_exposure_delay_time, 'holographic', 'dark')
    t += andor_download_time

    return t - initial_t

@stage
def z_insitu_fluorescence_imaging(t, **kwargs):
    initial_t = t

    for frametype in ['atoms', 'dark']:
        Andor_iXon_ultra.expose(
            t - andor_exposure_delay_time, 'fluorescence', frametype
        )
        # Probe
        # _ = pulse_beam(
        #     t,
        #     probe_1,
        #     AOM_probe_1,
        #     [shutter_x, shutter_z],
        #     z_top_imaging_insitu_probe_intensity,
        #     5 * us,
        #     z_top_imaging_insitu_probe_pulse_time,
        # )
        # Repump
        t += pulse_beam(
            t - 5*us,
            MOT_repump,
            AOM_MOT_repump,
            [shutter_top_repump],
            0.8,
            5 * us,
            z_top_imaging_insitu_probe_pulse_time,
        )
        t += andor_download_time

    return t - initial_t


@stage
def off(t, **kwargs):  
    """ Turn the state of all devices to idle values, except quadrupole coils which are
    turned off"""

    # Define MOT state
    # Cooling and repump
    MOT_repump.constant(t, idle_repump_intensity)
    MOT_cooling.constant(t, idle_cooling_intensity)
    MOT_lock.setfreq(t, idle_beatnote_freq, units='MHz')
    # Gradients
    curent_supply_1_enable.go_low(t)
    curent_supply_2_enable.go_low(t)
    curent_supply_3_enable.go_low(t)
    curent_supply_4_enable.go_low(t)
    transport_current_1.constant(t, 0.0, units='A')
    transport_current_2.constant(t, 0.0, units='A')
    transport_current_3.constant(t, 0.0, units='A')
    transport_current_4.constant(t, 0.0, units='A')
    # Bias fields
    kepco_enable_0.go_high(t)
    kepco_enable_1.go_high(t)
    x_bias.constant(t, idle_x_bias, units='A')
    y_bias.constant(t, idle_y_bias, units='A')
    z_bias.constant(t, idle_z_bias, units='A')
    
    # Safety related turn off-s
    probe_1.constant(t, idle_probe_1_intensity)    
    AOM_probe_1.go_low(t)
    shutter_z.go_low(t)
    RF_evap.setfreq(t,  10.0, units='MHz')
    RF_evap.setamp(t, 0.0)
    dipole_switch.go_low(t)
    dipole_intensity.constant(t, idle_dipole_intensity)
    dipole_split.constant(t, idle_dipole_split)
    
    # Acquisition related turn off-s
    fluxgate_trig.go_low(t)   
    scope_trigger_0.go_low(t)

    #Ramans

    AOM_Raman_1.setfreq(t, 80, units='MHz')
    AOM_Raman_1.setamp(t, 0.5)

    mixer_raman_1.constant(t,0.0)
    mixer_raman_2.constant(t,0.0)
    raman_1.go_low(t)
    raman_2.go_low(t) 

    shutter_raman1.go_low(t)
    shutter_raman2.go_low(t)
    
    if not UV_soak:
        UV_LED.go_low(t)

    return off_time

@stage
def extra_UV(t, **kwargs):
    """Shine UV to make up to total_UV_per_shot worth of UV in this shot"""

    UV_MOT_time = UV_MOT_fraction * MOT_time
    if make_small_MOT:
        UV_MOT_time /= 100
  
    extra_UV_time = total_UV_per_shot - UV_MOT_time
    assert extra_UV_time > 0
    UV_LED.go_high(t)
    UV_LED.go_low(t + extra_UV_time)
    return extra_UV_time



@stage
def snap_image(t, imaging_plane='z_insitu', type='atoms'):
    # Based on imaging plane, use a specific AOM/CCD/probe set.
    if imaging_plane == 'z_TOF':
        
        ###############  x in-situ beam as the TOF beam specifications - 2019/05/10
        AOM = AOM_probe_2
        probe, probeint, probe_freq = probe_2, z_top_imaging_TOF_probe_intensity, z_top_imaging_frequency #ImageFreqHighField #
        shutter = shutter_x_insitu
        CCD = XY_1_Flea3 
        
         
        
    elif imaging_plane == 'z_insitu':
        AOM = AOM_probe_1
        CCD = XY_2_Flea3
        probe, probeint, probe_freq = probe_1, z_top_imaging_insitu_probe_intensity, z_top_imaging_frequency # ImageFreqHighField #
        shutter = shutter_x
   


    total_time = 0.0    
    # Repump
    # if Repump :
    #     pulse_beam(t-5*us, MOT_repump, AOM_MOT_repump, shutter_top_repump, 0.8, z_top_imaging_insitu_probe_pulse_time)
    # if xRepump: 
    #     pulse_beam(t-5*us, probe_2, AOM_probe_2, shutter_x_insitu, 0.8, z_top_imaging_insitu_probe_pulse_time)   
    # Main acquisition
    if type == 'atoms':
        # Note: Same AOM is used for the probe beam and the MOT cooling beam        
        MOT_lock.frequency.constant(t-100.*ms, probe_freq, units='MHz')
        #set image freq in HoldAfterMove necause laser locking takes time        
        shot_id = 'shot1'
        total_time += pulse_beam_old(t, probe, AOM, shutter, probeint, z_top_imaging_insitu_probe_pulse_time)
    elif type == 'probe':
        shot_id = 'shot2'
        total_time += pulse_beam_old(t, probe, AOM, shutter, probeint, z_top_imaging_insitu_probe_pulse_time)  
    elif type == 'dark':
        shot_id = 'shot3'
        #total_time += pulse_beam(t, probe, AOM, shutter, 0.0, TimeImage)
        total_time += z_top_imaging_insitu_probe_pulse_time
    elif type == 'red':
        shot_id = 'shot4'
        total_time += pulse_beam_old(t, probe, AOM, shutter, probeint, z_top_imaging_insitu_probe_pulse_time)    
    elif type == 'blue':
        shot_id = 'shot5'
        total_time += pulse_beam_old(t, probe, AOM, shutter, probeint, z_top_imaging_insitu_probe_pulse_time)
    
    #fluxgate_trig.go_high(t)
    #fluxgate_trig.go_low(t+1.*ms)
    if imaging_plane=='z_insitu':
        exp_delay = 70*us
    else:
        exp_delay = 30*us
    CCD.expose(t-exp_delay, shot_id, type) # 2020_02_19: was 30 us.  Suggest variable.

    total_time += flea3_download_time
    
    return total_time

def pulse_beam_old(t, beam, rf_switch, shutter, command, pulse_duration):
    TimeInSituOpenShutter = 3.8*ms
    beam.constant(t-TimeInSituOpenShutter-1*ms, 0)
    rf_switch.go_low(t-TimeInSituOpenShutter-1*ms)
    shutter.go_high(t-TimeInSituOpenShutter)
    rf_switch.go_high(t)
    beam.constant(t, command)
    beam.constant(t+pulse_duration, 0)
    shutter.go_low(t+pulse_duration)
    rf_switch.go_low(t+pulse_duration)


    return pulse_duration

def fields_to_z(t,z_field):
    y_bias.customramp(
        t,
        250*ms,
        LineRamp,
        y_decompress_final_bias,
        top_zero_y_bias,
        samplerate=1 / (2*10*us),
        units='A',
    )
    x_bias.customramp(
        t,
        250*ms,
        LineRamp,
        x_transport_shim_bias,
        top_zero_x_bias,
        samplerate=1 / (2*10*us),
        units='A',
    )

    z_bias.customramp(
        t,
        250*ms,
        LineRamp,
        z_transport_shim_bias,
        z_field,
        samplerate=1 / (2*10*us),
        units='A',
    )
    
    return 250*ms

def pulse_ramans(t,raman_pulse_dur):

    pulse_duration = raman_pulse_dur
    TimeInSituOpenShutter = 3.8*ms

    if pulse_raman_1_opt:
    
        mixer_raman_1.constant(t-TimeInSituOpenShutter-1*ms, 0)
        raman_1.go_low(t-TimeInSituOpenShutter-1*ms)
        shutter_raman1.go_high(t-TimeInSituOpenShutter)
        raman_1.go_high(t)
        mixer_raman_1.constant(t, pulse_const_1)
        mixer_raman_1.constant(t+pulse_duration, 0)
        shutter_raman1.go_low(t+pulse_duration)
        raman_1.go_low(t+pulse_duration)


    if pulse_raman_2_opt:

        mixer_raman_2.constant(t-TimeInSituOpenShutter-1*ms, 0)
        raman_2.go_low(t-TimeInSituOpenShutter-1*ms)
        shutter_raman2.go_high(t-TimeInSituOpenShutter)
        raman_2.go_high(t)
        mixer_raman_2.constant(t, pulse_const_2)
        mixer_raman_2.constant(t+pulse_duration, 0)
        shutter_raman2.go_low(t+pulse_duration)
        raman_2.go_low(t+pulse_duration)


    return pulse_duration




start()

t = 0
t += prep(t)
t += MOT(t, color='cornflowerblue')
if wait_before_compressed_MOT:
    wait(label='compressed_MOT_wait', t=t, timeout=2)
t += compressed_MOT(t)
t += optical_molasses(t)
t += prep_optical_pumping(t)
t += optical_pump_2_2(t)
t += magnetic_transport(t, color='lightsteelblue')
t += rf_evaporate(t, color='goldenrod')


if dipole_evaporation:
    t += decompress(t)
    t += fields_to_z(t,raman_pulsing_z_bias)
    if uwave_arp_transfer:
        wait(label='uwave_arp_wait', t=t, timeout=1)
        t += uwave_arp(t, mode='state_preparation')



    

    t += dipole_evaporate(t, color='limegreen')

    

    #t += load_final_trap(t, color='orange')
    MOT_lock.frequency.constant(
        t - beatnote_lock_settle_time, z_top_imaging_frequency, units='MHz'
    )

    # z_bias.constant(t, raman_pulsing_z_bias, units='A')
    # x_bias.constant(t, top_zero_x_bias, units='A')
    # y_bias.constant(t, top_zero_y_bias, units='A')
    

    if pulse_ramans_opt:
        t += pulse_ramans(t,raman_pulse_dur)


    if release_in_TOF:
        t += dipole_trap_off(t)
        t += top_imaging_TOF
        x_bias.constant(t, top_zero_x_bias, units='A')
        y_bias.constant(t, top_zero_y_bias, units='A')
        z_bias.constant(t, z_top_imaging_z_bias, units='A')
        t += stern_gerlach_time
        #t += stern_gerlach_pulse(t)
        t += z_time_of_flight_absorption_imaging(t)
        # img = 'z_TOF'
    
        # t += snap_image(t, imaging_plane=img, type='atoms')
        # t += snap_image(t, imaging_plane=img, type='probe')
        # t += snap_image(t, imaging_plane=img, type='dark')

    elif not release_in_TOF and not microwave_insitu_slicing:
        t += dipole_trap_off(t)
        t += top_short_TOF
        #t += z_insitu_fluorescence_imaging(t)
        #t += z_insitu_absorption_imaging(t)
        #t += z_insitu_holographic_imaging(t)
        img = 'z_TOF'
    
        t += snap_image(t, imaging_plane=img, type='atoms')
        t += snap_image(t, imaging_plane=img, type='probe')
        t += snap_image(t, imaging_plane=img, type='dark')


else:
    if release_in_TOF:
        t += magnetic_trap_off(t, imaging='x')
        t += top_short_TOF
        #t += x_insitu_absorption_imaging(t)
        t += z_time_of_flight_absorption_imaging(t)
    else:
        img = 'z_insitu'
    
        t += snap_image(t, imaging_plane=img, type='atoms')
        t += snap_image(t, imaging_plane=img, type='probe')
        t += snap_image(t, imaging_plane=img, type='dark')
        

t += off(t)

if shine_extra_UV and not UV_soak:
    t += extra_UV(t)

stop(t+0.01, target_cycle_time=40.0, cycle_time_delay_after_programming=True)

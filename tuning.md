# Voron 2.4 tuning

A list of printer tuning to perform on a Voron 2.4. This guide does not try very hard to be very generic. These are the opinionated findings about what worked well/less well for us on our Vorons with our mods and upgrades.

There are lots of tuning guides online. The point of this one is to:
* Have a single list of all good tuning steps one can perform from various sources online.
* Some tuning can be done in a myriad of different ways. This document points out which method worked well for us and direct links to that variant.

The different tunings and tests are approximately in the order they should be performed.

## Belt tension

Before we can tune anything else, the belts must have a good and equal tension. This has to be done before most other tuning. And when changing belt tension, a lot of other tuning has to be re-done as the belt tension affects important mechanical properties of the printer.

The [official best tension tuning guide] is a good place to start. But it's extremely hard to read out the frequency of the belts.
Instead we recommend using some other tool to measure belt tension.

* A tool that measures the absolute belt tension using a spring: [GT2 Belt Tension Meter]. There are also numerous remixes with bearings, for smoother operation: [GT2 Belt Tension Meter w/Bearings].
* A tool that only measures relative belt tension. This can only help you to get the different belts to have the same tension. After all, that's the most important, as long as the absolute tension is not very off: [Belt Tension Meter]

[GT2 Belt Tension Meter w/Bearings]: https://www.printables.com/model/634190-gt2-belt-tension-meter-wbearings
[GT2 Belt Tension Meter]: https://github.com/Diyshift/3D-Printer/tree/main/GT2%20Belt%20Tension%20Meter
[Belt Tension Meter]: https://mods.vorondesign.com/details/fmmg4Yx2BLULkfDDpZnAng
[official best tension tuning guide]: https://docs.vorondesign.com/tuning/secondary_printer_tuning.html#belt-tension

## Input shaping (Resonance Compensation)

Input Shaper is a Klipper-specific software technique for reducing ringing (also known as echoing, ghosting or rippling) in prints. The [Klipper docs on Resonance compensation] is a good place to start. But the primary process described is extremely manual. Klipper has support for automatic tuning via accelerometers, and the CAN toolhead board has one of those built in. So this can be way simplified. The documentation for that is here: https://www.klipper3d.org/Measuring_Resonances.html#input-shaper-auto-calibration

The TLDR is:
1. Make sure the printer is placed in the place/way it will be used. The resonance changes with the physical placement and surroundings.
2. Run `SHAPER_CALIBRATE`
3. Observe the output. It will recommend input shaper algorithm for the X and Y axis along with the recommended `max_accel` for both.
3. Run `SAVE_CONFIG`.
4. Pick the lowest recommended `max_accel` from the two algorithms used and use that as your max acceleration for print moves (at least the visible ones) in your slicer acceleration configuration. Non-print moves can still go faster, so don't put this value in `max_accel` in your printer config.

[Klipper docs on Resonance compensation]: https://github.com/Klipper3d/klipper/blob/master/docs/Resonance_Compensation.md

## Determining Maximum Speeds and Accelerations

This is about finding out maximum values for the `max_velocity` and `max_accel` parameters in your printer config. These values determine how fast your printer can move without mechanically breaking down/skipping steps on the motors. You can most likely not actually print at these speeds.

You want to re-tune this after performing input shaping calibration.

Guide: https://ellis3dp.com/Print-Tuning-Guide/articles/determining_max_speeds_accels.html

TLDR:
1. Make sure the `run_current` is high enough. Our motors are rated at 2A and our 2209 drivers at 1.4A. So we put `run_current` at 0.9 to be on the safe side.
2. Add [this](https://github.com/AndrewEllis93/Print-Tuning-Guide/blob/main/macros/TEST_SPEED.cfg) macro to your printer.cfg file.
3. Run the torture test. Start out with not too whack values and increase them until the printer starts skipping. This can be noticed by the printer sounding like it wants to die/smacking the print head into the walls, or by the `stepper_x` and `stepper_y` values differing more than `microsteps` from the two homing runs the torture test performs.
    `TEST_SPEED SPEED=400 ACCEL=15000 ITERATIONS=2`
4. When you have found values for `SPEED` and `ACCEL` that don't skip with `ITERATIONS=2`, run the torture test again with `ITERATIONS=10`. If it starts skipping, lower the values.
5. When you have found values that smoothly pass `ITERATIONS=10` you are almost there. Run it once again with `ITERATIONS=50`.
6. Deduct ~15% from the found values and configure your printer's `max_velocity` and `max_accel` according to the found values.

Our printers topped out at around `SPEED=450 ACCEL=20000` somewhere. They could probably go a bit higher, but we did not want to put too high strain on them.

## Extruder calibration

Extruder calibration simply ensures that 100mm requested = 100mm extruded. Can be performed once and then hopefully never touched again. The documentation is here: https://ellis3dp.com/Print-Tuning-Guide/articles/extruder_calibration.html

Do this cold and with a disconnected hotend, to only measure the extruder itself.

## Maximum Volumetric Flow Rate

The act of figuring out how fast your hotend and nozzle combination can melt plastic. Has to be measured once per hotend and nozzle combo as well as temperature. If you lower the nozzle print temperature, your max flow rate will also go down.

The calibration built into Orca slicer is really simple and fast, use it!. The method described by Elli in https://ellis3dp.com/Print-Tuning-Guide/articles/determining_max_volumetric_flow_rate.html#method is really weird. In theory it's very simple. But every time I have tried it, I start losing out on extruded amount at *very* low flow rates. 

## First layer squish

Should in theory only have to be done once with TAP. Or after every time you reassemble the TAP part of the toolhead at least. But in practice it seems to be needed more often. Do after nozzle changes etc.

https://ellis3dp.com/Print-Tuning-Guide/articles/first_layer_squish.html

Both SuperSlicer and Orca slicer have this tuning built in. But they are a bit different. The one in Orca is more similar to Elli's guide.

At some point I was dead sure that optimal `z_offset` varied with printer temperature. But there *should* not be anything affecting this. And over a day of calibration at different temperatures finally convinced me that the temperature *does not* affect this. So just tune this with whatever filament at whatever temperature.


## Per filament tuning

All these tunings has to be done per filament and nozzle. At *least* for every type of plastic, but it's good if it's done per vendor as well.

### Nozzle temperature

Arguably the most important per filament slicer setting, and the one to perform first. Greatly affects properties such as stringing, layer adhesion, warping and quality of bridges.

Can be tested by printing a temperature tower. This is built into Orca slicer.

When multiple temperatures give indistinguishable results, choose the higher temperature as that will give better layer adhesion and higher max volumetric flow rate. Remember to re-test your max volumetric flow rate if you lower the printing temp.

### Extrusion Multiplier (Sometimes called "Flow ratio")

https://ellis3dp.com/Print-Tuning-Guide/articles/extrusion_multiplier.html

The calibration print is built into both SuperSlicer and Orca. However, the one built into SuperSlicer gave me (faern) very very high results. The results from the one built into Orca slicer were much more sane and basically identical to what Widar has and what I had in SuperSlicer.

### Pressure Advance (PA, or sometimes "Linear Advance")

This value differs when acceleration changes. So a value measured with Input Shaper is not valid for a non-Input Shaper print

https://ellis3dp.com/Print-Tuning-Guide/articles/pressure_linear_advance/pattern_method.html

The calibration print is built into both SuperSlicer and Orca.

## Retraction

You only need to fiddle with this if you have too much stringing or other retraction related issues. A good Pressure Advance calibration can alleviate some retraction issues. So calibrate PA first.

https://ellis3dp.com/Print-Tuning-Guide/articles/retraction.html

SuperSlicer has built in retraction calibration, so has [Orca](https://github.com/SoftFever/OrcaSlicer/wiki/retraction-calib).

I (faern) found that PLA has no noticeable stringing at all during this test, so I set my retraction to 0.4mm according to recommendations in Elli's guide. For PETG the stringing seemed to be the same for all retraction values, so I kept the retraction at the default 0.8 and have to try to combat stringing with PA and other settings.

### Filament shrinkage

Calibrates the width of the outer perimeter in order to compensate for filament shrinking when cooling.
This is a per filament setting in the slicer.

TODO: How to calibrate, and when in the process should this calibration be performed?


## Dimensional accuracy and XY Skew

The Califlower print can help you find if your printer has issues with dimensional accuracy or if it has any skew in the X/Y axis. This is performed by printing the "flower", taking a bunch of measurements.

This test should be performed late in the tuning, as it is basically a test to see if all the other tuning has resulted in a well working printer or not.

TODO: Insert link to where this calibration can be purchased

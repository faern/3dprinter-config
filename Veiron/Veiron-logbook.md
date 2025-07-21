# 2023-03-21 - Order Formbot kit

Ordered the Formbot Veiron 2.4 kit with Stealthburner


# 2023-11-27 - Input shaping

Today I performed automatic input shaping calibration with the accelerometer built into the
CAN bus toolhead PCB. The adxl345 chip was already configured thanks to the default configs
I pulled in when we installed the CANbus PCB. I just had to change the probe point to be
in the middle of the printbed and then follow:
https://www.klipper3d.org/Measuring_Resonances.html#measuring-the-resonances_1

Actually I went with the automatic version at: https://www.klipper3d.org/Measuring_Resonances.html#input-shaper-auto-calibration

I then manually changed the max_accel to 4000. The scripts recommended a maximum of 4200.
But the manual also says to not blindly trust what the scripts compute. And my example
config had a comment saying max = 4000, so I went with that.

Later in the day I continued Veiron upgrades with the following things:
* Installed KAMP (https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging) for smarter bed mesh leveling and purging
* Speed up both homing and QGL to save some time
* Add helpful M117 messages to various macros to better see what the printer is doing
* Activated the filament runout sensor and configured it with the help of the voron guides + ellis guide:
  https://docs.vorondesign.com/community/howto/samwiseg0/btt_smart_filament_sensor.html

# Upgrade to Phaetus Rapido Plus HF

Things to do after the upgrade:

* Compute Z min/max limits and Z calibration
* PID heating calibration
* 


# Todo

* Figure out filament drying/storage I can print directly from.
* Install exhaust fan. So chamber temperature can be controlled better.

# 2025-07-14 - Uppgrade software

Today I upgraded all software directly via Mainsail (crowsnest). Had to flash the klipper firmware to the boards to get
it working again. After som research I figured out what hardware I had :'D
* Mainboard - BTT Octopus 1.1
* CAN board - EBB SB2209 (RP2040)

Flashing to the mainboard was as simple as SSHing to `~/klipper/` and running `make menuconfig` and following
the instructions in the manual: https://docs.vorondesign.com/build/software/octopus_klipper.html, followed
by `make flash FLASH_DEVICE=0483:df11`

For the CAN head it took some time to figure out how to flash it. Can't remember how we did it last time.
Apparently the EBB board can be flashed both over CAN and via DFU method. Widar thinks we did the CAN method.
But to do the CAN flashing, one should use CanBoot (now renamed to Katapult), but I have no such software
checked out on the rpi, so I doubt I used that last time.

The manuals for the EBB differ significantly from when we bought the boards and now. So I have to figure out
which manual I better follow, and which method I better use

## What I tried that failed

1. Flashing directly over CAN with the existing firmware on the EBB board - Errors
2. Flashing newest Katapult version to the EBB board over USB, in preparation for then flashing over CAN - Resulting in the board blinking red and nothing working

## What I finally did that made it work

I flashed Klipper directly to the EBB board via USB (DFU mode). That worked fine! So my EBB board does not have any CanBoot/Katapult firmware now


# 2025-07-16 - Tuning with Widar

Planning on spending the day with Widar to tune and fix our printers. Mostly making sure they are still square and calibrated. And then increase the speed!

I realize two very obvious things regarding why my printer is so "slow":
1. I'm not using my input shaper profile :facepalm:. The profiles exist in my slicer, but they are not default, so I have forgotten to use it in a long time
2. I'm basing my profile on Ellis PIF-profiles, which focus a lot on strength. So I have 4 perimiters and 40% infill by default, which is a lot more than
   most people use. I could probably just go with fewer perimeters and less infill for most prints, and cut print time significantly.

Now I'm trying to migrate to Orca slicer, but decided to postpone that until a later date when I have more time and when I feel happy with my profiles in SuperSlicer. So I move from one good state.

We started doing speed tuning according to https://ellis3dp.com/Print-Tuning-Guide/articles/determining_max_speeds_accels.html.

First I just bumped my motor `run_current` from 0.8 to 0.9. Our motors seem to handle 2A and our drivers 1.4A. So we are still on the safe side here, and Widar bumped his `run_current` to 0.9, so I'm just following him and it seems safe. For the X/Y/Z steppers that is, not the extruder stepper.

We then started running the TEST_SPEED macro from the tuning guide. At first we thought something was wrong, because we could increase the acceleration a huge amount and never get any skips. We then raised the test velocity from 300 to 450 and more, and then we "finally" started getting skipping around 20-30k accel. We tested back and fourth. We settled on 450 probably being a good enough velocity, and then trying to find a fast but safe acceleration from that. The higher the velocity, the lower the max acceleration, and we thought a good acceleration was more important for most prints, so we did not want to go too bananas on the velocity.

I went crazy and tried `SPEED=450 ACCEL=35000`. This broke my printer :( The printed part where the belts attach to the print head snapped. So Veiron was now not operational. But Widar continued trying the speed test with more sane values. Since we wanted to settle on velocity 450, and we wanted to deduct 15% from the max velocity and acceleration we found during testing, we settled on testing at `SPEED=530` (450/0.85). We ended up with 20000 in accel being safe. As in always working, and never skipping. So we set `max_accel: 17000` (15% less than found value)

*Note from 2025-07-19*: I have now repaired Veiron and ran the same tests as Widar. However, I wanted to be able to sett acceleration to 20k for a nice rounder number. So I performed the torture test at `SPEED=530 ACCEL=23600`. It survived ITERATIONS=2, but started skipping at ITERATIONS=10 :( So I'll back down again. At `TEST_SPEED SPEED=530 ACCEL=20000 ITERATIONS=10` (same as worked fine for Widar) Veiron also skipped :( Si I went all the way down to `SPEED=500 ACCEL=20000` before it stopped skipping completely. So I'll configure it with:
```
max_velocity: 425
max_accel: 17000
```

# 2025-07-20 - More tuning

After setting the new speeds yesterday, I need to finish the tuning. Today I upgraded >200 debian packages on the rpi as a start, to gte all software to the latest version.

I then computed some heightmaps to see how flat my heatbed is. I did this heat soaked with the nozzle at 130C and the bed at 95C. I had the smooth side of the build plates up. Turns out it's more wobbly than I had hoped. The range is 0.177mm (almost a full layer!). Meanwhile Widar's Otto has a heightmap range of 0.144, so slightly better.

I tried running input shaper resonance calibration again to see if things changed after fixing the toolhead, re-tensioning the belts etc etc. Now I get worse results (with regards to recommended max accel). :(

I then performed the input shaper tuning again. Sadly the results are way different from last time. And the recommended `max_accel` is lower than last time. So I will likely try to find out why the resonance changed and if I can improve it.


# 2025-07-21 - Getting a hold of some tuning now!

Started writing the [tuning](../tuning.md) document.

## Belt tension

I compared belt tension between Veiron and Otto with the https://mods.vorondesign.com/details/fmmg4Yx2BLULkfDDpZnAng tool. Turns out Z was mostly good! Otto had the same tension on all four. And all but the back right Z belt on Veiron was the same as Otto. The last one was a bit too loose. Fixed! For A/B Otto was identical. Veiron was too loose on both, and not even equal between A and B. Fixed!

## Input shaper

New Input Shaper! I suspect the too loose and uneven A/B belt tension was the source of the worse resonance, and the lower recommended `max_accel`. And I was right! Re-running it now give me a recommended max accel of 4500:

Output from calibrate_shaper.py for X-axis:
```
Fitted shaper 'mzv' frequency = 39.0 Hz (vibrations = 1.3%, smoothing ~= 0.134)
To avoid too much smoothing with 'mzv', suggested max_accel <= 4500 mm/sec^2
```
Output from calibrate_shaper.py for Y-axis:
```
Fitted shaper '3hump_ei' frequency = 88.2 Hz (vibrations = 0.0%, smoothing ~= 0.105)
To avoid too much smoothing with '3hump_ei', suggested max_accel <= 5700 mm/sec^2
```

## Max velocity and acceleration

Both the tightening of the A/B belts and the new input shaper config warrants re-trying finding a new max velocity and acceleration. I re-tried the parameters that worked for Widar:
```
TEST_SPEED SPEED=530 ACCEL=20000 ITERATIONS=10
```
And it passed with flying colors! I realize that it's not worth pushing the acceleration more, because given the input shaper results, the vast majority of moves will be limited to acceleration <=4500 anyway. So I can stop at 20k accel, and see how far I can push the velocity instead. For many prints, speeds above 400 will never be reached anyway, becaues each move is rather short, and the acceleration becomes the bottleneck. But for filling larger areas or long straight lines, a high max velocity can really help.

After some testing of increased speeds I finally stopped at `SPEED=750 ACCEL=20000 ITERATIONS=50` without ever experiencing any skipping. I doubt going faster would ever be practical anyway, so there is no reason to push it futher. I deduct 20% to be on the safe side and configure my printer with:
```
max_velocity: 650
max_accel: 16000
```

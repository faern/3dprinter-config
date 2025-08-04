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

## Upgrade SuperSlicer and update slicer limits

A day or two ago I did the bulk work of migrating to the latest version of SuperSlicer (from `2.4.58.5` as recommended in the Ellis profiles, to `2.7.61.6` which is the newest.) A bunch of stuff had to be fixed manually in the upgrade. And then I also adopted a lot of new printer configs to make it fit Veiron better. Things I had been too lazy to do in the past.


# 2025-07-22 - More tuning!

## Heightmap / bed level

I started by doing heightmap/bed leveling testing again. To see if my results have improved with all the above improved tuning. I found it slightly worrying that my heightmap over the entire print surface had a diff range of almost a full print layer (~0.19mm).

In all heated states I set the nozzle temp to the same as the bed temp, so that them touching would not mean one part changing the temperature of the other, trying to avoid state changes throughout the measurement. I also waited for the chamber temperature to stabilize with the new bed temp in most cases.

* First measure from cold: **0.131mm range**
* Second measure. Bed and nozzle set to 60 C (PLA) and well cleaned nozzle: **0.092mm range**
* Third measure. Bed and nozzle at 100 C (roughly PETG/ASA/ABS). Waited for chamber to stabilize at 58 C: **0.277mm range diff**.
* Fourth measure. Bed and nozzle still at 100 C but a bit later after fiddling with other stuff: **0.219mm range**.
* Fifth measure. Turning the bed/nozzle back down to 60 C. Running the heightmap check just as the heatbed reached 60C, not waiting for chamber to stabilize: **0.220mm range**

Seems like my hotend is simply more wobbly when the bed/printer is hotter. It is mostly the front and back of the build plate that is high. The center (along Y) seems fine.

## X/Y Homing speed

I have always had the homing speed (`homing_speed`) left at the default; 25mm/s. This is painfully slow. A comment in the config that was there from the start said that 100 is the max. I bumped it up in increments of ~20 and stopped at 80mm/s. Still can't see/hear anything wrong so I'm going to settle for this. Greatly speeds up homing.

## max_z_velocity and Z homing speed

I have never touched the default speeds for Z. My config was:
```
[printer]
max_z_velocity: 15
max_z_accel: 350

[stepper_z]
homing_speed: 8
second_homing_speed: 3
```

I'm trying to find sources online as to what an upper limit/safe values for these would be. I don't find very much. I mostly find people change this to stop the printer from ringing. CNC kitchen has a post with `max_z_velocity: 40`, but the rest of the values the same as me - https://www.cnckitchen.com/blog/building-a-voron-24-r2-in-2022-ldo-kit.

I raised `max_z_velocity` to the double, `30`. It sounded fine when moving around at that speed. Seems like a safe level and still 100% faster than before.

Regarding the Z homing speed. I want the max value where the printer will detect that the TAP sensor is triggered and stops the movement, before the TAP rail reaches its end and cause mechanical strain. I measured that the TAP sensor triggers 2mm before the the very top of the print head Z movement. So I should use whatever Z homing speed that allows the software to detect the sensor and stop before 2 more mm has passed. At the current default of 8 mm/s, the machine has 0.25 seconds to stop. That's very long for electronics to react. I started out at around double that and experimented with what created the least noise/resonance in the motors. I ended up with 13 for Z homing speed.

## z_offset

Continuing down [my own guide](../tuning.md) the next step was tuning the first layer squish. I did so via the calibration built into SuperSlicer. It worked well. I ended up raising Z 0.03 mm.

## Filament tuning

Finally! Starting off with PLA as it's generally easy to print, does not require the printer to be heatsoaked etc. Using my 2kg Recycled dark grey Prusament PLA that I've only had for a few months. So fairly fresh roll.

I first did PA tuning for Prusament PLA. Ended up increasing it from 0.055 to 0.06 (very minor bump upwards). I then realized that SuperSlicer recommends doing EM calibration first.

EM calibration for Prusament PLA... I started off with my previous value: 0.96. I did the -20% to +20% calibration in SuperSlicer. +20% was the only good looking one, meaning EM = 1.15 :/ This is weird. That's too high. I re-tried with Ellis approach and test prints. Then I could suddenly not see any difference between 0.92 and 1.0. Very weird. Either the calibration built into SS is broken, or I'm doing something very wrong with that one.

## Going back to extruder calibration

Given the weird EM results above, I decided to take a step back in the calibration. Started off with extruder calibration. Check. Still extrudes exactl 100mm when asking it for 100mm.

## Maximum volumetric flow rate of my hotend and nozzle

Maybe my EM values are off because I'm trying to extrude faster than my hotend can handle? First I tried Ellis method of measuring this. But it's really weird. Already at ~10mm^3/s I start losing performance at around ~95mm extruded only. A 5% degradation at this low speed?! That's insane.

I asked Widar, and he only uses the max flow rate calibration built into Orca. So I now set up Orca. Just run with mostly default settings for a Voron 2.4. I adjusted the filament temperatures and some other settings to align with what Prusa recommends and what I have in Superslicer. Then I started printing the tests.

See results for each filament type below where I start doing more serious calibration per filament.


# 2025-07-23 - First layer squish calibration galore.

When playing with ASA yesterday I saw that the first layer squish was way off! I raised it by 0.03 yesterday, and I have disabled my `SET_TEMP_BASED_Z_OFFSET` a long time ago. Doing first layer squish with ASA at a fully heatsoaked printer today made me lower `z_offset` by 0.06 again. My guess is that I really need to re-enable `SET_TEMP_BASED_Z_OFFSET` and calibrate it.

`z_offset` in the config and the `SET_GCODE_OFFSET Z=...` offset are not intuitive! They go in different directions. `z_offset` specifies the global machine Z position when the probe triggers. So -1.8 means the probe triggers 1.8 mm *below* the bed surface. This means a lower `z_offset`, for example -1.9 creates *less* squish, since the print head will then *move up* a longer distance (1.9mm) before it considers itself at Z=0. However, doing live tuning on the printer by for example running `SET_GCODE_OFFSET Z=-0.1` lowers Z and creates *more* squish.

I inverted the algorithm in `SET_TEMP_BASED_Z_OFFSET` to have the default `z_offset` be the cold one, and then lowering Z (more squish) as it gets hotter.

* ASA, heat soaked to 60C and cleaned nozzle: Performs well on z_offset = -1.877 (maybe sliightly squished)
* PLA, print from cold (32C) and cleaned nozzle: Performs well on z_offset = -1.807
* ASA, heat soaked to 58C and somewhat clean nozzle: Performs well on z_offset = -1.800

I went crazy from the inconsistent results. I ended up disabling `SET_TEMP_BASED_Z_OFFSET` again and setting `z_offset = -1.800`. Today this seems to work fine both for PLA from cold and for ASA from hot.

# 2025-07-24 and 2025-07-27 - Filament tuning!

## Prusament ASA

**Temperature:** I printed the temperature tower in Orca slicer from 250 - 270 C. 265 C and up has significantly more stringing and surface artifacts than the lower temperatures. But I cannot tell much difference between 250 and 260. I settled for **260 C** both because it's the default, it's right in the middle of the Prusament recommended range. And it's also the highest temperature that did not produce any artifacts, which I guessed would improve layer adhesion and possible max flow rate.

**Maximum Volumetric Flow Rate**: I printed the Orca max flow rate test at 260C. Was able to finish the model up to 50 mm^3/s without the filament sensor erroring. But I start seeing gaps/artifacts at 45 mm^3/s. So I select **40 mm^3/s** as my max flow rate for ASA.

**Flow rate:** The Orca default for ASA was 0.92 which seems low. I printed the two test passes from the built in Orca calibration. Really can't tell much difference at all between EM 0.97 and 1.00. Settled for **0.99** since it was in that range, and it was what Widar had in his configs.

**Pressure Advance:** I printed three PA patterns from the Orca built in calibration. For velocity 120, 300 and 450. I doubt the printer can ever reach 450 on this short straights but anyway. Velocity was 3000 for all of them. The bulging really did not stop fully until PA ~0.05. But the gaps went all the way down to PA ~0.03, so the best should be somewhere in that range. I'll settle for **0.04** because it was what I had in SuperSlicer from before.

**Retraction:** I printed the Orca retraction test from 0.0 to 1.2 mm retraction. There is only visible stringing on the first section with zero retraction. According to the [Orca retraction guide](https://github.com/SoftFever/OrcaSlicer/wiki/retraction-calib) this is common on plastics with minimal oozing. The guide recommends a retraction of 0.2 - 0.4mm in this case. I'm going with the higher here: **0.4mm**. That's still half of the default retration (0.8mm).

**Shrinkage and dimensional accuracy (XY):** I first printed the Orca tolerance test. Measured the length of the object and got 99.6% as rough X-Y filament shrinkage. Then I printed the califlower with this new rough shrinkage. The result showed shrinkage 99.85%. Adding this new shrinkage to the old one resulted in **99.45%** XY filament shrinkage.

## Prusament PLA

**Temperature & Maximum Volumetric Flow Rate:** I printed the temperature tower in Orca slicer from 210 - 225 C. The chamber was around ~34 C and the doors were open. Bed temp at 60 C. The stringing over the long areas are there from 220 C and up. 215 C which is the default in Orca and also what I used in SuperSlicer seems fine. But 210 C has a bit less stringing on the narrow needle part. However, lower temp = lower max flow. I measured the max flow at 212 C for PLA and started seeing print issues at 34 mm^3/s already. So I will settle for **213 C** to get some of that string free goodness but without deviating too much from the values I know have worked well for me in the past, or getting too hit by lowered max volumetric flow rate. I now also lower the max volumetric flow for PLA to **30 mm^3/s** to be on the safe side.

* Prusament PLA @ 220C: 39 mm^3/s. Filament sensor errored at 44
* Prusament PLA @ 212C: 34 mm^3/s. Added on 2025-07-25 since I lowered the print temp

**Flow rate:** Started out with the default of 0.98. In pass 1 the `0` was very good, but had some gaps where the infill meets the perimeter. The +5% had a slight rougher surface but also less gaps along the edges. So I bumped EM +5% (1.03) for pass 2 it was tight, as usual. I think everything from -4% to +-0% was good looking, but finally decided -3% was the best. So I settled for flow **1.00**.

**Pressure Advance:** I printed the PA pattern for acceleration 2000 and 4000 and speeds 120 and 300. Around PA 0.05 is where the corner stops bulging, but the same value sadly has some gapping anyway. Following Elli's advice I'll accept some gapping to prioritize sharp corners. So **0.05** it is.

**Retraction:** I printed the Orca retraction test from 0.0 to 1.2 mm retraction. There is only visible stringing on the first section with zero retraction. According to the [Orca retraction guide](https://github.com/SoftFever/OrcaSlicer/wiki/retraction-calib) this is common on plastics with minimal oozing. The guide recommends a retraction of 0.2 - 0.4mm in this case. I'm going with the higher here: **0.4mm**. That's still half of the default retration (0.8mm).

**Shrinkage and dimensional accuracy (XY):** I just copied what Widar had for filament shrinkage: **99.89%**.

## Prusament PETG

**Temperature:** I printed the temperature tower in Orca slicer from 235 - 260 C. The chamber was around ~37 C and the doors open. Bed temp at 90 C. Widar uses 240 C for PETG and I have always used 250 C. Looks like Widar has a point here. 240 C has noticeably less stringing, albeit still lots of stringing compared to PLA/ASA. The retraction here is the Orca default 0.8mm. I will calibrate that later to see if I can reduce PETG stringing even more. I'll change PETG to **240 C** for now!

**Maximum Volumetric Flow Rate**: The lower print temp means I need to re-test max volumetric flow rate! There were a few inconsistencies at 33mm^3/s and then lots of failures at 35mm^3/s. So I lower the max flow rate to 30, should be safe enough.

* Prusament PETG @ 250C: 41 mm^3/s. Filament sensor errored at 45
* Prusament PETG @ 240C: 33 mm^3/s. Added on 2025-07-25 since I lowered the print temp

**Flow rate:** I started out with flow rate 1.0 since it was the default in Orca, and Widar had it in his profiles. For the first pass the +-0% change came out perfectly. So I'm just going to skip the second pass and just go with `1.00`.

**Pressure Advance:** I printed the PA pattern for speeds 120 and 300 as well as accelerations 2000 and 4000. PA 0.06 looked good. There almost no bulging was present at all at all speeds and accels, and very little gapping. But I then also printed the PA tower method and tried to find the height of the best corner. On that I though the corner bulging stopped at PA **0.068**, so I'm going to choose that since Elli says to lean towards higher values when in doubt.

**Retraction:** I printed the Orca retraction test from 0.0 to 1.3 mm retraction. Sadly I could not make anything useful of the output. There was stringing all the way up. The least stringing was at the bottom of the towers, where the retraction supposedly is the least? Since Elli [recommends staying under 1mm](https://ellis3dp.com/Print-Tuning-Guide/articles/retraction.html) for a direct drive extruder, and Widar can print PETG just fine and he has the default retraction of **0.8**, I'm going to leave it there for now.

**Shrinkage and dimensional accuracy (XY):** I just copied what Widar had for filament shrinkage: **99.78%**. When printing the Orca tolerance test all outside dimensions seem spot on, so that number is probably very good. However, the holes were a bit small. The 6mm hex key could only be squeezed into the 0.1mm extra tolerance hole. I set the printer global *X-Y hole compensation* setting to 0.05 and printed another one. Now the allen key can be forced into the hole with no extra tolerances, but it's really tight.

## Prusament PC Blend

My single roll of black Prusament PC blend is from way back when we bought Ymer, our Prusa Mini. But I have not used it much. So it's been sitting in the sealed bag most of the time. Hopefully it has not deteriorated too much. Worst case, whenever I get a new roll, I might need to tweak some parameters a little bit.

**Temperature:** I prented the temperature tower in Orca slicer from 265 - 285 C with Prusas recommended temp of 275 right in the middle. 275 is OK. At 280 there is significantly more stringing. At 270 there was a bit less stringing and a tiny bit less unwanted artifacts. But since when I print PC I probably do that to optimize for strength, not looks, and as a result I choose **275 C** here.

**Maximum Volumetric Flow Rate**: I printed the Orca max flow rate test at 275C. Started seeing artifacts at 31 mm^3/s, so I settle for a maximum flow rate of **28 mm^3/s**.

**Flow rate:** The default Orca EM for PC was 0.94. I printed pass 1 and saw gaps pretty high up. I set EM to 1.16 and printed pass two. I could se one single gap at -9% here, but none at -8%. So I selected -8% and set my EM (flowt rate) to **1.06**. The [Prusa datasheet for PC Blend](https://prusament.com/wp-content/uploads/2022/10/PCBlend_Prusament_TDS_2022_16_EN.pdf) states EM 1.034.

**Pressure Advance:** The PA pattern is hard to interpret. There are large amounts of gapping throughout the entire range. Maybe that's a sign of too low EM. But I doubt that 1.06 can be that much too low. Widar and I picked PA ~0.07. I then printed the PA tower and it also pointed at **0.07** being the best PA.

**Retraction:** Absolutely no stringing in the retraction test in Orca. So lowering the retraction to **0.4mm**.

**Shrinkage and dimensional accuracy (XY):** I first printed the Orca tolerance test. The holes were a bit too small (even though X-Y hole compensation was already set to 0.05). But it also warped and was a pretty bad print overall. I measured the outside length of this tolerance test and computed a shrinkage of 99.45% so I set this up in the slicer. Then I printed the califlower with this new shrinkage. After battling some warping I finally got a good print and it was near prefect. The spreadsheet gave me 99.97% shrinkage. So 99.45% * 99.97% = **99.42%** in new shrinkage. I also have -0.32 degrees angle skew. Not related to this filament though. Will ignore this small error.


# 2025-07-28 - Fix skew

I was initially very skeptical towards fixing mechanichal skew with software correction. But the [Califlower] gave a serious impression. Since I got almost identical skew in Califlower for three different prints in three different filaments:

* Prusament PETG: -0.29° error
* Prusament ASA: -0.34°
* Prusament PC Blend: -0.32° error

I decided that it probably helps more than it hurts to do skew correction for roughly these values. I picked the one with the error in the middle (PC Blend) and applied the skew correction recommended by the Califlower spreadsheet.

I then printed a Califlower in PLA. And the skew error was 0.03°. Well within measurement error margin! Amazing. Now I really want to get the Calilantern for Z skew calculations.

[Califlower]: https://vector3d.shop/products/califlower-calibration-tool-mk2

# 2025-07-28 - PC Blend cooling?

PC Blend shrinks and warps quite easily. It is known to have layer shifting artifacts due to dynamic cooling for example. Is this something I can improve on by tweaking the part cooling fan settings? Currently my slicer cooling settings are mostly just guesswork for the hotter filaments (ASA + PC Blend).

General [cooling tips and tricks from Elli](https://ellis3dp.com/Print-Tuning-Guide/articles/cooling_and_layer_times.html):
* Enclosed printers want lots of part cooling
* Smaller objects need more part cooling than large objects. Because large objects tend to warp more, and less part cooling mitigate some warping.
* Variable fan speed can easily create inconsistent layers and banding
* Increasing minimum layer time can help a lot, so you don't print a new layer on a still soft layer that is still shrinking.

Printing a bunch of benchys with different cooling and other modifications. All prints had:
* the benchy placed at the default center location, with starboard towards the doors
* the chamber temp was ~60-63C when starting the print. Chamber stabilized at ~64-65C during printing
* the printer doors were closed, but the closet door was wide open

It should be kept in mind that a benchy is a small print. So the settings found here might not apply for optimal cooling of larger prints. This print is so small that the `slow_down_layer_time` really affected the printing speed. My default value for this (taken from PrusaSlicer for the Core One) was 20 seconds, and this was a limiting factor for the overall print speed.

1. Default settings (Commit [8fe31b6](https://github.com/faern/3dprinter-config/commit/8fe31b601dd15a3698cedb2e084cde7c95e8c147)). Fan 50-60%. Print time 1h17m: Looks good overall. Some minor banding on the hull. One tiny layer shift/banding on the chimney.
2. 100% fan constant speed. Print time 1h17m: Very similar artifacts as on #1, but a bit worse. The hull is a bit uneven. Probably from different layers shrinking a different amount.
3. 10 seconds layer time (`slow_down_layer_time`). Print time 52m: Almost indistinguishable from #1, but maybe a tiny bit better results. The banding in the hull is slightly less noticeable.
4. 20% fan constant speed. Print time 1h17m: Completely indistinguishable from #1.
5. 30 seconds layer time (`slow_down_layer_time`). Print time 1h39m: No real noticeable difference

The results are very anticlimactic. No cooling changes made any real differences. So keeping my old values.


# 2025-07-31 - Best infill pattern?

I watched Thomas Sanladerer's video https://www.youtube.com/watch?v=nV3GbN6hLjg and learned that Cubic (and Adaptive Cubic) are really great infill patterns.

* Cubic is the strongest infill according to Tomas test
* Cubic is pretty fast (13% faster than gyroid)

I'm switching out my default infill pattern from the Orca default (Cross hatch) to Cubic now!


# 2025-08-03 - New lower printer placement and new input shaping!

To accomodate for my new filament drier (that has not yet arrived) I had to move the printer down, so it would fit on top of Veiron. Just ~20 cm under the shelf where Veiron sits is another shelf. So I planned to just move it to that and remove the old shelf. But the new shelf was not flat. So I had to put some plywood under one side to level it. I then jammed some wedges in on one side to make the shelf sit rock solid. It was not screwed in place, just placed on top of two wooden beams. With the wedges in place I crewed the shelf to the beams. Now it was very stable and sitting still.

After placing Veiron on the new shelf I re-ran input shaping to accomodate for the new home. The results were very similar to before. Max accel ~4200.

```
faern@veiron:~ $ ~/klipper/scripts/calibrate_shaper.py /tmp/calibration_data_y_20250803_175209.csv
Fitted shaper 'zv' frequency = 39.8 Hz (vibrations = 6.3%, smoothing ~= 0.101)
To avoid too much smoothing with 'zv', suggested max_accel <= 6200 mm/sec^2
Fitted shaper 'mzv' frequency = 37.6 Hz (vibrations = 0.1%, smoothing ~= 0.144)
To avoid too much smoothing with 'mzv', suggested max_accel <= 4200 mm/sec^2
Fitted shaper 'ei' frequency = 44.6 Hz (vibrations = 0.0%, smoothing ~= 0.162)
To avoid too much smoothing with 'ei', suggested max_accel <= 3700 mm/sec^2
Fitted shaper '2hump_ei' frequency = 55.4 Hz (vibrations = 0.0%, smoothing ~= 0.176)
To avoid too much smoothing with '2hump_ei', suggested max_accel <= 3400 mm/sec^2
Fitted shaper '3hump_ei' frequency = 66.6 Hz (vibrations = 0.0%, smoothing ~= 0.185)
To avoid too much smoothing with '3hump_ei', suggested max_accel <= 3200 mm/sec^2
Recommended shaper is mzv @ 37.6 Hz
faern@veiron:~ $ ~/klipper/scripts/calibrate_shaper.py /tmp/calibration_data_x_20250803_175209.csv
Fitted shaper 'zv' frequency = 45.2 Hz (vibrations = 11.6%, smoothing ~= 0.081)
To avoid too much smoothing with 'zv', suggested max_accel <= 8000 mm/sec^2
Fitted shaper 'mzv' frequency = 29.6 Hz (vibrations = 1.4%, smoothing ~= 0.232)
To avoid too much smoothing with 'mzv', suggested max_accel <= 2600 mm/sec^2
Fitted shaper 'ei' frequency = 40.0 Hz (vibrations = 0.4%, smoothing ~= 0.201)
To avoid too much smoothing with 'ei', suggested max_accel <= 3000 mm/sec^2
Fitted shaper '2hump_ei' frequency = 47.2 Hz (vibrations = 0.0%, smoothing ~= 0.242)
To avoid too much smoothing with '2hump_ei', suggested max_accel <= 2400 mm/sec^2
Fitted shaper '3hump_ei' frequency = 84.8 Hz (vibrations = 0.0%, smoothing ~= 0.114)
To avoid too much smoothing with '3hump_ei', suggested max_accel <= 5300 mm/sec^2
Recommended shaper is 3hump_ei @ 84.8 Hz
```

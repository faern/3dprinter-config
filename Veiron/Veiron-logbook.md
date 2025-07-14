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


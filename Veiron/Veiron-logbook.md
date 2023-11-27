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


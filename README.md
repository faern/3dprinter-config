# faern's and widar's 3d printer setup

Hi and welcome to my stash of:
  * Slicer profiles
  * Printer firmware configurations
  * Hardware build logs, tuning benchmark dumps etc.

Printer specific configuration can be found under the directories with the name of the printer.

## Printers

* [Veiron](Veiron/README.md)

## Firmware config

See `$printer_name/Klipper-config` for the files.

## SuperSlicer profiles

I use SuperSlicer and I originally based everything off of [Ellis SuperSlicer profiles]. I then did
lots of tuning with [Ellis' Print Tuning Guide] and from other sources. The result is versioned in
this repository under `$printer_name/SuperSlicer-profiles/``

These are stored as separate INI files for each profile (printer, filament and print profiles
separately). Use the [split_superslicer_config_bundle]
script to generate these files from an exported SuperSlicer Config Bundle:

1. Export a Config Bundle from SuperSlicer (File -> Export -> Export Config Bundle...)
   Save it under any `$name.ini`
2. Run [split_superslicer_config_bundle] with the exported bundle and desired output directory:
   ```
   $ ./split_superslicer_config_bundle.py $name.ini --output-dir $printer_name/SuperSlicer-profiles/
   ```
3. Inspect the diff and commit it.


[Ellis SuperSlicer profiles]: https://github.com/AndrewEllis93/Ellis-SuperSlicer-Profiles
[Ellis' Print Tuning Guide]: https://ellis3dp.com/Print-Tuning-Guide
[split_superslicer_config_bundle]: ./split_superslicer_config_bundle.py

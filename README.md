# SB3-SVG-Convertor
This project will convert the drawing made in Scratch3 into an SVG file.<br>

## Usage Guide

### Classic Usage:
To use the converter in the standard manner, execute the "convertor.py" file with at least one argument indicating the location of the sb3 file to convert:

```bash
python ./convertor.py <sb3_file_location>
```

### Shortcut:
A shortcut has been established for running the converter in partnership with the tabgo project. Simply type the following command:

```bash
python ./convertor.py tabgo
```

This command instructs the converter to search for the file in "../tabgo/data/sb3/Programme_scratch.sb3".

### Result Display Options:
There are two possible options for displaying the result:

#### Option 1:
Adding nothing after specifying the location ensures that the obtained result is a simple line.

#### Option 2:
Additional arguments can be added in the following order: scale (int), translation x (int), translation y (int).

- **Scale**: Adjusts the size of the figure (use 1 to maintain the original size).
- **Translation x**: Indicates the number of pixels the figure should move horizontally.
- **Translation y**: Indicates the number of pixels the figure should move vertically.

The x and y translations are useful if the figure extends beyond the boundaries of the SVG after scaling (> 1).

If scale is provided with Option 2 (i.e., if more than one argument is provided), then the rendering is automatically adapted for the Ozobot robot.
Here's the addition for your README section on Ivy bus usage:

## Usage with Ivy Bus

To open the converter using Ivy Bus, execute the "ivyCconvertor.py" file:

```bash
python ./ivyConvertor.py
```

The converter will to be looped in communication with the Ivy bus. It is open to 4 types of messages:

1. `"tabgo : *"` -> Executes the program by searching for the sb3 file crated by TaBGO with classic rendering.
2. `"print tabgo: .*"` -> Executes the program by searching for the sb3 file crated by TaBGO with Ozobot rendering.
3. `"convert:(.*?)location=.*"` -> Executes the program with the specified sb3 file and classic rendering.
4. `"print convert:(.*?)location=.*"` -> Executes the program with the specified sb3 file and Ozobot rendering.

When another program sends a message following one of the indicated types, the associated action will be executed immediately. It's possible to add `"scale=.*"`, `"x=.*"`, and `"y=.*"` for the print case.

---

For more informations, read the "Documentation technique de développement" file.

#### The Available Blocks :
- pen_penUp
- pen_penDown
- motion_movesteps
- motion_changeyby
- motion_changexby
- motion_setx
- motion_sety
- motion_gotoxy
- motion_turnright
- motion_turnleft
- motion_pointindirection
- control_repeat
- control_repeat_until
- control_if
- control_if_else
- data_setvariableto
- data_changevariableby
- operator_or
- operator_and
- operator_not
- operator_equals
- operator_gt
- operator_lt
- operator_add
- operator_substract
- operator_divide
- operator_mod
- motion_xposition
- motion_yposition
- senting_touchingobject
- procedure_definition
- procedure_prototype
- procedure_call

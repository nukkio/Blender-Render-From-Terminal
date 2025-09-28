
# Render from terminal
## Overview
A Blender extension to write script file to launch renders from the terminal.

Write file `.sh` and, but poorly tested, `.bat`.

Launching renders from the command line is useful for:

- automating the rendering phase
- optimizing resources
- adding external commands (editing renders, uploading them online, sending messages...)
- launching the render remotely

With this addon the script creation is simplified and can then be modified and customized according to your needs.

With default values ​​this addon writes a script to start rendering the current frame with the project settings; clicking the "Write script" button creates a `.sh` and/or `.bat` file in the same folder as the `.blend` project, with the same name followed by "_render":`[blend file name]_render.sh`

This file is ready to be launched from the terminal with
```shell
./<nome blend file>_render.sh
```

*****************
## The script
The created script has a function "startrender" which is called by passing several parameters:

- the name to give to the render\
empty string to use the project settings
- frames to render
	- **1,3**: render frame 1 and 3
	- **1-3**: render from frame 1 to frame 3, inclusive
	- **1..3**: as 1-3
	- **no value**: the current frame when the "write script" button is pressed
- Resolution Scale\
as "Resolution scale" nel pannello "Format"
- render engine\
BLENDER_EEVEE_NEXT, BLENDER_WORKBENCH, CYCLES or empty string to use the project settings
- render quality\
"max samples" for Cycles and "samples" for Eevee
- scene to use
- whether or not it should overwrite the renders
- a python script to run before render

The values ​​for resolution percentage, render engine, render quality and overwrite are collected in a Python string that is passed to blender with the `--python-expr` parameter.\
The other values ​​are passed with the corresponding blender command line parameters.

## Use
### Frame to render
In this panel you choose which frames to render

- **Render only current frame**:\
renders only the current frame; (the same result is obtained if you leave the "frames to render" field empty).

- **Launch animation as in project**\
launches the animation as set in the project; if the "Enable Override values" option is not selected in the script, Blender is launched with the `-a` option; if instead there are changes to the project settings ("Enable Override values" selected) Blender is launched passing the frame interval set with "Frame Start" and "End" of the animation.

- **frames to render**\
	- **1,3**: render frame 1 and 3
	- **1-3**: render from frame 1 to frame 3 included
	- **1..3**: as 1-3
	- the above values ​​can be entered together; e.g.; 1,3,5-10 (render frames 1 and 3, and frames 5 to 10)
	- no value: the current frame when the "write script" button is pressed

- **animation as singles**\
If there is an animation, e.g. 1-5, the command line does not have the animation `-f 1..5`, but the single separate frames: `-f 1,2,3,4,5`.\
Useful when used together with "**new call each render**"
- **new call each render**\
For each frame indicated in the "frames to render" field a blender call is made.\
For example:
	- in the "frames to render" field there is: 1,3,5-8
	- if "**new call each render**" **NOT selected**:
		* Blender is launched only once by passing `-f 1,3,5..8`
	- if "**new call each render**" **is selected**:
		* Blender is launched three times, passing\
			+ the first time `-f 1`\
			+ the second time `-f 3`\
			+ and the third time `-f 5..8`
	- if "**new call each render**" **is selected** e also "**animation as singles**" **is selected**:
		* Blender is launched six times, passing\
			+ the first time `-f 1`\
			+ the second time `-f 3`\
			+ the third `-f 5`
			+ the fourth `-f 6`
			+ the fifth `-f 7`
			+ the sixth `-f 8`

	This can be useful if you need to reload the entire project before each render.
	



### Additional commands
These are commands that you want to run before or after the renders.

**Warning**: these values ​​will be copied into the script without any syntax checking or anything else.

- **Start**\
before launching the first Blender call
- **Pre**\
before launching any Blender call
- **Python**\
python file to pass to blender (`-P pyfile.py`)
- **Post**\
after each Blender call
- **End**\
after the last Blender call

### Override values
With these values ​​the script will launch the renders by modifying the project settings.

- **Enable Override values**\
Enable override
- **Output path**\
Like the "Output path" field in the "Output" panel, if empty uses the project setting
- **Override overwrite** + **Overwrite**\
With "Override overwrite" selected it allows you to choose whether to overwrite the renders or not
- **Override placeholder** + **Placeholder**\
With "Override placeholder" selected it allows you to choose whether to create placeholder or not.\

> **Note for multiple PCs or parallel sessions**	
> If the script needs to be run on multiple computers or from different sessions (terminals) on the same computer, it is best to uncheck "overwrite" and check "placeholder" to avoid the same frame being rendered multiple times, even if these options are set differently in the project.\

- **Render Engine**\
Choosing which render engine to use:\
	- Default (as set in the project)
	- BLENDER_EEVEE_NEXT
	- BLENDER_WORKBENCH
	- CYCLES

- **Samples**\
rendering quality, "max samples" for Cycles and "samples" for Eevee
- **%**\
As "Resolution Scale", 0: Use project setting
- **Scene**\
Scene to load before launching the render (`-S [scene name]`)

### Write script
Write the script:\
	`[blend file name]_render.sh`

**Warning**: The .bat file for Windows has not been adequately tested.

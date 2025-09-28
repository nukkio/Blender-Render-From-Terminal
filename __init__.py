# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##################################
#write script, .sh and .bat, for launch render from terminal
##################################
import bpy
import os
import math
from mathutils import Vector
from mathutils import Matrix
from bpy.types import (
						Panel, 
						Operator, 
						Scene, 
						PropertyGroup
					)
from bpy.props import (
						BoolProperty,
						IntProperty,
						EnumProperty,
						StringProperty,
						PointerProperty
					)

#from bpy.app.handlers import persistent

class RFT_Settings(bpy.types.PropertyGroup):
	
	rft_frametorender:StringProperty(
		name = "frames to render",
		description = "Frames to render: x,y,z= render the frame x, y and z; x-z= render the frame from number x to z; empty=current frame",
		default = ""
	)
	rft_onlycurrent: bpy.props.BoolProperty(
		name="Render only current frame",
		default=False,
		description="Render only current frame",
	)	
	rft_animationdefault: bpy.props.BoolProperty(
		name="launch animation as in project",
		default=False,
		description="Launch render animation as saved in project (blender -a)",
	)	
	rft_onlyactivecamera: bpy.props.BoolProperty(
		name="Fix framing only for active camera",
		default=False,
		description="Change camera FoV or position only for active camera or for all cameras in active scene",
	)
	rft_animasstillseq: bpy.props.BoolProperty(
		name="animation as singles",
		default=False,
		description="Render animation (s-e, start-to end frame) as a series of single renders",
	)
	rft_newinstance: bpy.props.BoolProperty(
		name="new call each render",
		default=False,
		description="Call blender for each frame, or frames sequence, to render",
	)
	rft_writeSH: bpy.props.BoolProperty(
		name="Write shell script",
		default=True,
		description="Write shell script, '<blend file name>_render.sh'",
	)
	rft_writeBAT: bpy.props.BoolProperty(
		name="Write batch script",
		default=False,
		description="Write batch script, '<blend file name>_render.bat' - Warning: poorly tested",
	)
	##command
	rft_comm_start:StringProperty(
		name = "Start",
		description = "Command before start all renders",
		default = "echo \"**** Start renders\""
	)
	rft_comm_pre:StringProperty(
		name = "Pre",
		description = "Command before launch each Blender execution",
		default = "echo \"**** before launching Blender\""
	)
	rft_comm_python:StringProperty(
		name = "Python",
		description = "Python file to run launching Blender (blender -P file.py)",
		default = ""
	)
	rft_comm_post:StringProperty(
		name = "Post",
		description = "Command after finish each render/Blender call, i.e. sleep 10s",
		default = "echo \"**** after close Blender\""
	)
	rft_comm_end:StringProperty(
		name = "End",
		description = "Command after all renders, i.e. 'shutdown -P 5'",
		default = "echo \"**** End renders\""
	)
	##override
	rft_or_enabled: bpy.props.BoolProperty(
		name="Enable Override values",
		default=False,
		description="Enable Override values",
	)
	rft_or_filename:StringProperty(
		name = "Output path",
		description = "Directory/name to save animations, # characters define the position and padding of frame numbers",
		default = ""
	)
	rft_or_overwrite: bpy.props.BoolProperty(
		name="Override overwrite",
		default=False,
		description="Override overwrite option",
	)
	rft_or_overwritevalue: bpy.props.BoolProperty(
		name="Overwrite",
		default=False,
		description="Overwrite existing files while rendering",
	)
	rft_or_placeholder: bpy.props.BoolProperty(
		name="Override placeholder",
		default=False,
		description="Override placeholder option",
	)
	rft_or_placeholdervalue: bpy.props.BoolProperty(
		name="placeholder",
		default=True,
		description="Create empty placeholder files while rendering frames (similar to Unix 'touch')",
	)
	rft_or_renderengine:bpy.props.EnumProperty(
		name="Render Engine",
		description="Engine to use for rendering",
		items=[
			("DEFAULT", "Default","Use engine from blend project when render from script",0),
			("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE_NEXT","Use BLENDER_EEVEE_NEXT when render from script",1),
			("CYCLES", "CYCLES","Use CYCLES when render from script",2),
			("BLENDER_WORKBENCH", "BLENDER_WORKBENCH","Use BLENDER_WORKBENCH when render from script",3)
		],
		default="DEFAULT"
	)
	rft_or_renderquality: bpy.props.IntProperty(
		name = "Samples",
		description="'Max samples' for Cycles and 'Samples' for Eevee - 0=default from blend project",
		default=0,
		min=0
	)
	rft_or_percres: bpy.props.IntProperty(
		name = "%",
		description="Percentage scale for render resolution - 0=use value from blend project",
		default=0,
		min=0
	)
	rft_or_scene:StringProperty(
		name = "Scene",
		description = "Scene to render - ''=use scene as saved in blend project",
		default = ""
	)
	
#	rft_cameras=[]
#	rft_fixingactive: bpy.props.BoolProperty(
#		name="fixing",
#		default=False,
#		description="Camera framing fixing active",
#	)
#	rft_addingmargins: bpy.props.BoolProperty(
#		name="rft_addingmargins",
#		default=False
#	)
#	rft_targetOb: bpy.props.PointerProperty(type=bpy.types.Object)
#	rft_pixeltoX: bpy.props.IntProperty(
#		name = "Pixels to X",
#		description="Pixels to add to resolution X of render (to left + to right)",
#		default=0
#	)
#	rft_pixeltoY: bpy.props.IntProperty(
#		name = "Pixels to Y",
#		description="Pixels to add to resolution Y of render (to top + to bottom)",
#		default=0
#	)
#	rft_startXres: bpy.props.IntProperty(
#		name = "rft_startXres",
#		default=0
#	)
#	rft_startYres: bpy.props.IntProperty(
#		name = "rft_startYres",
#		default=0
#	)
#	rft_startAR: bpy.props.FloatProperty(
#		name = "rft_startAR",
#		default=1
#	)
#	rft_fixedframing:bpy.props.EnumProperty(
#		name="Maintain framing",
#		description="How to maintain the framing",
#		items=[
#			("FOV", "Field of view","Maintain the frame by changing the field of view angle", "DRIVER_ROTATIONAL_DIFFERENCE",0),
#			("POS", "Position","Maintain the frame by changing the camera position along the local Z-axis", "TRACKING_FORWARDS_SINGLE",1)
#		],
#		default="FOV"
#	)
#	rft_doforobj:bpy.props.EnumProperty(
#		name="Use DoF or Object",
#		description="Calculate new position using DoF or the distance from camera to object",
#		items=[
#			("DOF", "Depth of Field","Calculate new position using the Depth of Field from camera settings", "CAMERA_DATA",0),
#			("OBJ", "Obiect","Calculate the new position using the distance between the camera and an object", "TRACKING_FORWARDS_SINGLE",1)
#		],
#		default="DOF"
#	)
#	rft_restoreposs: bpy.props.BoolProperty(
#		name="rft_restoreposs",
#		default=False
#	)

class RFT_OT_writescript(bpy.types.Operator):
	bl_idname = "render.writescript"
	bl_label = "Write script"
	bl_description = "Writes the script file to the same folder as the open project"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		scn = context.scene
		rnd = scn.render
		rftsettings = scn.rftsettings
		
####		#todo:
####		if bpy.data.is_saved:
####		filepath 
####		if bpy.data.is_dirty:
#		print("bpy.data.is_saved",bpy.data.is_saved)
#		print("bpy.data.is_dirty",bpy.data.is_dirty)
#		print("filepath",bpy.context.blend_data.filepath) 
		if bpy.data.is_saved==False or bpy.context.blend_data.filepath=="":
			self.report({'ERROR'},"Save project!")
	#		'DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY')
			return {'CANCELLED'}
		
		#nome del file blend
		blendName= bpy.path.basename(bpy.context.blend_data.filepath).split(".")[0]
		
		file_name=os.path.splitext( os.path.split(bpy.data.filepath)[1])[0]
#		outputFolderAbs=os.path.split( bpy.path.abspath(rnd.filepath) )[0]
		outputFolderAbs=os.path.split( bpy.path.abspath(bpy.data.filepath) )[0]
#		print("outputFolderAbs",outputFolderAbs)
		
		self.resperc=rnd.resolution_percentage
		
		#######################
		#check filepath, if "" or "/tmp\" alert user
		if(rnd.filepath=="" or rnd.filepath=="/tmp\\" or rnd.filepath=="/tmp/"):
			self.report({'ERROR'},"Error in Output path, set a valid path")
			return {"CANCELLED"}
		#######################
		#######################
		relp=""
		try:
			relp=bpy.path.relpath(rnd.filepath)
		except:
			relp=bpy.path.abspath(rnd.filepath)
		
		self.outputFolder=os.path.split( relp )[0]
		#######################
		
##		#add n frame
		cfs=scn.frame_current
		nframescript = "_"+str(f'{cfs:0{3}d}')
	
		####################
##		##control file path, if output folder exist
#		check exist self.outputFolderAbs+ os.path.sep
		renderFolder=outputFolderAbs
		renderFolderExist = os.path.exists(renderFolder)
		creatingFolder=""
		if (renderFolderExist==False):
			try:
				os.makedirs(renderFolder)
				print(f"render folder '{renderFolder}' created.")
				creatingFolder="created"
				renderFolderExist=True
			except FileExistsError:
				print(f"render folder '{renderFolder}' already exists.")
				creatingFolder="already exists"
				renderFolderExist=True
			except PermissionError:
				print(f"Permission denied: Unable to create '{renderFolder}'.")
				creatingFolder=f"Permission denied: Unable to create '{renderFolder}'."
			except Exception as e:
				print(f"An error occurred: {e}")
				creatingFolder=f"An error occurred: {e}"
		if (renderFolderExist==False):
			self.report({'ERROR'},"Error creating render folder, no script created, error: "+ creatingFolder)
			return('FINISHED')
		####################
		##prepara i frame da renderizzare
		arframes=self.calculateframes(context)
		####################
		
		if rftsettings.rft_writeSH==True:
			scriptExt=".sh"
	##		fileScript=outputFolderAbs+ os.path.sep+blendName+nframescript+"_render"+scriptExt
			fileScript=outputFolderAbs+ os.path.sep+blendName+"_render"+scriptExt
			strScript=self.getScriptShell(context, arframes)
				
			with open(fileScript, 'w') as file:
				file.write(strScript)
				file.close()

			self.report({'INFO'},"script file written: "+fileScript)

		if rftsettings.rft_writeBAT==True:
			scriptExt=".bat"
	##		fileScript=outputFolderAbs+ os.path.sep+blendName+nframescript+"_render"+scriptExt
			fileScript=outputFolderAbs+ os.path.sep+blendName+"_render"+scriptExt
			strScript=self.getScriptBatch(context, arframes)
				
			with open(fileScript, 'w') as file:
				file.write(strScript)
				file.close()

			self.report({'INFO'},"script file written: "+fileScript)

#		'DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY')
		return {'FINISHED'}
		
	def initValue(self, context, cam):
		scene = context.scene
		rftsettings = scene.rftsettings
#		startAngle=cam.data.angle
		return True

	def calculateframes(self,context):
		scene = context.scene
		rftsettings = scene.rftsettings

		arframes=[]
		errorInsertRegions=False
		control=""
		ar_temp=[]
		startend=[]
		
		if rftsettings.rft_onlycurrent==True:
			arframes.append(str(scene.frame_current))
			return arframes
		if rftsettings.rft_animationdefault==True:
			arframes.append("-1")
			return arframes
		
		#split con la virgola
		#loop
			#cerca "-"
		strframes=rftsettings.rft_frametorender
		if strframes=="":
			strframes=str(scene.frame_current)
		strframes=strframes.replace("..","-")
		ar_temp=strframes.split(",")
#		print(len(ar_temp))
#		print(ar_temp)
		
		for x in ar_temp:
			if "-" in x:
				#se deve fare render singoli anche per le sequenze
				#aggiunge tutti i frame
				if rftsettings.rft_animasstillseq==True:
	#				if (x.startswith("-")==False and x.endswith("-")==False):
					startend=x.split("-")
					print("startend",startend)
					if len(startend)>1:
						s=-1
						e=-1
						for xx in startend:
							if xx!="":
								if s==-1:
									s=int(xx)
								elif e==-1:
									e=int(xx)
						if s==-1 or e==-1:
							s=max(s,e)
							arframes.append(str(s))
						else:
							e=e+1
							for i in range(s,e):
								arframes.append(str(i))
				else:
					arframes.append(str(x.replace("-","..")))
			else:
				if x!="":
					arframes.append(str(x))
		print(len(arframes))
		print(arframes)
		
		return arframes
	
	def getScriptBatch(self,context,arframes):
		scn = context.scene
		rnd = context.scene.render
		rftsettings = scn.rftsettings
		
#		folder blender file
		mainPath=bpy.path.abspath("//")

#		path blender file
		filepath = bpy.data.filepath
		
#		nome del file
		fileName=bpy.path.basename(bpy.data.filepath)
		
#		executable path
		blenderPath=bpy.app.binary_path
		
		strScript=""
		strScript+="@echo off"+"\n"
		strScript+=""+"\n"
		strScript+="SETLOCAL"+"\n"
		strScript+="set mainPath="+mainPath+"\n"
		strScript+="set file=%mainPath%"+fileName+"\n"
		strScript+="set blenderPath="+blenderPath+"\n"
		
#		strScript+=":: set cyclesSamples="+str(scn.cycles.samples)+"\n"
#		strScript+=":: set eeveeSamples="+str(scn.eevee.taa_render_samples)+"\n"
#		strScript+=":: set renderEngine="+str(scn.render.engine)+"\n"
#		strScript+=":: BLENDER_EEVEE CYCLES"+"\n"
		
#		strScript+="set pythonName=render_from_terminal"+"\n"
#		strScript+="set pyfile=%mainPath%%pythonName%.py"+"\n"

		strScript+="\n"
		
		
		#########################################################
		#########################################################
		if rftsettings.rft_or_enabled==False:
			strScript+="set fileout="+"\n"
			strScript+="set resperc=0"+"\n"
			strScript+="REM 0: value from .blend file"+"\n"
			strScript+="set rendeng="+"\n"
			strScript+="REM BLENDER_EEVEE_NEXT - BLENDER_WORKBENCH - CYCLES"+"\n"
			strScript+="set rendqual=0"+"\n"
			strScript+="REM max samples for Cycles and samples for Eevee"+"\n"
			strScript+="set scene="+"\n"
			strScript+="REM empty: value from .blend file"+"\n"
			strScript+="set overwrite="+"\n"
			strScript+="REM empty: value from .blend file"+"\n"
			strScript+="set pythonfile="+rftsettings.rft_comm_python+"\n"
			strScript+="REM .py file"+"\n"
		else:
			strScript+="set fileout="+str(rftsettings.rft_or_filename)+"\n"
			strScript+="set resperc="+str(rftsettings.rft_or_percres)+"\n"
			strScript+="REM 0: value from .blend file"+"\n"
			if rftsettings.rft_or_renderengine=="DEFAULT":
				strScript+="set rendeng="+"\n"
			else:
				strScript+="set rendeng="+str(rftsettings.rft_or_renderengine)+"\n"
			strScript+="REM BLENDER_EEVEE_NEXT - BLENDER_WORKBENCH - CYCLES"+"\n"
			strScript+="set rendqual="+str(rftsettings.rft_or_renderquality)+"\n"
			strScript+="REM max samples for Cycles and samples for Eevee"+"\n"
			strScript+="set scene="+str(rftsettings.rft_or_scene)+"\n"
			strScript+="REM empty: value from .blend file"+"\n"

			if rftsettings.rft_or_overwrite==False:
				strScript+="set overwrite="+"\n"
			else:
				strScript+="set overwrite="+str(rftsettings.rft_or_overwritevalue)+"\n"
			strScript+="REM empty: value from .blend file"+"\n"

			if rftsettings.rft_or_placeholder==False:
				strScript+="set placeholder="+"\n"
			else:
				strScript+="set placeholder="+str(rftsettings.rft_or_placeholdervalue)+"\n"
			strScript+="REM empty: value from .blend file"+"\n"

			strScript+="set pythonfile="+rftsettings.rft_comm_python+"\n"
			strScript+="REM .py file"+"\n"
		strScript+=""+"\n"
		#########################################################
		#########################################################
		
		allframes=""
		
		if rftsettings.rft_animationdefault==True and rftsettings.rft_onlycurrent==False:
			strScript+="set datarender=%TIME% "+"\n"
			allframes=str(scn.frame_start)+".."+str(scn.frame_end)
			if rftsettings.rft_comm_start!="":
				strScript+=rftsettings.rft_comm_start+"\n"
			if rftsettings.rft_or_enabled==False:
				strScript+="CALL \"%blenderPath%\" -b \"%file%\" -a"+"\n"
				strScript+="REM CALL :startrender "
				strScript+="\"%fileout%\", " 
				strScript+="\""+allframes+"\", " 
				strScript+="\"%resperc%\", "
				strScript+="\"%rendeng%\", " 
				strScript+="\"%rendqual%\", " 
				strScript+="\"%scene%\", " 
				strScript+="\"%overwrite%\", " 
				strScript+="\"%placeholder%\", " 
				strScript+="\"%pythonfile%\" " 
				strScript+=""+"\n"
			else:
				strScript+="REM CALL \"%blenderPath%\" -b \"%file%\" -a"+"\n"
				strScript+="CALL :startrender "
				strScript+="\"%fileout%\", " 
				strScript+="\""+allframes+"\", " 
				strScript+="\"%resperc%\", "
				strScript+="\"%rendeng%\", " 
				strScript+="\"%rendqual%\", " 
				strScript+="\"%scene%\", " 
				strScript+="\"%overwrite%\", " 
				strScript+="\"%placeholder%\", " 
				strScript+="\"%pythonfile%\" " 
				strScript+=""+"\n"
			if rftsettings.rft_comm_end!="":
				strScript+=rftsettings.rft_comm_end+"\n"
		else:
			if rftsettings.rft_newinstance==False:
				for i in arframes:
					allframes+=i+","
				if allframes.endswith(","):
					allframes = allframes[:-1]
#				print(allframes)
				if rftsettings.rft_comm_start!="":
					strScript+=rftsettings.rft_comm_start+"\n"
				strScript+="set datarender=%TIME% "+"\n"
				strScript+="CALL :startrender "
				strScript+="\"%fileout%\", " 
				strScript+="\""+allframes+"\", " 
				strScript+="\"%resperc%\", "
				strScript+="\"%rendeng%\", " 
				strScript+="\"%rendqual%\", " 
				strScript+="\"%scene%\", " 
				strScript+="\"%overwrite%\", " 
				strScript+="\"%pythonfile%\" " 
				strScript+=""+"\n"
				if rftsettings.rft_comm_end!="":
					strScript+=rftsettings.rft_comm_end+"\n"

			else:
				if rftsettings.rft_comm_start!="":
					strScript+=rftsettings.rft_comm_start+"\n"
				for i in arframes:
					strScript+="set datarender=%TIME% "+"\n"
					strScript+="CALL :startrender "
					strScript+="\"%fileout%\", " 
					strScript+="\""+i+"\", " 
					strScript+="\"%resperc%\", "
					strScript+="\"%rendeng%\", " 
					strScript+="\"%rendqual%\", " 
					strScript+="\"%scene%\", " 
					strScript+="\"%overwrite%\", " 
					strScript+="\"%pythonfile%\" " 
					strScript+=""+"\n"
				if rftsettings.rft_comm_end!="":
					strScript+=rftsettings.rft_comm_end+"\n"

		strScript+="\n"
		strScript+="CALL :msg \"end\"\n"
		strScript+="echo \"done\"\n"
		strScript+="\n"
		
		####################################
		
#		tmprow=0
#		for ireg in arObRegions:
#			comm=""
#			if(ireg.render==False):
#				comm="::"
#			
#			strScript+=comm+"set tmpImgName=\""+ireg.imageName+"\""+"\n"
#			strScript+=comm+"set datarender=%TIME% "+"\n"
#			strScript+=comm+"set datascript=%TIME% "+"\n"
#			strScript+=comm+"CALL :startrender "
#			strScript+=str(ireg.regionarea.minx)+", "
#			strScript+=str(ireg.regionarea.miny)+", "
#			strScript+=str(ireg.regionarea.maxx)+", "
#			strScript+=str(ireg.regionarea.maxy)+", "
#			strScript+="%tmpImgName%, "
#			strScript+=str(ireg.resolution)+", "
#			strScript+=str(ireg.resolutionPercent)+", "
#			strScript+=str(ireg.usecrop)+", "
#			strScript+=str(ireg.currframe)+", "
#			strScript+="\""+str(ireg.regionName)+"\" "
#			strScript+="\n"
#			strScript+=comm+"CALL :msg \"ok "+str(ireg.nrow)+" "+str(ireg.ncol)+"\""+"\n"
#			strScript+="\n"
		
#		strScript+="\n"
#		strScript+="echo \"done\"\n"
		strScript+="EXIT /B %ERRORLEVEL% \n"
		strScript+="\n"

		strScript+=":msg"+"\n"
		strScript+="SETLOCAL"+"\n"
		strScript+="set msg=%~1"+"\n"
		strScript+="set datamsg=%TIME%"+"\n"
		strScript+="::telegram-send \"%datarender% - %datamsg% - render %msg%\""+"\n"
		strScript+="echo \"%datascript% -- %datarender% - %datamsg% - render %msg%\""+"\n"
		strScript+="ENDLOCAL"+"\n"
		strScript+="EXIT /B 0"+"\n"
		strScript+="\n"
		
		strScript+=":startrender"+"\n"
		strScript+="SETLOCAL"+"\n"
		strScript+="set imageName=%~1"+"\n"
		strScript+="set curframe=%~2"+"\n"
		strScript+="set resolutionPercent=%~3"+"\n"
		strScript+="set renderEngine=%~4"+"\n"
		strScript+="set renderQuality=%~5"+"\n"
		strScript+="set scene=%~6"+"\n"
		strScript+="set renderoverwrite=%~7"+"\n"
		strScript+="set renderplaceholder=%~8"+"\n"
		strScript+="set pythonfile=%~9"+"\n"
##########################################		
		strScript+="set strscene="+"\n"
		strScript+="IF NOT [%scene%]==[] set strscene=-S %scene%"+"\n"
		strScript+="set strimage="+"\n"
		strScript+="IF NOT [%imageName%]==[] set strimage=-o %imagename%"+"\n"
		strScript+="set strpython="+"\n"
		strScript+="IF NOT [%pythonfile%]==[] set strpython=-P %pythonfile%"+"\n"

		strScript+="set pythonexpr=import bpy; scn = bpy.context.scene; rnd = scn.render; "+"\n"
		strScript+="IF %resolutionPercent% GTR 0 set pythonexpr=%pythonexpr% rnd.resolution_percentage=%resolutionPercent%;  "+"\n"
		strScript+="IF NOT [%renderEngine%]==[] set pythonexpr=%pythonexpr% scn.render.engine='%renderEngine%'; "+"\n"
		strScript+="IF %renderQuality% GTR 0 set pythonexpr=%pythonexpr% scn.cycles.samples=%$renderQuality%; scn.eevee.taa_render_samples=%renderQuality%; "+"\n"
		strScript+="IF NOT [%renderoverwrite%]==[] set pythonexpr=%pythonexpr% scn.render.use_overwrite=%renderoverwrite%; "+"\n"
		strScript+="IF NOT [%renderplaceholder%]==[] set pythonexpr=%pythonexpr% scn.render.use_placeholder=%renderplaceholder%; "+"\n"

#		strScript+="set comm=\"%blenderPath% -b \\\"%file%\\\" -x 1 %strscene% %strimage% --python-expr \\\"%pythonexpr%\\\" -f %curframe%\""+"\n"
		if rftsettings.rft_comm_pre!="":
			strScript+=rftsettings.rft_comm_pre+" \"%file%\" \"%imagename%\""+"\n"
		strScript+="CALL \"%blenderPath%\" -b \"%file%\" -x 1 %strscene% %strimage% --python-expr \"%pythonexpr%\" %strpython% -f %curframe%"+"\n"
		if rftsettings.rft_comm_post!="":
			strScript+=rftsettings.rft_comm_post+" \"%file%\" \"%imagename%\""+"\n"
		
		strScript+="CALL :msg \"%curframe%\""+"\n"

#######################################
#		strScript+="CALL \"%blenderPath%\" -b \"%file%\" -x 1 -o \"%imageName%\" -P \"%pyfile%\" -f %curframe%"+"\n"
		strScript+="ENDLOCAL"+"\n"
		strScript+="EXIT /B 0"+"\n"

		strScript+="\n"
		return strScript

	def getScriptShell(self,context,arframes):
		scn = context.scene
		rnd = context.scene.render
		rftsettings = scn.rftsettings
		
#		folder blender file
		mainPath=bpy.path.abspath("//")

#		path blender file
		filepath = bpy.data.filepath
		
#		nome del file
		fileName=bpy.path.basename(bpy.data.filepath)
		
#		executable path
		blenderPath=bpy.app.binary_path
		
		strScript=""

		strScript+="#! /bin/bash"+"\n"
		strScript+=""+"\n"
#		strScript+="mainPath=\""+mainPath+"\""+"\n"
#		strScript+="file=$mainPath\""+fileName+"\""+"\n"
		strScript+="blenderPath="+blenderPath+""+"\n"
		strScript+="datarender=$(date +\"%Y%m%d_%H-%M\")"+"\n"
		strScript+="datascript=$(date +\"%Y%m%d_%H-%M\")"+"\n"
		
#		strScript+="#cyclesSamples="+str(scn.cycles.samples)+"\n"
#		strScript+="#eeveeSamples="+str(scn.eevee.taa_render_samples)+"\n"
#		strScript+="#renderEngine="+str(scn.render.engine)+"\n"
#		strScript+="#### BLENDER_EEVEE_NEXT	BLENDER_WORKBENCH CYCLES"+"\n"
		
		strScript+="__dir=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\""+"\n"
		
		strScript+="\n"
		
		strScript+="msg()"+"\n"
		strScript+="{"+"\n"
		strScript+="\tmsg=$1"+"\n"
		strScript+="\tdatamsg=$(date +\"%Y%m%d_%H-%M\")"+"\n"
		strScript+="\t#telegram-send \"$datarender - $datamsg - render $1\""+"\n"
		strScript+="\techo \"$datascript -- $datarender - $datamsg - render $1\""+"\n"
		strScript+="}"+"\n"
		
		strScript+="function startrender()"+"\n"
		strScript+="{"+"\n"
		strScript+="\timagename=$1"+"\n"
		strScript+="\tcurframe=$2"+"\n"
		strScript+="\tresolutionPercent=$3"+"\n"
		strScript+="\trenderEngine=$4"+"\n"
		strScript+="\trenderQuality=$5"+"\n"
		strScript+="\tscene=$6"+"\n"
		strScript+="\trenderoverwrite=$7"+"\n"
		strScript+="\trenderplaceholder=$8"+"\n"
		strScript+="\tpythonfile=$9"+"\n"
		
		strScript+="\tstrscene=\"\""+"\n"
		strScript+="\tif [ ! -z \"$scene\" -a \"$scene\"!=\"\" ]; then"+"\n"
		strScript+="\t\tstrscene=\"-S \\\"$scene\\\"\""+"\n"
		strScript+="\tfi"+"\n"

		strScript+="\tstrimage=\"\""+"\n"
		strScript+="\tif [ ! -z \"$imagename\" -a \"$imagename\"!=\"\" ]; then"+"\n"
		strScript+="\t\tstrimage=\"-o \\\"$imagename\\\"\""+"\n"
		strScript+="\tfi"+"\n"
		
		strScript+="\tstrpython=\"\""+"\n"
		strScript+="\tif [ ! -z \"$pythonfile\" -a \"$pythonfile\"!=\"\" ]; then"+"\n"
		strScript+="\t\tstrpython=\"-P \\\"$pythonfile\\\"\""+"\n"
		strScript+="\tfi"+"\n"

#		##############write python file
#		strScript+="\tif test -f \"$pyfile\"; then"+"\n"
#		strScript+="\t\techo \"$pyfile exists.\""+"\n"
#		strScript+="\t\trm $pyfile"+"\n"
#		strScript+="\tfi"+"\n"
#		strScript+="\techo \"$pyfile\""+"\n"
#		strScript+="\ttouch $pyfile"+"\n"
#		strScript+="\techo \"import bpy\" >> $pyfile"+"\n"
#		strScript+="\techo \"scn = bpy.context.scene\" >> $pyfile"+"\n"
#		strScript+="\techo \"rnd = scn.render\" >> $pyfile"+"\n"
##		strScript+="\techo \"rnd.filepath='\"$imageName\"'\" >> $pyfile"+"\n"
#		strScript+="\tif (( $resolutionPercent > 0 )); then"+"\n"
#		strScript+="\t\techo \"rnd.resolution_percentage=\"$resolutionPercent >> $pyfile"+"\n"
#		strScript+="\tfi"+"\n"

#		strScript+="\tif [ ! -z \"$renderEngine\" -a \"$renderEngine\"!=\"\" ]; then"+"\n"
#		strScript+="\t\techo \"scn.render.engine='\"$renderEngine\"'\" >> $pyfile"+"\n"
#		strScript+="\tfi"+"\n"

#		strScript+="\tif [ ! -z \"$renderQuality\" -a \"$renderQuality\"!=\"\" ]; then"+"\n"
#		strScript+="\t\techo \"scn.cycles.samples=\"$renderQuality >> $pyfile"+"\n"
#		strScript+="\t\techo \"scn.eevee.taa_render_samples=\"$renderQuality >> $pyfile"+"\n"
#		strScript+="\tfi"+"\n"

#		strScript+="\techo \"\" >> $pyfile"+"\n"
##		strScript+="\techo \"scn.frame_set(\"$curframe\")\" >> $pyfile"+"\n"
##		strScript+="\techo \"scn.frame_current = \"$curframe >> $pyfile"+"\n"
#		strScript+="\techo \"scn.render.use_overwrite=True\" >> $pyfile"+"\n"
##		strScript+="\t#echo \"scn.cycles.samples=\"$cyclesSamples >> $pyfile"+"\n"
##		strScript+="\t#echo \"scn.eevee.taa_render_samples=\"$eeveeSamples >> $pyfile"+"\n"
##		strScript+="\t#echo \"scn.render.engine='\"$renderEngine\"'\" >> $pyfile"+"\n"
##		strScript+="\techo \"if(scn.node_tree!=None):\" >> $pyfile"+"\n"
##		strScript+="\techo \"    for xfo in scn.node_tree.nodes:\" >> $pyfile"+"\n"
##		strScript+="\techo \"        if (xfo.type=='OUTPUT_FILE'):\" >> $pyfile"+"\n"
##		strScript+="\techo \"            tempslotcount=len(xfo.file_slots)\" >> $pyfile"+"\n"
##		strScript+="\techo \"            for xSlot in range(tempslotcount):\" >> $pyfile"+"\n"
##		strScript+="\techo \"                xfo.file_slots[xSlot].path=xfo.file_slots[xSlot].path + '\"$foPath\"' + '_'\" >> $pyfile"+"\n"
#		
#		strScript+="\techo \"\" >> $pyfile"+"\n"
#		######call the active scene when the script was created
##		strScript+="\t$blenderPath -b \"$file\" -x 1 -o \"$imageName\" -S '"+scn.name+"' -P $pyfile -f $curframe"+"\n"
##		strScript+="\t$blenderPath -b \"$file\" -x 1 $strimage $strscene -P \"$pyfile\" -f $curframe"+"\n"
#		strScript+="\tcomm=\"$blenderPath -b \\\"$file\\\" -x 1 $strscene $strimage -P \\\"$pyfile\\\" -f $curframe\""+"\n"
#		strScript+="\teval $comm"+"\n"
#		strScript+="\t#rm \"$pyfile\""+"\n"
#		##########################################
		
		##########################################
		###############python-expr
		strScript+="\tpythonexpr=\"import bpy; scn = bpy.context.scene; rnd = scn.render; \""+"\n"
		strScript+="\tif (( $resolutionPercent > 0 )); then"+"\n"
		strScript+="\t\tpythonexpr=\"${pythonexpr}rnd.resolution_percentage=\"$resolutionPercent\"; \""+"\n"
		strScript+="\tfi"+"\n"
		strScript+="\tif [ ! -z \"$renderEngine\" -a \"$renderEngine\"!=\"\" ]; then"+"\n"
		strScript+="\t\tpythonexpr=\"${pythonexpr}scn.render.engine='\"$renderEngine\"'; \""+"\n"
		strScript+="\tfi"+"\n"
		strScript+="\tif (( $renderQuality > 0 )); then"+"\n"
#		strScript+="\tif [ ! -z \"$renderQuality\" -a \"$renderQuality\"!=\"\" ]; then"+"\n"
		strScript+="\t\tpythonexpr=\"${pythonexpr}scn.cycles.samples=\"$renderQuality\"; \""+"\n"
		strScript+="\t\tpythonexpr=\"${pythonexpr}scn.eevee.taa_render_samples=\"$renderQuality\"; \""+"\n"
		strScript+="\tfi"+"\n"
		
		strScript+="\tif [ ! -z \"$renderoverwrite\" -a \"$renderoverwrite\"!=\"\" ]; then"+"\n"
		strScript+="\t\tpythonexpr=\"${pythonexpr}scn.render.use_overwrite=$renderoverwrite; \""+"\n"
		strScript+="\tfi"+"\n"

		strScript+="\tif [ ! -z \"$renderplaceholder\" -a \"$renderplaceholder\"!=\"\" ]; then"+"\n"
		strScript+="\t\tpythonexpr=\"${pythonexpr}scn.render.use_placeholder=$renderplaceholder; \""+"\n"
		strScript+="\tfi"+"\n"

		strScript+="\tcomm=\"$blenderPath -b \\\"$file\\\" -x 1 $strscene $strimage --python-expr \\\"$pythonexpr\\\" $strpython -f $curframe\""+"\n"
		if rftsettings.rft_comm_pre!="":
			strScript+="\t"+rftsettings.rft_comm_pre+" \"$file\" \"$imagename\""+"\n"
		strScript+="\teval $comm"+"\n"
		if rftsettings.rft_comm_post!="":
			strScript+="\t"+rftsettings.rft_comm_post+" \"$file\" \"$imagename\""+"\n"
		
		strScript+="\tmsg \"$curframe\""+"\n"
		##########################################
		
		strScript+="}"+"\n"
#		strScript+="pythonName=\"render_from_terminal\""+"\n"
#		strScript+="pyfile=$mainPath$pythonName\".py\""+"\n"
		strScript+=""+"\n"
		strScript+="################################"+"\n"
		strScript+=""+"\n"
		strScript+="mainPath=\""+mainPath+"\""+"\n"
		strScript+="file=$mainPath\""+fileName+"\""+"\n"
		strScript+=""+"\n"


		if rftsettings.rft_or_enabled==False:
			strScript+="fileout=\"\""+"\n"
			strScript+="resperc=0"+"\n"
			strScript+="# 0: value from .blend file"+"\n"
			strScript+="rendeng=\"\""+"\n"
			strScript+="## BLENDER_EEVEE_NEXT - BLENDER_WORKBENCH - CYCLES"+"\n"
			strScript+="rendqual=0"+"\n"
			strScript+="#max samples for Cycles and samples for Eevee"+"\n"
			strScript+="scene=\"\""+"\n"
			strScript+="#empty: value from .blend file"+"\n"
			strScript+="overwrite=\"\""+"\n"
			strScript+="#empty: value from .blend file"+"\n"
			strScript+="pythonfile=\""+rftsettings.rft_comm_python+"\""+"\n"
			strScript+="#.py file"+"\n"
			
		else:
			strScript+="fileout=\""+str(rftsettings.rft_or_filename)+"\""+"\n"
			strScript+="resperc="+str(rftsettings.rft_or_percres)+"\n"
			strScript+="# 0: value from .blend file"+"\n"
			if rftsettings.rft_or_renderengine=="DEFAULT":
				strScript+="rendeng=\"\""+"\n"
			else:
				strScript+="rendeng=\""+str(rftsettings.rft_or_renderengine)+"\""+"\n"
			strScript+="## BLENDER_EEVEE_NEXT - BLENDER_WORKBENCH - CYCLES"+"\n"
			strScript+="rendqual="+str(rftsettings.rft_or_renderquality)+"\n"
			strScript+="#max samples for Cycles and samples for Eevee"+"\n"
			strScript+="scene=\""+str(rftsettings.rft_or_scene)+"\""+"\n"
			strScript+="#empty: value from .blend file"+"\n"

			if rftsettings.rft_or_overwrite==False:
				strScript+="overwrite=\"\""+"\n"
			else:
				strScript+="overwrite=\""+str(rftsettings.rft_or_overwritevalue)+"\""+"\n"
			strScript+="#empty: value from .blend file"+"\n"

			if rftsettings.rft_or_placeholder==False:
				strScript+="placeholder=\"\""+"\n"
			else:
				strScript+="placeholder=\""+str(rftsettings.rft_or_placeholdervalue)+"\""+"\n"
			strScript+="#empty: value from .blend file"+"\n"

			strScript+="pythonfile=\""+rftsettings.rft_comm_python+"\""+"\n"
			strScript+="#.py file"+"\n"
		strScript+=""+"\n"
		
#		BLENDER_EEVEE_NEXT
#		BLENDER_WORKBENCH
#		CYCLES
		
		allframes=""
		
		if rftsettings.rft_animationdefault==True and rftsettings.rft_onlycurrent==False:
			strScript+="datarender=$(date +\"%Y%m%d_%H-%M\") "+"\n"
			allframes=str(scn.frame_start)+".."+str(scn.frame_end)
			if rftsettings.rft_comm_start!="":
				strScript+=rftsettings.rft_comm_start+"\n"
			if rftsettings.rft_or_enabled==False:
				strScript+="$blenderPath -b \"$file\" -a"+"\n"
				strScript+="#startrender "
				strScript+="\"$fileout\" " 
				strScript+="\""+allframes+"\" " 
				strScript+="\"$resperc\" "
				strScript+="\"$rendeng\" " 
				strScript+="\"$rendqual\" " 
				strScript+="\"$scene\" " 
				strScript+="\"$overwrite\" " 
				strScript+="\"$placeholder\" " 
				strScript+="\"$pythonfile\" " 
				strScript+=""+"\n"
			else:
				strScript+="#$blenderPath -b \"$file\" -a"+"\n"
				strScript+="startrender "
				strScript+="\"$fileout\" " 
				strScript+="\""+allframes+"\" " 
				strScript+="\"$resperc\" "
				strScript+="\"$rendeng\" " 
				strScript+="\"$rendqual\" " 
				strScript+="\"$scene\" " 
				strScript+="\"$overwrite\" " 
				strScript+="\"$placeholder\" " 
				strScript+="\"$pythonfile\" " 
				strScript+=""+"\n"
			if rftsettings.rft_comm_end!="":
				strScript+=rftsettings.rft_comm_end+"\n"
		else:
			if rftsettings.rft_newinstance==False:
				for i in arframes:
					allframes+=i+","
				if allframes.endswith(","):
					allframes = allframes[:-1]
#				print(allframes)
				if rftsettings.rft_comm_start!="":
					strScript+=rftsettings.rft_comm_start+"\n"
				strScript+="datarender=$(date +\"%Y%m%d_%H-%M\") "+"\n"
				strScript+="startrender "
				strScript+="\"$fileout\" " 
				strScript+="\""+allframes+"\" " 
				strScript+="\"$resperc\" "
				strScript+="\"$rendeng\" " 
				strScript+="\"$rendqual\" " 
				strScript+="\"$scene\" " 
				strScript+="\"$overwrite\" " 
				strScript+="\"$pythonfile\" " 
				strScript+=""+"\n"
				if rftsettings.rft_comm_end!="":
					strScript+=rftsettings.rft_comm_end+"\n"

			else:
				if rftsettings.rft_comm_start!="":
					strScript+=rftsettings.rft_comm_start+"\n"
				for i in arframes:
					strScript+="datarender=$(date +\"%Y%m%d_%H-%M\") "+"\n"
					strScript+="startrender "
					strScript+="\"$fileout\" " 
					strScript+="\""+i+"\" " 
					strScript+="\"$resperc\" "
					strScript+="\"$rendeng\" " 
					strScript+="\"$rendqual\" " 
					strScript+="\"$scene\" " 
					strScript+="\"$overwrite\" " 
					strScript+="\"$pythonfile\" " 
					strScript+=""+"\n"
				if rftsettings.rft_comm_end!="":
					strScript+=rftsettings.rft_comm_end+"\n"

		strScript+="\n"
		strScript+="msg \"end\"\n"
		strScript+="echo \"done\"\n"
		strScript+="\n"
		return strScript
'''
-b or --background - Run in background (often used for UI-less rendering).
-a or --render-anim - Render frames from start to end (inclusive).
-S or --scene <name>
-f or --render-frame <frame>
	Render frame <frame> and save it.
	* +<frame> start frame relative, -<frame> end frame relative.
	* A comma separated list of frames can also be used (no spaces).
	* A range of frames can be expressed using '..' separator between the first and last frames (inclusive).
-s or --frame-start <frame>
-e or --frame-end <frame>
-j or --frame-jump <frames>
-o or --render-output <path>
-E or --engine <engine>
-t or --threads <threads>
Cycles Render Options:
--cycles-device <device>
	Valid options are: 'CPU' 'CUDA' 'OPTIX' 'HIP' 'ONEAPI' 'METAL'.
	Append +CPU to a GPU device to render on both CPU and GPU.
Format Options:
-F or --render-format <format>
	'TGA' 'RAWTGA' 'JPEG' 'IRIS' 'AVIRAW' 'AVIJPEG' 'PNG' 'BMP' 'HDR' 'TIFF'.
	Formats that can be compiled into Blender, not available on all systems:
	'OPEN_EXR' 'OPEN_EXR_MULTILAYER' 'FFMPEG' 'CINEON' 'DPX' 'JP2' 'WEBP'.
-x or --use-extension <bool>
Python Options:
-y or --enable-autoexec 
-Y or --disable-autoexec 
-P or --python <filepath>
--python-text <name>
	Run the given Python script text block.
--python-expr <expression>
	Run the given expression as a Python script.
--python-exit-code <code>
	Set the exit-code in [0..255] to exit if a Python exception is raised
	(only for scripts executed from the command line), zero disables.

'''
class RFT_PT_panel(bpy.types.Panel):
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "output"
	
	bl_label = "Render from terminal"
	
	def draw_header(self, context):
		layout = self.layout
		layout.label(text="", icon="CONSOLE")

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		rftsettings = scene.rftsettings

		box = layout.box()
		row = box.row()
		row.label(text="Frames to render")
		row = box.row()
		row.prop(rftsettings, "rft_onlycurrent")
		row = box.row()
		row.prop(rftsettings, "rft_animationdefault")
		row.active=rftsettings.rft_onlycurrent==False
		row.enabled=rftsettings.rft_onlycurrent==False
		row = box.row()
		row.prop(rftsettings, "rft_frametorender")
		row.active=rftsettings.rft_onlycurrent==False and rftsettings.rft_animationdefault==False
		row.enabled=rftsettings.rft_onlycurrent==False and rftsettings.rft_animationdefault==False
		row = box.row()
		row.prop(rftsettings, "rft_animasstillseq")
		row.prop(rftsettings, "rft_newinstance")
		row.active=rftsettings.rft_onlycurrent==False and rftsettings.rft_animationdefault==False
		row.enabled=rftsettings.rft_onlycurrent==False and rftsettings.rft_animationdefault==False

		box = layout.box()
		row = box.row()
		row.label(text="Additional commands")
		row = box.row()
		row.prop(rftsettings, "rft_comm_start")
		row = box.row()
		row.prop(rftsettings, "rft_comm_pre")
		row = box.row()
		row.prop(rftsettings, "rft_comm_python")
		row = box.row()
		row.prop(rftsettings, "rft_comm_post")
		row = box.row()
		row.prop(rftsettings, "rft_comm_end")
	
		box = layout.box()
		row = box.row()
		row.label(text="Override values")
#		row = box.row()
		row.prop(rftsettings, "rft_or_enabled")
		row = box.row()
		row.prop(rftsettings, "rft_or_filename")
		row.active=rftsettings.rft_or_enabled==True
		row.enabled=rftsettings.rft_or_enabled==True
		
		row = box.row()
		split = row.split(factor=0.5)
		col_1 = split.column(align=True)
		col_2 = split.column(align=True)
		row1 = col_1.row()
		row2 = col_2.row()
		row1.prop(rftsettings, "rft_or_overwrite")
		row2.prop(rftsettings, "rft_or_overwritevalue")
		row2.active=rftsettings.rft_or_overwrite==True
		row2.enabled=rftsettings.rft_or_overwrite==True
		row.active=rftsettings.rft_or_enabled==True
		row.enabled=rftsettings.rft_or_enabled==True
		row = box.row()
		split = row.split(factor=0.5)
		col_1 = split.column(align=True)
		col_2 = split.column(align=True)
		row1 = col_1.row()
		row2 = col_2.row()
		row1.prop(rftsettings, "rft_or_placeholder")
		row2.prop(rftsettings, "rft_or_placeholdervalue")
		row2.active=rftsettings.rft_or_placeholder==True
		row2.enabled=rftsettings.rft_or_placeholder==True
		row.active=rftsettings.rft_or_enabled==True
		row.enabled=rftsettings.rft_or_enabled==True
		row = box.row()
		row.prop(rftsettings, "rft_or_renderengine", expand=False)
		row.active=rftsettings.rft_or_enabled==True
		row.enabled=rftsettings.rft_or_enabled==True
		row = box.row()
		split = row.split(factor=0.5)
		col_1 = split.column(align=True)
		col_2 = split.column(align=True)
		row1 = col_1.row()
		row2 = col_2.row()
		row1.prop(rftsettings, "rft_or_renderquality")
		row2.prop(rftsettings, "rft_or_percres")
		row.active=rftsettings.rft_or_enabled==True
		row.enabled=rftsettings.rft_or_enabled==True
		row = box.row()
		row.prop(rftsettings, "rft_or_scene")
		row.active=rftsettings.rft_or_enabled==True
		row.enabled=rftsettings.rft_or_enabled==True


		box = layout.box()
		row = box.row()
		row.label(text="Write script")
		row = box.row()
		row.prop(rftsettings, "rft_writeSH")
		row.prop(rftsettings, "rft_writeBAT")
		row = box.row()
		row.operator("render.writescript", icon="VIEW_CAMERA")
		row.active=rftsettings.rft_writeSH==True or rftsettings.rft_writeBAT==True
		row.enabled=rftsettings.rft_writeSH==True or rftsettings.rft_writeBAT==True

#		box = layout.box()
#		row = box.row()
#		row.label(text="Fix framing method")
#		row = box.row()
#		row.prop(rftsettings, "rft_fixedframing", expand=True)
#		row = box.row()
#		split = row.split(factor=0.6)
#		col_1 = split.column(align=True)
#		col_2 = split.column(align=True)
#		row1 = col_1.row()
#		row2 = col_2.row()
#		row1.prop(rftsettings, "rft_doforobj", expand=True)
#		row1.active=rftsettings.rft_fixedframing=="POS"
#		row1.enabled=rftsettings.rft_fixedframing=="POS"
#		row2.prop_search(rftsettings, "rft_targetOb", scene, "objects", text="Pick Object")
#		row2.active=rftsettings.rft_doforobj=="OBJ" and row1.active
#		row2.enabled=rftsettings.rft_doforobj=="OBJ" and row1.enabled
#		box.active=rftsettings.rft_fixingactive==False
#		box.enabled=rftsettings.rft_fixingactive==False
#		
#		box = layout.box()
#		row = box.row()
#		row.prop(rftsettings, "rft_onlyactivecamera")
#		row = box.row()
#		row.prop(rftsettings, "rft_ifsmallershrink")
#		box.active=rftsettings.rft_fixingactive==False
#		box.enabled=rftsettings.rft_fixingactive==False
#		row = box.row()
#		row.operator("rft.restoreoldres", icon="LOOP_BACK")
#		row.active=rftsettings.rft_fixingactive==False and rftsettings.rft_restoreposs==True
#		row.enabled=rftsettings.rft_fixingactive==False and rftsettings.rft_restoreposs==True
#		
#		box = layout.box()
#		row = box.row()
#		row.label(text="Add margin to render resolution")
#		row = box.row()
#		row.prop(rftsettings, "rft_pixeltoX")
#		row.prop(rftsettings, "rft_pixeltoY")
#		row = box.row()
#		row.operator("rft.addmargins", icon="CON_OBJECTSOLVER")
#		box.active=rftsettings.rft_fixingactive==False
#		box.enabled=rftsettings.rft_fixingactive==False
#		split = row.split(factor=0.5)
#		col_1 = split.column(align=True)
#		col_2 = split.column(align=True)
#		row1 = col_1.row()
#		row2 = col_2.row()
#		row1.operator("rft.startfixing", icon="VIEW_CAMERA")
#		row2.operator("rft.stopfix", icon="EVENT_MEDIASTOP")
#		row1.active=rftsettings.rft_fixingactive==False
#		row1.enabled=rftsettings.rft_fixingactive==False
#		row2.active=rftsettings.rft_fixingactive==True
#		row2.enabled=rftsettings.rft_fixingactive==True
		
		
		
classes = [
	RFT_OT_writescript,
	RFT_PT_panel,
	RFT_Settings,
]

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
	
	bpy.types.Scene.rftsettings = PointerProperty(type=RFT_Settings)

def unregister():
	from bpy.utils import unregister_class
	for cls in classes:
		unregister_class(cls)
	del bpy.types.Scene.rftsettings

if __name__ == "__main__":
	register()


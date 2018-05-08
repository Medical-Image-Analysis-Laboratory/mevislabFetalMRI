# ----------------------------------------------------------------------------

# 
#  \file    ImageOrientationInterface.py
#  \author  FetalMRI
#  \date    2018-01-16
#
#  

# ----------------------------------------------------------------------------

from mevis import *
from mevis import MLAB, MLABFileManager, MLABFileDialog
from PythonQt import QtGui
import numpy
import math
import os

activePositioning = None
activeMasking = None
currentPositioning = None
currentImage = None
g_layoutImageOrientation = None 
g_sceneImageOrientation = None 
g_ImageOrientationGraphicsView = None
g_HorizontalControl = {}
activeShowPosition = 1
ctx.field("Switch.currentInput").setValue(0)
ctx.field("SoInteractionMapping1.ignoreOtherCommandActions").setBoolValue(False)


def setSceneBackgroundColor(scene):
  scene.setBackgroundBrush(QtGui.QColor(0,0,0,255))

def initImageOrientationGraphicsView(view):
  global g_ImageOrientationGraphicsView
  g_ImageOrientationGraphicsView = view
  global TempObj
  
  global activePositioning
  activePositioning = False
  global activeMasking
  activeMasking = False
  ctx.field("itkImageFileReader1.unresolvedFileName").setStringValue("")
  ctx.field("AlreadyModifiedMaskReader.unresolvedFileName").setStringValue("")
  ctx.field("AlreadyModifiedMaskReader.fileName").setStringValue("")
  ctx.field("itkImageFileReader1.fileName").setStringValue("")
  ctx.field("itkImageFileReader1.close").touch()
  ctx.field("AlreadyModifiedMaskReader.close").touch()
  ctx.field("SwitchAlreadyRegistered.currentInput").setValue(0)
  ctx.field("AlreadyModifiedMask.currentInput").setValue(0)
  ctx.field("Switch.currentInput").setValue(0)
  ctx.field("GetAtlasMacro.itkImageFileReader.open").touch()
  ctx.field("GetAtlasMacro.itkImageFileReaderMask.open").touch()
  ctx.field("ToggleBrainMask.on").setValue(False)
  ctx.field("SwitchAlreadyRegistered.currentInput").setValue(0)
  ctx.field("AlreadyModifiedMask.currentInput").setValue(0)
  ctx.field("adaptTemplateMask.SoToggleMaskEditor.on").setBoolValue(False)
  showImageOrientationInterface()
  resetZoom()
  TempObj=temporaryObject()
  
def showImageOrientationInterface():
  
  global g_layoutImageOrientation
  global g_sceneImageOrientation
  global g_ImageOrientationGraphicsView
  global g_HorizontalControl
  
  g_HorizontalControl = {}
  g_sceneImageOrientation = g_ImageOrientationGraphicsView.scene()
  g_sceneImageOrientation.clear()
  #setSceneBackgroundColor(g_sceneImageOrientation)
  #layer = g_sceneImageOrientation.addLayer()

  #g_layoutImageOrientation = g_sceneImageOrientation.createVerticalLayout(layer)
  
  #MainMDL = g_sceneImageOrientation.addMDL("Panel { module=parent:ImageOrientationInterface window=ImageOrientationPanel }")
  #ctx.control("GraphicsView" ).setProperty("expandX",False)
  mdlToSet = ""
  numIm = ctx.field("NumberImages").value
  print("number of images: %s")
  for i in range(numIm):
    buttonDefinition = """Button {expandX = No title = \"Image %i\" name = buttonImage%i command = "py: updateImage(\'Image%i\')"}"""%(i,i,i)
    #buttonImage = g_sceneImageOrientation.addMDL(buttonDefinition, True)
    buttonPositioningDef = """Button {expandX = No title = "Set IH T B A P positons" name = buttonPositioning%i command = "py: setPositioning(\'Image%i\')"}"""%(i,i)
    #buttonPositioning = g_sceneImageOrientation.addMDL(buttonPositioningDef, True)
    buttonResetBrainMaskDef = """Button {expandX = No title ="Reset Brain Mask" name = buttonResetBrainMask%i enabled = False command = "py: resetBrainMask(\'Image%i\')"}"""%(i,i)
    #buttonManualPositioning = g_sceneImageOrientation.addMDL(buttonManualPositioningDef, True)
    buttonGenerateMaskDef = """Button {expandX = No title = "Edit Brain Mask" name = GenerateBrainMask%i enabled = False command = "py: generateBrainMask(\'Image%i\')"}"""%(i,i)
    #buttonGenerateMask = g_sceneImageOrientation.addMDL(buttonGenerateMaskDef, True)
    checkBoxDefinition = "CheckBox {name = checkImage%i}"%(i)
    #checkBoxImage = g_sceneImageOrientation.addMDL(checkBoxDefinition,True)
    comboboxDefinition = """ComboBox {expandX = No name = \"comboImage%i\" items {item = unknown item = axial item = sagittal item = coronal} textChangedCommand = "py: registerplaneOrientation(\'Image%i\')"}"""%(i,i)
    
    #mdlToSet +="""Horizontal { name = \"horizontal%i\"  "+ buttonDefinition + buttonPositioningDef + buttonManualPositioningDef + buttonGenerateMaskDef + comboboxDefinition + checkBoxDefinition " Execute = "py: getHorizontalControl(\'horizontal%i\')" } """%(i,i)
    mdlToSet +="""Horizontal { name = \"horizontal%i\"  """%i + buttonDefinition + buttonPositioningDef + buttonGenerateMaskDef + buttonResetBrainMaskDef+ comboboxDefinition + checkBoxDefinition + """ Execute = "py: getHorizontalControl(\'Image%i\',\'horizontal%i\')" } """%(i,i)
    #mdlPanel = g_sceneImageOrientation.addMDL(mdlToSet)
    #g_layoutImageOrientation.addItem(mdlPanel)
    #comboboxImage = g_sceneImageOrientation.addMDL(comboboxDefinition,True)
    #comboboxImage.setProperty("expandX",False)
    #buttonPositioning.setProperty("expandX",False)
    #buttonImage.setProperty("expandX",False)
    #comboboxImage.setProperty("expandY",True)
    #g_layoutImageOrientation.addItem(buttonImage,i,0)
    #g_layoutImageOrientation.addItem(buttonPositioning,i,1)
    #g_layoutImageOrientation.addItem(buttonManualPositioning,i,2)
    #g_layoutImageOrientation.addItem(comboboxImage,i,3)
    #g_layoutImageOrientation.addItem(buttonGenerateMask,i,4)
    #g_layoutImageOrientation.addItem(checkBoxImage,i,5)
  
  buttonResetIm = """Button {expandX = No title = "Reset Images" name = buttonResetImage command = "py: resetImages()"}"""
  
  mdlToSet += buttonResetIm
  g_sceneImageOrientation.addMDL("Vertical {" + mdlToSet + "}")
  
  updateComboBox()
  
def updateComboBox():
    
  global g_HorizontalControl
  try:
    inImages = ctx.field("inImageInfos").object()
    if inImages is not None:
      print("set orientation plane")
      dictItem = {"unknown":0,"axial":1,"sagittal":2,"coronal":3}
      for imiter in inImages.keys():
        if 'file' in inImages[imiter].keys():
          if ctx.hasControl("button%s"%imiter):
            try:
              ctx.control("button%s"%imiter).setStyleSheetFromString('QPushButton { background-color: "blue"; }')
            except:
              print("test background has control didn't work")
          else:
            try:
              g_HorizontalControl[imiter].control("button%s"%imiter).setStyleSheetFromString('QPushButton { background-color: "blue"; }')
            except:
              print("test background g_horizontalcontrol didn't work")
        
        if 'planeOrientation' in inImages[imiter].keys():
            if ctx.hasControl("combo%s"%imiter):
             try:
               ctx.control("combo%s"%imiter).setCurrentItem(dictItem[inImages[imiter]['planeOrientation']])
             except:
               ctx.control("combo%s"%imiter).setCurrentItem(0)
            else:
              #valIm = imiter.split('Image')[-1]
              try:
                g_HorizontalControl[imiter].control("comboImage%s"%valIm).setCurrentItem(dictItem[inImages[imiter]['planeOrientation']])
              except:
                g_HorizontalControl[imiter].control("comboImage%s"%valIm).setCurrentItem(0)
                
        if 'mask' in inImages[imiter].keys():
          valIm = imiter.split('Image')[-1]
          if ctx.hasControl("GenerateBrainMask%s"%valIm):
            try:
              ctx.control("GenerateBrainMask%s"%valIm).setStyleSheetFromString('QPushButton { background-color: "blue"; }')
              ctx.control("buttonResetBrainMask%s"%valIm).setEnabled(True)
            except:
              print("test background has control didn't work")
          else:
            try:
              g_HorizontalControl[imiter].control("GenerateBrainMask%s"%valIm).setStyleSheetFromString('QPushButton { background-color: "blue"; }')
              g_HorizontalControl[imiter].control("buttonResetBrainMask%s"%valIm).setEnabled(True)
            except:
              print("test background g_horizontalcontrol didn't work")
         
        if "WorldChanged" in inImages[imiter].keys():
          valIm = imiter.split('Image')[-1]
          if ctx.hasControl("GenerateBrainMask%s"%valIm):
            try:
              ctx.control("GenerateBrainMask%s"%valIm).setEnabled(True)
            except:
              print("don't know")
          else:
            try:
              g_HorizontalControl[imiter].control("GenerateBrainMask%s"%valIm).setEnabled(True)
            except:
              print("don't know")
                
            
  except:
    pass
 
  #g_layoutImageOrientation.addItem(buttonResetIm)
  #g_layoutImageOrientation.addItem(MainMDL,0,4)

def getAtlasManually():
  
  exp = ctx.expandFilename(ctx.field("AtlasImage").stringValue())
  filename = MLABFileDialog.getOpenFileName(exp, "", "Open file")
  
  ctx.field("GetAtlasMacro.itkImageFileReader.fileName").setStringValue(filename)

def resetImages():

  ctx.field("itkImageFileReader.fileName").setStringValue("")
  resetZoom()
  ctx.field("Switch.currentInput").setValue(0)
  ctx.field("AlreadyModifiedMask.currentInput").setValue(0)
  ctx.field("SwitchAlreadyRegistered.currentInput").setValue(0)
  
  global g_HorizontalControl  
  
  for iterIm in range(ctx.field("NumberImages").value):
    print("reset combo box")
    if ctx.hasControl("comboImage%i"%iterIm):
      ctx.control("comboImage%i"%iterIm).setCurrentItem(0)
    else:
      print("why not .....")

  inImages = None
  ctx.field("inImageInfos").setObject(inImages)
  print("images reseted")
  
  for iterbutton in range(ctx.field("NumberImages").value):
    if ctx.hasControl("buttonImage%i"%iterbutton):
      try:
        ctx.control("buttonImage%i"%iterbutton).setStyleSheetFromString('QPushButton { background-color: "white"; }')
      except:
        print("test background has control didn't work")
    else:
      try:
        g_HorizontalControl["Image%i"%iterbutton].control("buttonImage%i"%iterbutton).setStyleSheetFromString('QPushButton { background-color: "white"; }')
      except:
        print("test background g_horizontalcontrol didn't work")

    if ctx.hasControl("GenerateBrainMask%s"%iterbutton):
      try:
        ctx.control("GenerateBrainMask%s"%iterbutton).setStyleSheetFromString('QPushButton { background-color: "white"; }')
      except:
        print("test background has control didn't work")
    else:
      try:
        g_HorizontalControl[imiter].control("GenerateBrainMask%s"%iterbutton).setStyleSheetFromString('QPushButton { background-color: "white"; }')
      except:
        print("test background g_horizontalcontrol didn't work")            

def updateImage(Image="Image0"):
  
  #first backup current cso if there is one
  global TempObj
  global currentImage
  if currentImage !=  None:
    TempObj.getTempCSOs()
  
  currentImage = Image
  global activePositioning
  activePositioning = False
  inImages = ctx.field("inImageInfos").object()
  print("New Image : %s"%Image)
  try:
    filename = inImages[Image]["file"]
  except:
    print("inImages must be a dictionnary with 'Image0' etc as keys and inImage['Image0'] must be a dictionnary with at least 'file' as key")
    print("select manually a file for debug")
    if inImages == None:
      exp = ctx.expandFilename(ctx.field("AtlasImage").stringValue())
    else:
      exp = os.path.dirname(inImages[inImages.keys()[0]]['file'])
    filename = MLABFileDialog.getOpenFileName(exp, "", "Open file")
    if filename == "":
      print("no file selected")
      return
    if inImages != None:
      inImages.update({Image:{"file":filename}})
    else:
      inImages={Image:{"file":filename}}
    #return
  
  ctx.field("itkImageFileReader.fileName").setStringValue(filename)
  ctx.field("inImageInfos").setObject(inImages)
  
  if ctx.hasControl("button%s"%Image):
    try:
      ctx.control("button%s"%Image).setStyleSheetFromString('QPushButton { background-color: "blue"; }')
    except:
      print("test background has control didn't work")
  else:
    global g_HorizontalControl
    try:
      g_HorizontalControl[Image].control("button%s"%Image).setStyleSheetFromString('QPushButton { background-color: "blue"; }')
    except:
      print("test background g_horizontalcontrol didn't work")
  
  #la il faut aussi gerer les labels anatomics qu'on affiche
  if "Positioning" in inImages[Image].keys():
    if "A" in inImages[Image]["Positioning"].keys():
      ctx.field("LabelA.worldPosition").setValue(inImages[Image]["Positioning"]["A"])
      ctx.field("LabelA.drawingOn").setValue(True)
    else:
      ctx.field("LabelA.drawingOn").setValue(False)
    
    if "P" in inImages[Image]["Positioning"].keys():
      ctx.field("LabelP.worldPosition").setValue(inImages[Image]["Positioning"]["P"])
      ctx.field("LabelP.drawingOn").setValue(True)
    else:
      ctx.field("LabelP.drawingOn").setValue(False)
    
    if "IH" in inImages[Image]["Positioning"].keys():
      ctx.field("LabelIH.worldPosition").setValue(inImages[Image]["Positioning"]["IH"])
      ctx.field("LabelIH.drawingOn").setValue(True)
    else:
      ctx.field("LabelIH.drawingOn").setValue(False)
    
    if "T" in inImages[Image]["Positioning"].keys():
      ctx.field("LabelT.worldPosition").setValue(inImages[Image]["Positioning"]["T"])
      ctx.field("LabelT.drawingOn").setValue(True)
    else:
      ctx.field("LabelT.drawingOn").setValue(False)
    
    if "B" in inImages[Image]["Positioning"].keys():
      ctx.field("LabelB.worldPosition").setValue(inImages[Image]["Positioning"]["B"])
      ctx.field("LabelB.drawingOn").setValue(True)
    else:
      ctx.field("LabelB.drawingOn").setValue(False)
  else:
    ctx.field("LabelIH.drawingOn").setValue(False)
    ctx.field("LabelA.drawingOn").setValue(False)
    ctx.field("LabelP.drawingOn").setValue(False)
    ctx.field("LabelT.drawingOn").setValue(False)
    ctx.field("LabelB.drawingOn").setValue(False)
    ctx.field("ToggleBrainMask.on").setBoolValue(False)
    print("No label to show")  
  
  
  if "WorldChanged" in inImages[Image].keys():
      ctx.field("itkImageFileReader1.unresolvedFileName").setValue(inImages[Image]["WorldChanged"])
      ctx.field("SwitchAlreadyRegistered.currentInput").setValue(1)
  else:
      ctx.field("SwitchAlreadyRegistered.currentInput").setValue(0)
      ctx.field("Switch.currentInput").setValue(0)
    
    #here I do, if all positioning are present I toggle the brain cso but it means that I reload the transfo in setworldmatrix and transformworldmatrix 
  if "WorldChanged" in inImages[Image].keys() and "planeOrientation" in inImages[Image].keys():
      if inImages[Image]["planeOrientation"] == 'axial':
        ctx.field("OrthoSwapFlip.view").setValue("Transversal")
      elif inImages[Image]["planeOrientation"] == 'coronal':
        ctx.field("OrthoSwapFlip.view").setValue("Coronal")
      elif inImages[Image]["planeOrientation"] == 'sagittal':
        ctx.field("OrthoSwapFlip.view").setValue("Sagittal")
      else:
        print("orientation unknown")
      ctx.field("Switch.currentInput").setValue(1)  
      #ctx.field("adaptTemplateMask.updateCSOButton").touch()
      ctx.field("ToggleBrainMask.on").setBoolValue(True)
  else:
      if "WorldChanged" in inImages[Image].keys():
        ctx.field("ToggleBrainMask.on").setBoolValue(True)
        ctx.field("Switch.currentInput").setValue(1)
      else:  
        ctx.field("ToggleBrainMask.on").setBoolValue(False)
        ctx.field("Switch.currentInput").setValue(0)
        print("Switch set to 0")
        
  if "mask" in inImages[Image].keys():
     ctx.field("AlreadyModifiedMaskReader.fileName").setStringValue(inImages[Image]["mask"])
     ctx.field("AlreadyModifiedMask.currentInput").setValue(1)
     ctx.field("adaptTemplateMask.updateCSOButton").touch()
     
  else:
     ctx.field("AlreadyModifiedMask.currentInput").setValue(0)
     ctx.field("adaptTemplateMask.updateCSOButton").touch()
     
  if "planeOrientation" in inImages[Image].keys():
    dictItem = {"unknown":0,"axial":1,"sagittal":2,"coronal":3}
    if ctx.hasControl("combo%s"%Image):
      if inImages[Image]["planeOrientation"] != ctx.control("combo%s"%Image).currentText():
        ctx.control("combo%s"%Image).setCurrentItem(dictItem[inImages[Image]['planeOrientation']])
    else:
      print("why the f... this combo doesn't have any control")

  ctx.field("SoInteractionMapping1.ignoreOtherCommandActions").setBoolValue(False)
  ctx.field("adaptTemplateMask.SoToggleMaskEditor.on").setBoolValue(False)
  ctx.field("LabelViewerMode.text").setStringValue("Viewer Mode")
  
  if ctx.hasControl("button%s"%Image):
    print("has control")
  else:
      print("doesn't have control")
  print("label updated")
  
def setPositioning(Image="Image0"):
  
  updateImage(Image)
  ctx.field("SwitchAlreadyRegistered.currentInput").setValue(0)
  ctx.field("ToggleBrainMask.on").setBoolValue(False)
  ctx.field("Switch.currentInput").setValue(0)
  print("New Image : %s"%Image)
  
  #faire une message box, click IH puis T puis B puis A puis P ? ou faire message box, click IH, puis message box, click T etc ...
  ctx.field("MessageBoxImOrient.message").setStringValue("click anywhere on the Inter Hemisphere Plan")
  
  #ctx.module("MessageBoxImOrient").showWindow("dialog")
  global activePositioning
  activePositioning = True
  global currentPositioning
  currentPositioning = Image
  #ctx.field("View2DExtensions.annotation.wantsKeyEvents").setBoolValue(False)
  ctx.field("View2DExtensions.annotation.editingOn").setBoolValue(False)
  ctx.field("SoView2D.useManagedInteraction").setBoolValue(True)
  ctx.field("eventChoice").setValue(1)
  ctx.field("LabelViewerMode.text").setStringValue("Set Positioning Mode")
  #while tuppleWorldPosition == None:
  #    tuppleWorldPosition = button1PressedImOrient() #ctx.field("SyngoViaView2DOverlay.annoReadPix.worldPosition").value
  #ctx.showModalDialog("ViewerOnly")
  #print("modal")
  #button1PressedImOrient()
  #print(tuppleWorldPosition)

  
def registerplaneOrientation(Image="Image0"):
  
  if not ctx.hasControl("combo%s"%Image):
    return
  
  inImages = ctx.field("inImageInfos").object()
  
  try:
    if inImages == None:
      inImages={Image:{"planeOrientation":ctx.control("combo%s"%Image).currentText()}}
    
    else:
      if Image in inImages.keys():
        inImages[Image].update({"planeOrientation":ctx.control("combo%s"%Image).currentText()})
      else:
        inImages.update({Image:{"planeOrientation":ctx.control("combo%s"%Image).currentText()}})

  except:
    pass
  
  #a actualiser seulement si Image == currentImage
  global currentImage
  if currentImage != None:
    if currentImage == Image:
      if ctx.control("combo%s"%Image).currentText() == 'axial':
        ctx.field("OrthoSwapFlip.view").setValue("Transversal")
      elif ctx.control("combo%s"%Image).currentText() == 'coronal':
        ctx.field("OrthoSwapFlip.view").setValue("Coronal")
      elif ctx.control("combo%s"%Image).currentText() == 'sagittal':
        ctx.field("OrthoSwapFlip.view").setValue("Sagittal")
      else:
        print("orientation unknown")
      
      ctx.field("adaptTemplateMask.updateCSOButton").touch()
      updateImage(Image)
      
    
  ctx.field("inImageInfos").setObject(inImages)

def cornerMenuClicked():
  
  print("user clicked on the conerMenu")
  print(ctx.field("cornerMenuIteraction").value)
  
  if ctx.field("cornerMenuIteraction").value == '3':
    print("switch overlay")
    ctx.field("Switch.currentInput").setValue(1 - ctx.field("Switch.currentInput").value)
    
  if ctx.field("cornerMenuIteraction").value == '2':
    print("add/remove overlay")
    if ctx.field("SoView2DOverlay.alphaFactor").value != 0:
      ctx.field("SoView2DOverlay.alphaFactor").setValue(0)
    else:
      ctx.field("SoView2DOverlay.alphaFactor").setValue(1)
      
  if ctx.field("cornerMenuIteraction").value == '1':
    
    global activeShowPosition
    if activeShowPosition == 1:
      print("show position")
      inImages = ctx.field("inImageInfos").object()
      global currentImage
      if currentImage in inImages.keys():
       if "Positioning" in inImages[currentImage].keys():
        if "A" in inImages[currentImage]["Positioning"].keys():
          ctx.field("LabelA.drawingOn").setValue(True)
        else:
          ctx.field("LabelA.drawingOn").setValue(False)
    
        if "P" in inImages[currentImage]["Positioning"].keys():
          ctx.field("LabelP.drawingOn").setValue(True)
        else:
          ctx.field("LabelP.drawingOn").setValue(False)
    
        if "IH" in inImages[currentImage]["Positioning"].keys():
          ctx.field("LabelIH.drawingOn").setValue(True)
        else:
          ctx.field("LabelIH.drawingOn").setValue(False)
    
        if "T" in inImages[currentImage]["Positioning"].keys():
          ctx.field("LabelT.drawingOn").setValue(True)
        else:
          ctx.field("LabelT.drawingOn").setValue(False)
    
        if "B" in inImages[currentImage]["Positioning"].keys():
          ctx.field("LabelB.drawingOn").setValue(True)
        else:
          ctx.field("LabelB.drawingOn").setValue(False)
      
       else:
        ctx.field("LabelIH.drawingOn").setValue(False)
        ctx.field("LabelA.drawingOn").setValue(False)
        ctx.field("LabelP.drawingOn").setValue(False)
        ctx.field("LabelT.drawingOn").setValue(False)
        ctx.field("LabelB.drawingOn").setValue(False)
      else:  
       ctx.field("LabelIH.drawingOn").setValue(False)
       ctx.field("LabelA.drawingOn").setValue(False)
       ctx.field("LabelP.drawingOn").setValue(False)
       ctx.field("LabelT.drawingOn").setValue(False)
       ctx.field("LabelB.drawingOn").setValue(False)        
    elif activePositioning == 0:
      print("unshow position")
      ctx.field("LabelIH.drawingOn").setValue(False)
      ctx.field("LabelA.drawingOn").setValue(False)
      ctx.field("LabelP.drawingOn").setValue(False)
      ctx.field("LabelT.drawingOn").setValue(False)
      ctx.field("LabelB.drawingOn").setValue(False)
      
    activeShowPosition = 1 - activeShowPosition  
      
  
def button1PressedImOrient(event):
  
  global activeShowPosition
  global activePositioning
  #print activeShowPosition
  if activeShowPosition == 0:
    ctx.field("cornerMenuIteraction").setValue(1)
  
  inImages = ctx.field("inImageInfos").object() 

  #print("eventChoice button1PressedImOrient")
  #print(ctx.field("eventChoice").value)
  if activePositioning == True:
    if event["type"] == "MouseButtonPress":
      if event["button"] == "left":
        if ctx.field("View2DExtensions.annoReadPix.outputValue").value == 0:
          print("not within the brain")
          return
        
        #print("ecriture label")
        position = ctx.field("View2DExtensions.annoReadPix.worldPosition").value
        #est-ce qu'on check que l'output value est differente de 0 ? ctx.field("SyngoViaView2DOverlay.annoReadPix.outpoutValue").value
        print(position)
        #ctx.field("LabelIH.worldPosition").setValue(position)
      
      #if event["button"] == "right":
      #  print("validate position")
      #  return
    
    elif event["type"] == "KeyPress":    
      print(event["key"])
      if event["key"] == "I":
        positionI = ctx.field("View2DExtensions.annoReadPix.worldPosition").value
        positionIvox = ctx.field("View2DExtensions.annoReadPix.voxelPosition").value
        ctx.field("LabelIH.worldPosition").setValue(positionI)
        if inImages == None:
          inImages={currentPositioning:{"Positioning":{"IH":ctx.field("LabelIH.worldPosition").value,"IHvox":positionIvox}}}
        else:
          if currentPositioning in inImages.keys():
            if "Positioning" in inImages[currentImage].keys():
               inImages[currentPositioning]["Positioning"].update({"IH":ctx.field("LabelIH.worldPosition").value,"IHvox":positionIvox})
            else:
               inImages[currentPositioning].update({"Positioning":{"IH":ctx.field("LabelIH.worldPosition").value,"IHvox":positionIvox}})
          else:
            inImages.update({currentPositioning:{"Positioning":{"IH":ctx.field("LabelIH.worldPosition").value,"IHvox":positionIvox}}})
        ctx.field("LabelIH.drawingOn").setValue(True)
        
      elif event["key"] == "A":
        positionA = ctx.field("View2DExtensions.annoReadPix.worldPosition").value
        positionAvox = ctx.field("View2DExtensions.annoReadPix.voxelPosition").value
        ctx.field("LabelA.worldPosition").setValue(positionA)
        if inImages == None:
          inImages={currentPositioning:{"Positioning":{"A":ctx.field("LabelA.worldPosition").value,"Avox":positionAvox}}}
        else:
          if currentPositioning in inImages.keys():
            if "Positioning" in inImages[currentImage].keys():
               inImages[currentPositioning]["Positioning"].update({"A":ctx.field("LabelA.worldPosition").value,"Avox":positionAvox})
            else:
               inImages[currentPositioning].update({"Positioning":{"A":ctx.field("LabelA.worldPosition").value,"Avox":positionAvox}})
          else:
            inImages.update({currentPositioning:{"Positioning":{"A":ctx.field("LabelA.worldPosition").value,"Avox":positionAvox}}})
        ctx.field("LabelA.drawingOn").setValue(True)
      elif event["key"] == "P":
        positionP = ctx.field("View2DExtensions.annoReadPix.worldPosition").value
        positionPvox = ctx.field("View2DExtensions.annoReadPix.voxelPosition").value
        ctx.field("LabelP.worldPosition").setValue(positionP)
        if inImages == None:
          inImages={currentPositioning:{"Positioning":{"P":ctx.field("LabelP.worldPosition").value,"Pvox":positionPvox}}}
        else:
          if currentPositioning in inImages.keys():
            if "Positioning" in inImages[currentImage].keys():
               inImages[currentPositioning]["Positioning"].update({"P":ctx.field("LabelP.worldPosition").value,"Pvox":positionPvox})
            else:   
              inImages[currentPositioning].update({"Positioning":{"P":ctx.field("LabelP.worldPosition").value,"Pvox":positionPvox}})
          else:
            inImages.update({currentPositioning:{"Positioning":{"P":ctx.field("LabelP.worldPosition").value,"Pvox":positionPvox}}})
        ctx.field("LabelP.drawingOn").setValue(True)  
      elif event["key"] == "T":
        positionT = ctx.field("View2DExtensions.annoReadPix.worldPosition").value
        positionTvox = ctx.field("View2DExtensions.annoReadPix.voxelPosition").value
        ctx.field("LabelT.worldPosition").setValue(positionT)
        if inImages == None:
          inImages={currentPositioning:{"Positioning":{"T":ctx.field("LabelT.worldPosition").value,"Tvox":positionTvox}}}
        else:
          if currentPositioning in inImages.keys():
            if "Positioning" in inImages[currentImage].keys():
               inImages[currentPositioning]["Positioning"].update({"T":ctx.field("LabelT.worldPosition").value,"Tvox":positionTvox})
            else:
              inImages[currentPositioning].update({"Positioning":{"T":ctx.field("LabelT.worldPosition").value,"Tvox":positionTvox}})
          else:
            inImages.update({currentPositioning:{"Positioning":{"T":ctx.field("LabelT.worldPosition").value,"Tvox":positionTvox}}})
        ctx.field("LabelT.drawingOn").setValue(True)    
      elif event["key"] == "B":
        positionB = ctx.field("View2DExtensions.annoReadPix.worldPosition").value
        positionBvox = ctx.field("View2DExtensions.annoReadPix.voxelPosition").value
        ctx.field("LabelB.worldPosition").setValue(positionB)
        if inImages == None:
          inImages={currentPositioning:{"Positioning":{"B":ctx.field("LabelB.worldPosition").value,"Bvox":positionBvox}}}
        else:
          if currentPositioning in inImages.keys():
            if "Positioning" in inImages[currentImage].keys():
              inImages[currentPositioning]["Positioning"].update({"B":ctx.field("LabelB.worldPosition").value,"Bvox":positionBvox})
            else:  
              inImages[currentPositioning].update({"Positioning":{"B":ctx.field("LabelB.worldPosition").value,"Bvox":positionBvox}})
          else:
            inImages.update({currentPositioning:{"Positioning":{"B":ctx.field("LabelB.worldPosition").value,"Bvox":positionBvox}}})
        ctx.field("LabelB.drawingOn").setValue(True)    
      elif event["key"] == "Return":
        print("Enter")
        ctx.field("eventChoice").setValue(0)
        ctx.field("View2DExtensions.annotation.editingOn").setBoolValue(True)
        ctx.field("SoView2D.useManagedInteraction").setBoolValue(False)
        activePositioning = False
        print("anatomic position registered")  
        print("modifying voxel to world transformation matrix")
        if (("IH" in inImages[currentPositioning]["Positioning"].keys()) and ("A" in inImages[currentPositioning]["Positioning"].keys()) and ("P" in inImages[currentPositioning]["Positioning"].keys()) and ("T" in inImages[currentPositioning]["Positioning"].keys()) and ("B" in inImages[currentPositioning]["Positioning"].keys())):
          print("coucou")
          imagetorotate = ctx.field("itkImageFileReader.output0")
          voxelSize = imagetorotate.voxelSize()
        
          #reset of the world matrix which correspond to the mother and not the foetus
          ctx.field("SetWorldMatrix.scale").setValue(voxelSize)
          ctx.field("SetWorldMatrix.translation").setValue([0,0,0])
          ctx.field("SetWorldMatrix.center").setValue([0,0,0])
          ctx.field("SetWorldMatrix.scaleOrientation").setValue([0,0,1,0])
          ctx.field("SetWorldMatrix.rotation").setValue([0,0,0])
          #ctx.field("SetWorldMatrix.rotation").setValue()
          #ca fait quoi si je prend pas en compte la voxel size?
          PA = numpy.subtract(numpy.multiply(inImages[currentPositioning]["Positioning"]["Avox"],voxelSize),numpy.multiply(inImages[currentPositioning]["Positioning"]["Pvox"],voxelSize))
          PA = PA/numpy.linalg.norm(PA)
          orientPA = numpy.cross(PA,numpy.array([0,-1,0]))
          
          #I think I have to recalculate T or B to make the vector orthogonal to PA. I think that's why sometimes I get a resulting image with A and P flipped. because the vector BT make a rotation along the axis.
          BT = numpy.subtract(numpy.multiply(inImages[currentPositioning]["Positioning"]["Bvox"],voxelSize),numpy.multiply(inImages[currentPositioning]["Positioning"]["Tvox"],voxelSize))
          lengthBT = numpy.linalg.norm(BT)
          BT=BT/numpy.linalg.norm(BT)
          vectorOrthoBoth = numpy.cross(PA,BT)
          recalculateBTortho = numpy.cross(vectorOrthoBoth,PA)
          newBvox= inImages[currentPositioning]["Positioning"]["Tvox"]+numpy.multiply(recalculateBTortho*lengthBT,numpy.array([1/voxelSize[0],1/voxelSize[1],1/voxelSize[2]]))
          #orientBT = numpy.cross(BT,numpy.array([0,0,1]))
          
          if numpy.linalg.norm(orientPA) != 0:
            skewMatrixPA = numpy.array(((0,-orientPA[2],orientPA[1]),(orientPA[2],0,-orientPA[0]),(-orientPA[1],orientPA[0],0)))
            #skewMatrixBT = numpy.array(((0,-orientBT[2],orientBT[1]),(orientBT[2],0,-orientBT[0]),(-orientBT[1],orientBT[0],0)))
          
            SquaredPA = numpy.dot(skewMatrixPA,skewMatrixPA)*1/(1+numpy.dot(PA,numpy.array([0,-1,0])))
            #SquaredBT = numpy.dot(skewMatrixBT,skewMatrixBT)*1/(1+numpy.dot(BT,numpy.array([0,1,0])))
          
            #FullRotation = numpy.array(((1,0,0),(0,1,0),(0,0,1))) + skewMatrixAP  + SquaredAP + SquaredBT + skewMatrixBT
            #ca ne marche pas je ne peux pas composer des matrices de rotations comme ca
            #PA
            RotationPA = numpy.array(((1,0,0),(0,1,0),(0,0,1))) + skewMatrixPA  + SquaredPA
            FullRotationPA = numpy.identity(4)
            FullRotationPA[0:3,0:3]=RotationPA
          else:
            FullRotationPA = numpy.identity(4)
          #la le determinant est bien a 1, numpy.linalg.det(FullRotationAP)
          
          #BT
          #RotationBT = numpy.array(((1,0,0),(0,1,0),(0,0,1))) + skewMatrixBT  + SquaredBT
          #FullRotationBT = numpy.identity(4)
          #FullRotationBT[0:3,0:3]=RotationBT          
          
          #FullRotation1[:-1,-1]=-numpy.multiply(numpy.array(inImages[currentPositioning]["Positioning"]['IHvox']),voxelSize)
          Translation = numpy.identity(4)
          Translation[:-1,-1]=-numpy.multiply(numpy.array(inImages[currentPositioning]["Positioning"]['IHvox']),voxelSize)
          RotationPAautour0 = numpy.dot(numpy.dot(numpy.linalg.inv(Translation),FullRotationPA),Translation)
          
          FirstTransformation = numpy.dot(Translation,RotationPAautour0)
          #sens2 = numpy.dot(RotationAPautour0,Translation)
          
          #ca ca marche pas il faut que je recalcul ma nouvelle position de IH ? et B et T aussi en fait.... 
          IHinter=list(inImages[currentPositioning]["Positioning"]['IHvox']) #should I use the voxel size ? but normaly not ...
          IHinter.append(1)
          newIH = numpy.dot(FirstTransformation,numpy.multiply(IHinter,numpy.array([voxelSize[0],voxelSize[1],voxelSize[2],1])))
          print("newIH : %s"%str(newIH))
          Binter=list(newBvox)
          Binter.append(1)
          newB = numpy.dot(FirstTransformation,numpy.multiply(Binter,numpy.array([voxelSize[0],voxelSize[1],voxelSize[2],1])))
          print("newB : %s"%str(newB))
          Tinter=list(inImages[currentPositioning]["Positioning"]['Tvox'])
          Tinter.append(1)          
          newT = numpy.dot(FirstTransformation,numpy.multiply(Tinter,numpy.array([voxelSize[0],voxelSize[1],voxelSize[2],1])))
          print("newT : %s"%str(newT))
          ctx.field("SoView2DLabel.worldPosition").setValue([newB[0],newB[1],newB[2]])
          ctx.field("SoView2DLabel1.worldPosition").setValue([newT[0],newT[1],newT[2]])
          newBT = numpy.subtract(newB[0:3],newT[0:3])
          newBT=newBT/numpy.linalg.norm(newBT)
          print("new BT")
          print(newBT)
          orientBT = numpy.cross(newBT,numpy.array([0,0,-1]))
          if numpy.linalg.norm(orientBT) != 0:
            skewMatrixBT = numpy.array(((0,-orientBT[2],orientBT[1]),(orientBT[2],0,-orientBT[0]),(-orientBT[1],orientBT[0],0)))
            SquaredBT = numpy.dot(skewMatrixBT,skewMatrixBT)*1/(1+numpy.dot(newBT,numpy.array([0,0,-1])))
          
            RotationBT = numpy.array(((1,0,0),(0,1,0),(0,0,1))) + skewMatrixBT  + SquaredBT
            FullRotationBT = numpy.identity(4)
            FullRotationBT[0:3,0:3]=RotationBT
          else:
           FullRotationBT = numpy.identity(4)
           
          print(FullRotationBT)
          
          #getnewIHvoxelPosition
          #ctx.field("getIHvoxel.worldPos").setValue([0,0,0])
          #voxIH=ctx.field("getIHvoxel.voxelPos").value
          #print("voxIH")
          #print(voxIH)
          #newImage =ctx.field("TransformWorldMatrixTransAndAP.output0")
          #newVoxelSize = newImage.voxelSize()
          #make the rotation around voxIH
          #Translation2 = numpy.identity(4)
          #Translation2[:-1,-1]=-numpy.multiply(numpy.array(voxIH),newVoxelSize)
          #RotationBTautour0 = numpy.dot(numpy.dot(numpy.linalg.inv(Translation2),FullRotationBT),Translation2)
          #print(RotationBTautour0)
          #print(newBT)
          #FullTransfo=numpy.dot(FirstTransformation,FullRotationBT)
          #FullTransfoothersens = numpy.dot(FullRotationBT,FirstTransformation)
          #print("FullTransfo")
          #print(FullTransfo)
          ctx.field("TransformWorldMatrixBT.transformation").setValue(FullRotationBT)
          #on fait pareil avec juste AP pour comprendre
          ctx.field("TransformWorldMatrixTransAndAP.transformation").setValue(FirstTransformation)
          
          #ctx.field("TransformWorldMatrix.transformation").setValue(FullTransfo)
          WorldChangedName= inImages[currentImage]['file']
          WorldChangedNameFull=WorldChangedName.replace('.nii','_worldmatrixModified_lr.nii')
          #WorldChangedNameAP=WorldChangedName.replace('.nii','_worldmatrixModifiedAP.nii')
          
          ctx.field("itkImageFileWriterWorldMatrixChanged.fileName").setValue(WorldChangedNameFull)
          ctx.field("itkImageFileWriterWorldMatrixChanged.save").touch()
          #ctx.field("itkImageFileWriterTransAndAP.unresolvedFileName").setValue(WorldChangedNameAP)
          #ctx.field("itkImageFileWriterTransAndAP.save").touch()
          inImages[currentImage].update({"WorldChanged":WorldChangedNameFull})
          
          #to change
          #inImages[currentImage].update({"newWorldMatrix":FullTransfo})
          ctx.field("inImageInfos").setObject(inImages)
          valIm = currentImage.split('Image')[-1]
          if ctx.hasControl("GenerateBrainMask%s"%valIm):
            try:
              ctx.control("GenerateBrainMask%s"%valIm).setEnabled(True)
              ctx.control("buttonResetBrainMask%s"%valIm).setEnabled(True)
            except:
              print("don't know")
          else:
            try:
              g_HorizontalControl[currentImage].control("GenerateBrainMask%s"%valIm).setEnabled(True)
              g_HorizontalControl[currentImage].control("buttonResetBrainMask%s"%valIm).setEnabled(True)
            except:
              print("don't know")
              
          #modify mask
          generateBrainMask(currentImage)

          #voxelworldmatrix = imagetorotate.voxelToWorldMatrix()
        
  elif activePositioning ==False:
    global activeMasking
    #print("activeMaskting")
    #print(activeMasking)
    if activeMasking == True:
      button1PressedMaskRefine(event)
    #else:
      
      #print("j'en veux pas de ton click souris")
    
  
def generateBrainMask(Image="Image0"): 
  updateImage(Image)
  print("Mask Generation %s"%Image)
  ctx.field("View2DExtensions.annotation.editingOn").setBoolValue(False)
  ctx.field("SoView2D.useManagedInteraction").setBoolValue(True)
  ctx.field("eventChoice").setValue(2)
  ctx.field("Switch.currentInput").setValue(1)
  ctx.field("ToggleBrainMask.on").setValue(True)
  print("update CSO")
  global activeMasking
  activeMasking = True
  ctx.field("adaptTemplateMask.updateCSOButton").touch()
  ctx.field("adaptTemplateMask.SoToggleMaskEditor.on").setBoolValue(True)
  ctx.field("SoInteractionMapping1.ignoreOtherCommandActions").setBoolValue(True)
  ctx.field("LabelViewerMode.text").setStringValue("Editing Brain Mask Mode")
  
  #remove blue background
  
  #detection of 2,8 4,6 1,9 on the keypad enter to validate
  
def button1PressedMaskRefine(event):

  global currentImage
  
  inImages = ctx.field("inImageInfos").object()
  if event["type"]== "KeyPress":
    if event["key"] != "Return" or event["key"]!="Enter":
      if 'planeOrientation' not in inImages[currentImage].keys():
        print("need to define a plante orientation first")
        return
  
  
  worldToVoxelMatrix = ctx.field("SwitchAlreadyRegistered.output0").worldToVoxelMatrix()
  csoId2Modify = []
  if event["type"] == "KeyPress":
    if event["key"] != "Return" or event["key"]!="Enter":
    #ctx.field("adaptTemplateMask.updateCSOButton").touch()
      CSOobj = ctx.field("adaptTemplateMask.CSOManager1.outCSOList").object()
      for csobj in CSOobj.getCSOs():
        if csobj.isInPlane:
          if ctx.field("SoView2D.startSlice").value == int(csobj.getVoxelBoundingBox(worldToVoxelMatrix)[5]):
              csoId2Modify.append(str(csobj.id))
      csoId2Modifystr=" ".join(csoId2Modify)
      print(csoId2Modifystr)        
    if event["key"]=="2":   
      #ctx.field("adaptTemplateMask.AffineMatrixComposition.inTranslation").value
      #ctx.field("adaptTemplateMask.AffineMatrixComposition.inTranslation").setValue(numpy.array(ctx.field("adaptTemplateMask.AffineMatrixComposition.inTranslation").value) + numpy.array([0,-1,0,0]))
      #ctx.field("AffineMatrixComposition.update").touch()  
      #which orientation am I ? coronal/sagital 2 is -1 z
      #axial, 2 is -1 y
      if inImages[currentImage]['planeOrientation'] == "coronal" or inImages[currentImage]['planeOrientation'] == "sagittal":
         newMatrix=numpy.array([[1,0,0,0],[0,1,0,0],[0,0,1,-0.5],[0,0,0,1]])
      elif inImages[currentImage]['planeOrientation'] == "axial" :
         newMatrix=numpy.array([[1,0,0,0],[0,1,0,-0.5],[0,0,1,0],[0,0,0,1]])
         
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.csoIdList").setValue(csoId2Modifystr)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.matrix").setValue(newMatrix)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.apply").touch()
    
    elif event["key"]=="8":
      if inImages[currentImage]['planeOrientation'] == "coronal" or inImages[currentImage]['planeOrientation'] == "sagittal":
         newMatrix=numpy.array([[1,0,0,0],[0,1,0,0],[0,0,1,0.5],[0,0,0,1]])
      elif inImages[currentImage]['planeOrientation'] == "axial" :
         newMatrix=numpy.array([[1,0,0,0],[0,1,0,0.5],[0,0,1,0],[0,0,0,1]])
         
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.csoIdList").setValue(csoId2Modifystr)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.matrix").setValue(newMatrix)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.apply").touch()    
      
    elif event["key"]=="4":
      if inImages[currentImage]['planeOrientation'] == "coronal" or inImages[currentImage]['planeOrientation'] == "axial":
         newMatrix=numpy.array([[1,0,0,-0.5],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
      elif inImages[currentImage]['planeOrientation'] == "sagittal" :
         newMatrix=numpy.array([[1,0,0,0],[0,1,0,-0.5],[0,0,1,0],[0,0,0,1]])
         
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.csoIdList").setValue(csoId2Modifystr)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.matrix").setValue(newMatrix)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.apply").touch()    

    elif event["key"]=="6":
      if inImages[currentImage]['planeOrientation'] == "coronal" or inImages[currentImage]['planeOrientation'] == "axial":
         newMatrix=numpy.array([[1,0,0,0.5],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
      elif inImages[currentImage]['planeOrientation'] == "sagittal" :
         newMatrix=numpy.array([[1,0,0,0],[0,1,0,0.5],[0,0,1,0],[0,0,0,1]])
         
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.csoIdList").setValue(csoId2Modifystr)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.matrix").setValue(newMatrix)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.apply").touch()    

    elif event["key"]=="1":
      
      if inImages[currentImage]['planeOrientation'] == "coronal":
         newMatrix=numpy.array([[0.99984769502584625,0,0.017452413916200969,0],[0,1,0,0],[-0.017452413916200969,0,0.99984769502584625,0],[0,0,0,1]])
      elif inImages[currentImage]['planeOrientation'] == "axial":
         newMatrix=numpy.array([[0.99984769502584625,-0.017452413916200969,0,0],[0.017452413916200969,0.99984769502584625,0,0],[0,0,1,0],[0,0,0,1]])
      elif inImages[currentImage]['planeOrientation'] == "sagittal" :
         newMatrix=numpy.array([[1,0,0,0],[0,0.99984769502584625,-0.017452413916200969,0],[0,0.017452413916200969,0.99984769502584625,0],[0,0,0,0]])
         
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.csoIdList").setValue(csoId2Modifystr)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.matrix").setValue(newMatrix)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.apply").touch()    

      
    elif event["key"]=="9":
      
      if inImages[currentImage]['planeOrientation'] == "coronal":
         newMatrix=numpy.array([[0.99984769502584625,0,-0.017452413916200969,0],[0,1,0,0],[0.017452413916200969,0,0.99984769502584625,0],[0,0,0,1]])
      elif inImages[currentImage]['planeOrientation'] == "axial":
         newMatrix=numpy.array([[0.99984769502584625,0.017452413916200969,0,0],[-0.017452413916200969,0.99984769502584625,0,0],[0,0,1,0],[0,0,0,1]])
      elif inImages[currentImage]['planeOrientation'] == "sagittal" :
         newMatrix=numpy.array([[1,0,0,0],[0,0.99984769502584625,0.017452413916200969,0],[0,-0.017452413916200969,0.99984769502584625,0],[0,0,0,0]])
         
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.csoIdList").setValue(csoId2Modifystr)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.matrix").setValue(newMatrix)
      ctx.field("adaptTemplateMask.CSOAffineTransformationModificator1.apply").touch()        
    
    
    elif event["key"]=="r" or event["key"]=="R":
      print("should reset only current slice")
      #AffineMatrixComposition.inScale

    elif event["key"]=="Minus":
      print("decrease")
    
    elif event["key"]=="Plus":
      print("increase")
    
    elif event["key"]=="Backspace":
      print("delete current CSO")
      
      isCSOmouse = CSOobj.getCSOCurrentlyUnderMouse()
      
      if isCSOmouse is not None:
         idundermouse = isCSOmouse.id
         ctx.field("adaptTemplateMask.CSOManager1.csoSelectedItems").setValue(idundermouse) 
      else:
         ctx.field("adaptTemplateMask.CSOManager1.csoSelectedItems").setValue(csoId2Modifystr) 
      ctx.field("adaptTemplateMask.CSOManager1.csoRemoveSelected").touch()
    
    elif event["key"] == "Return" or event["key"]=="Enter":
      print(event["key"])
      ctx.field("eventChoice").setValue(0)
      ctx.field("View2DExtensions.annotation.editingOn").setBoolValue(True)
      ctx.field("SoView2D.useManagedInteraction").setBoolValue(False)
      ctx.field("adaptTemplateMask.CSOConvertToImage.apply").touch()
      #if "planeOrientation" in inImages[currentImage]:
      nameInter = inImages[currentImage]['WorldChanged'] 
      NameFull=nameInter.replace('.nii','_brain_mask.nii')
      ctx.field("itkImageFileWriterMask.unresolvedFileName").setStringValue(NameFull)
      ctx.field("itkImageFileWriterMask.save").touch()
      
      if currentImage in inImages.keys():
        inImages[currentImage].update({"mask":NameFull})
      
      ctx.field("AlreadyModifiedMaskReader.fileName").setStringValue(NameFull)
      
      ctx.field("AlreadyModifiedMask.currentInput").setValue(1)
      
      ctx.field("inImageInfos").setObject(inImages)
      ctx.field("SoInteractionMapping1.ignoreOtherCommandActions").setBoolValue(False)
      ctx.field("adaptTemplateMask.SoToggleMaskEditor.on").setBoolValue(False)
      ctx.field("LabelViewerMode.text").setStringValue("Viewer Mode")
      
      valIm = currentImage.split('Image')[-1]
      if ctx.hasControl("GenerateBrainMask%s"%valIm):
        try:
          ctx.control("GenerateBrainMask%s"%valIm).setStyleSheetFromString('QPushButton { background-color: "blue"; }')
        except:
          print("test background has control didn't work")
      else:
        global g_HorizontalControl
        try:
          g_HorizontalControl[imiter].control("GenerateBrainMask%s"%valIm).setStyleSheetFromString('QPushButton { background-color: "blue"; }')
        except:
          print("test background g_horizontalcontrol didn't work")  
      #else:
      #  ctx.field("parent:MessageBox.message").setStringValue("you have to precise the plane orientation to be able to save")
      #  ctx.parent().module("MessageBox").showModalDialog("dialog")
      #  return

      
      #we set a inImages object mask done to show the mask when updateDisplay
         
def modifyImageNumber(x):
  ctx.field("NumberImages").setValue(int(ctx.field("NumberImages").value)+x)
  global g_ImageOrientationGraphicsView
  inImages = ctx.field("inImageInfos").object()
  if inImages is not None:
    for ii in range(0,20):
      if "Image%i"%(ctx.field("NumberImages").value+ii) in inImages.keys():
        del inImages["Image%i"%(int(ctx.field("NumberImages").value))]
        
      
  ctx.field("inImageInfos").setObject(inImages)
  initImageOrientationGraphicsView(g_ImageOrientationGraphicsView)
  #updateComboBox()
  #ctx.updateLayout()

def getHorizontalControl(image,horizon):
  
  #print("get %s control"%horizon)
  global g_HorizontalControl
  g_HorizontalControl.update({image:ctx.control(horizon)})
  
def resetBrainMask(Image):

  print("reset brain mask")
  inImages = ctx.field("inImageInfos").object()
  if "mask" in inImages[Image].keys():
    del inImages[Image]["mask"]
  
    valIm = Image.split('Image')[-1]
    if ctx.hasControl("GenerateBrainMask%s"%valIm):
      try:
        ctx.control("GenerateBrainMask%s"%valIm).setStyleSheetFromString('QPushButton { background-color: "white"; }')
      except:
        print("test background has control didn't work")
    else:
      global g_HorizontalControl
      try:
        g_HorizontalControl[Image].control("GenerateBrainMask%s"%valIm).setStyleSheetFromString('QPushButton { background-color: "white"; }')
      except:
        print("test background g_horizontalcontrol didn't work") 
  
  ctx.field("inImageInfos").setObject(inImages)  
  generateBrainMask(Image)
  
def updateCSOfromAdapt():
    ctx.field("adaptTemplateMask.updateCSOButton").touch()
    
def resetZoom():
   ctx.field("SoView2D.unzoom").touch()

   
class temporaryObject():
  def __init__(self):
    self.tempCSOs= {}
  
  def getTempCSOs(self):
    self.tempCSOs.update({currentImage:ctx.field("adaptTemplateMask.CSOManager1.outCSOList").object()})
    
  def setTempCSOs(self):
    ctx.field("adaptTemplateMask.CSOManager1.outCSOList").setObject(self.tempCSOs[currentImage])
    
# ----------------------------------------------------------------------------

# 
#  \file    ChangeTAGCHUV.py
#  \author     neuropsynov
#  \date    2019-01-11
#
#  

# ----------------------------------------------------------------------------

from mevis import *


def fileDialog(whichPath):
  
  if whichPath == "SRTV":
    print("SRTV")
    filename = MLABFileDialog.getExistingDirectory(ctx.expandFilename(ctx.localPath()), "Select the SRTV directory", MLABFileDialog.ShowDirsOnly)
    if filename:
      ctx.field("PathSRTV").value = ctx.unexpandFilename(filename)
    
  if whichPath == "Acq":
    print("Acq")
    filename = MLABFileDialog.getExistingDirectory(ctx.expandFilename(ctx.localPath()), "Select the Acquisition directory", MLABFileDialog.ShowDirsOnly)
    if filename:
      ctx.field("PathAcq").value = ctx.unexpandFilename(filename)
      
      
def PathAcqChanged():
  print("PathAcqChanged")
  ctx.field("DirectDicomImport1.source").setStringValue(ctx.field("PathAcq").value)
  ctx.field("DirectDicomImport1.dplImport").touch()
  ctx.field("MultiFileVolumeListImageOutput.outVolIdx").setValue(0)
  ChangelabelAcqDisplayed()


def PathSRTVChanged():
  print("PathSRTVChanged")
  ctx.field("DirectDicomImport.source").setStringValue(ctx.field("PathSRTV").value)
  ctx.field("DirectDicomImport.dplImport").touch()
  ctx.field("MultiFileVolumeListImageOutput.outVolIdx").setValue(0)
  ChangeLabelSRTVDisplayed()
  
def ChangelabelAcqDisplayed():
  print(ctx.field("MultiFileVolumeListImageOutput.outVolIdx").value)
  ctx.field("SeriesDescriptionAcq").setValue(ctx.field("DicomTagViewer1.tagValue3").value)
  
def ChangeLabelSRTVDisplayed():
  print(ctx.field("MultiFileVolumeListImageOutput1.outVolIdx").value)
  ctx.field("SeriesDescriptionSRTV").setValue(ctx.field("DicomTagViewer.tagValue0").value)
  
  
def SaveDicom():
  import getpass
  ctx.field("DicomTagModify.tagName4").setValue(getpass.getuser())
  ctx.field("DicomTagModify.apply").touch()
  ctx.field("DicomTool.saveSlices").touch()
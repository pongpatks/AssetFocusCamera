#version 0.1

#Import python modules
import os, sys

#import GUI
from PySide2 import QtCore, QtWidgets

#import maya module
import maya.cmds as mc

#Load ui part.
moduleFile = sys.modules[__name__].__file__
moduleDir = os.path.dirname(moduleFile)
sys.path.append(moduleDir)


def loadUi(parent):
	""""""
	print 'loading ui using PySide...'
	from PySide2 import QtUiTools
	loader = QtUiTools.QUiLoader()
	loader.setWorkingDirectory(moduleDir)

	f = QtCore.QFile("%s/assetFocusCam_ui.ui" % moduleDir)
	f.open(QtCore.QFile.ReadOnly)

	myWidget = loader.load(f, parent)

	f.close()

	return myWidget


#===================================================================================================
# global var
#===================================================================================================
ICON_PATH = 'O:/studioTools/icons/etc/'
ICON_CAMERA = ICON_PATH+'camera.png'
ICON_BLANK = ICON_PATH+'blank.png'

#This UI name when run under Maya.
mayaUI = 'AssetFocusCamUI'

class MyForm(QtWidgets.QMainWindow):
	"""Main Window"""
	def __init__(self, parent=None):
		super(MyForm, self).__init__(parent)

		self.cameraGrpNode = 'tmp_camera'

		self.initUi()
		self.initSignals()	

	def initUi(self):
		""""""
		self.setObjectName(mayaUI)
		self.setWindowTitle('Asset Focus Camera Tool')

		self.ui = loadUi(self)
		self.setCentralWidget(self.ui)

		self.resize(256, 400)

		self.loadSceneAssetList()

	def initSignals(self):
		""""""
		self.ui.lst_assetList.doubleClicked.connect(self.lookThroughCam)
		self.ui.btn_addCam.clicked.connect(self.addCamera)
		self.ui.btn_deleteCam.clicked.connect(self.deleteCamera)
		self.ui.btn_clearCam.clicked.connect(self.clearCamera)

	def loadSceneAssetList(self):
		""""""
		existedAssetCams = []
		if mc.ls(self.cameraGrpNode):
			existedCamNodes = mc.listRelatives(self.cameraGrpNode, children=True)
			if existedCamNodes:
				existedAssetCams = [cam.rstrip('_camGrp') for cam in existedCamNodes]
		
		i=0
		for each in mc.file(q=True, r=True): 
			if mc.referenceQuery(each, isLoaded=True): 
				assetName = mc.referenceQuery(each, namespace=True)[1:]

				item = QtWidgets.QListWidgetItem()
				item.setText(assetName)
				if assetName in existedAssetCams:
					item.setIcon(QtGui.QIcon(ICON_CAMERA))
					item.setToolTip(mc.pointConstraint(assetName+'_camGrp',q=True, targetList=True)[0])
				else:
					item.setIcon(QtGui.QIcon(ICON_BLANK))

				self.ui.lst_assetList.insertItem(i, item)
				i+=1

	def lookThroughCam(self, modelIndex):
		""""""
		assetName = str(modelIndex.data(0))
		cam = assetName+'_cam'
		manip = str(modelIndex.data(3))

		if mc.ls(cam) and manip:
			mc.select(manip)
			mc.lookThru(cam)
			mc.viewFit()
		else:
			print 'Error: Create camera first.'

	def addCamera(self):
		""""""
		item = self.ui.lst_assetList.currentItem()
		if not item:
			return False
		
		assetName = item.text()
		
		selected = mc.ls(selection=True, long=True)
		if len(selected)==1:
			selectedSplit = selected[0].split('|')[2].split(':')
			if selectedSplit[0] != assetName or selectedSplit[1] != 'Rig_Grp':
				generateMsgBox('Error', 'Invalid constraining object.')
				return False
		else:
			generateMsgBox('Error', 'Invalid constraining object.')
			return False

		manip = mc.ls(selection=True)[0]	


		if not mc.ls(self.cameraGrpNode):
			mc.createNode('transform', name=self.cameraGrpNode)

		if len(mc.ls([assetName+'_camGrp', assetName+'_cam'])) == 2:
			mc.pointConstraint(item.toolTip(), assetName+'_camGrp', e=True, remove=True)
		else:
			camGrp = mc.createNode('transform', name=assetName+'_camGrp', parent=self.cameraGrpNode)
			tmpCam = mc.camera()
			mc.parent(tmpCam[0], camGrp)
			cam = mc.rename(tmpCam[0], assetName+'_cam')
		
		mc.xform(assetName+'_cam', t=(100,50,0))
		#print mc.xform(manip, q=True, t=True, ws=True)
		mc.select(manip)
		mc.lookThru(assetName+'_cam')
		mc.viewFit()
		#mc.viewLookAt(pos=mc.xform(manip, q=True, t=True, ws=True))
		mc.pointConstraint(manip, assetName+'_camGrp', maintainOffset=True)

		item.setToolTip(manip)
		item.setIcon(QtGui.QIcon(ICON_CAMERA))

	def deleteCamera(self):
		""""""
		item = self.ui.lst_assetList.currentItem()

		if item:
			assetCamGrp = item.text()+'_camGrp'

			if mc.ls(assetCamGrp):
				mc.delete(assetCamGrp)

			item.setToolTip('')	
			item.setIcon(QtGui.QIcon(ICON_BLANK))		

			if mc.ls(self.cameraGrpNode):
				existedCamNodes = mc.listRelatives(self.cameraGrpNode, children=True)
				if not existedCamNodes:
					mc.delete(self.cameraGrpNode)

	def clearCamera(self):
		""""""
		if self.ui.lst_assetList.count() > 0:

			for i in range(self.ui.lst_assetList.count()):
				item = self.ui.lst_assetList.item(i)
				assetCamGrp = item.text()+'_camGrp'

				if mc.ls(assetCamGrp):
					mc.delete(assetCamGrp)
					item.setToolTip('')	
					item.setIcon(QtGui.QIcon(ICON_BLANK))

			mc.delete(self.cameraGrpNode)

def generateMsgBox(title, content):
    """pop up!"""
    msgBox = QtWidgets.QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(content)
    msgBox.exec_() 
#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
HOLO_TO_SLM:
This program takes in an array, converts it into an image, and projects it onto a widget.
This program then creates a window onto a secondary display and displays the
 widget on that window.
There is a "set hologram" button that takes text input and acts on it. Inputting "phaseshift"
will project an optical conveyor beam at phase shifts (2pi/100)*u, u running from 1-100. After it projects one beam, opencv takes a pictuer and saves it with the corresponding phaseshift, then the program projects the next beam, and so on.
Finally, this program also creates a menu on the original display that shows the projected image and a "quit" button.

authors: Nikitas Kanellakopoulos  and David Ruffner

References: zetcode.com
 
Modification History:
2014_07_31: Edited by David B. Ruffner, New York University
2014_09_08: Edited by Nikitas Kanellakopoulos, NYU. Added ability to import an
image and project it onto the window created.
2014_12_04: Edited by Nikitas Kanellakopoulos, NYU. Added the ability to type "phaseshift" and run 100 phaseshifts of the optical conveyor beam
2014_12_09: Edited by Nikitas Kanellakopoulos, NYU. Added opencv capabilities to "phaseshift," allowing it to take pictures of each phaseshift
2015_1_21: Edited by Nikitas Kanellakopoulos, NYU. Added the ability to display a static conveyor beam in the drop down menu.

"""

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4 import QtGui, QtCore
#import projectconveyer
import numpy as np
import qimage2ndarray as q2
import time
import cv2.cv as cv #opencv for taking pictures in camera
import projectconveyor
import planewave
import lens
import os
import re
import vortex
import scanner

		
class ImageChanger(QtGui.QWidget):    
    def __init__(self, images, parent=None):
        super(ImageChanger, self).__init__(parent)        

        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItems(images)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.comboBox)

class MyWindow(QtGui.QWidget):
    def __init__(self, images, parent=None):
        super(MyWindow, self).__init__(parent)
        self.label = QtGui.QLabel(self)

        self.imageChanger = ImageChanger(images)
        self.imageChanger.move(self.imageChanger.pos().y(), self.imageChanger.pos().x() + 100)
        self.imageChanger.show()
        self.imageChanger.comboBox.currentIndexChanged[str].connect(self.changeImage)

	self.setGeometry(300, 400, 850, 400)
        self.setWindowTitle('SLMcontrol') 

	qbtn = QtGui.QPushButton('Quit', self)
        qbtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(500,20) 
	
        self.lbl = QtGui.QLabel(self)
        self.lbl.move(300,100)
	
	self.btn = QtGui.QPushButton('Set Hologram',self)
        self.btn.move(500,70)
        self.btn.clicked.connect(self.showDialog)

        
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.label)

    def showDialog(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
                                              'Enter Hologram:hologram(#)+hologram(#)')
	       
	if ok:
            self.lbl.setText(text)
	    self.lbl.move(450,100)
	    self.lbl.adjustSize() 

	    if text == "phaseshift":
		for u in range(100):
			phiout = projectconveyor.construct(u*(2.*np.pi/100.)) #calls projectconveyer to create the optical conveyor array
			img = SLM(phiout) #sends the array to SLM() which projects the array onto the SLM
			pixmap = QtGui.QPixmap(img)
			pixmap = pixmap.scaledToHeight(300)
 			self.label.setPixmap(pixmap)#sends the array to the smaller window on the main screen
			print(u*(2.*np.pi/100.))
			QtGui.QApplication.processEvents() #pauses the program to let the image buffer onto the SLM and window
			img = cv.QueryFrame(capture) #begins camera capture
			cv.ShowImage("camera",img)
			cv.SaveImage('phaseshift'+str(u) + '.jpg',img)#saves camera capture with corresponding phase shift
	    else: 
		text = text.encode('ascii','ignore')	#converts from unicode to ascii	
		hologram = scanner.scanner(text)#splits up the input into the individual holograms with their paramaters
		phiout = np.zeros((768,1024))
		for indiv in hologram:				
			for file in os.listdir("/home/nikitas/Desktop/TractorMaster"):#searches main folder
				if indiv[0] in file:
					if file.endswith('.py'):
						a = __import__(indiv[0])#imports the corresponding function
						if indiv[1] == '':
							subphiout = a.construct()#default
						else: 
							subphiout = a.construct(float(indiv[1]))#generates the array
						phiout += subphiout #adds the arrays
		phiout = phiout % 256 #rescaling, not sure why it doesn't mess up when only one array is inputted
		converted_image = q2.gray2qimage(phiout, normalize =  True)
		pixmap = QtGui.QPixmap(converted_image)
		pixmap = pixmap.scaledToHeight(300)
		SLM(converted_image)
       		self.label.setPixmap(pixmap)
					 
     
    def changeImage(self, pathToImage): #Allows user to cycle through various beam setups
	if pathToImage.endswith('planewave.npy'): #converting any non-default array into an image
        	phiout = planewave.construct()
    		converted_image = q2.gray2qimage(phiout, normalize =  True)
	elif pathToImage.endswith('lens.npy'): #converting any non-default array into an image
        	phiout = lens.construct()
    		converted_image = q2.gray2qimage(phiout, normalize =  True)
	elif pathToImage.endswith('conveyorarray.npy'): #converting any non-default array into an image
        	phiout = projectconveyor.construct()
    		converted_image = q2.gray2qimage(phiout, normalize =  True)
	elif pathToImage.endswith('vortex.npy'): #converting any non-default array into an image
        	phiout = vortex.construct()
    		converted_image = q2.gray2qimage(phiout, normalize =  True)
        else: converted_image = pathToImage
        pixmap = QtGui.QPixmap(converted_image)
	pixmap = pixmap.scaledToHeight(300)
	SLM(converted_image)
        self.label.setPixmap(pixmap)

def SLM(image='heart.png'): #default image set to locally stored file
    w = QtGui.QWidget(QtGui.QApplication.desktop().screen(1)) #projects window onto secondary display
    w.setGeometry(0,0,1024,768)
    pic = QtGui.QLabel(w) #Picture to be projected on SLM
    pic.setGeometry(0,0,1024,768)
    img = QtGui.QPixmap(image)
    img = img.scaled(1024,768)
    pic.setPixmap(img)
    w.show()
    return img

cv.NamedWindow("camera",1) #starts up opencv
capture = cv.CaptureFromCAM(0)

if __name__ == "__main__":
    import sys

    images = [  "heart.png","star.png","conveyorarray.npy","planewave.npy", "lens.npy", "vortex.npy"]

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MyWindow')
 
    main = MyWindow(images)
    main.show()
   
    

    sys.exit(app.exec_())
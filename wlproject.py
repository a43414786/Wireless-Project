import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import pyqtSlot, right
import cv2
import numpy as np
import time
import pickle
import math

class UI:
    
    def __init__(self):
        self.setUI()

    def label(self,name,position):
        label = QLabel(self.widget)
        label.setText(name)
        label.setFont(QFont('Arial', 12))
        label.resize(250,32)
        label.move(position[0],position[1])
        return label

    def updatalabel(self,time,best,threshold,entropy,my,car_insys,car_incall):

        self.time.setText       ("Time\t\t: " + str(time) + "   (s)")
        
        self.best.setText       ("Best Effect\t: " + str(best))
        
        self.threshold.setText  ("Threshold\t: " + str(threshold))
 
        self.entropy.setText    ("Entropy\t\t: " + str(entropy))
        
        self.my.setText         ("My design\t: " + str(my))

        self.car_insys.setText  ("Cars in system\t: " + str(car_insys))

        self.car_incall.setText ("Cars in call\t: " + str(car_incall))

    def setUI(self):
        
        self.app = QApplication(sys.argv)
    
        self.widget = QWidget()

        
        self.time = self.label("Time\t\t: 0" + "   (s)" ,(32,32))
        self.best = self.label("Best Effect\t: 0"  ,(32,64))
        self.threshold = self.label("Threshold\t: 0"   ,(32,96))
        self.entropy = self.label("Entropy\t\t: 0"    ,(32,128))
        self.my =   self.label("My design\t: 0"    ,(32,160))
        self.car_insys =   self.label("Cars in system\t: 0"    ,(32,192))
        self.car_incall =   self.label("Cars in call\t: 0"    ,(32,224))

        self.widget.setGeometry(50,50,50+250,50+250)
        self.widget.setWindowTitle("2021 Opencvdl Hw1")
        self.widget.show()

class car:
    def __init__(self,position,dir,hv,signalmap):
        self.callmu = 10*60
        self.waitmu = 6*60
        self.callsigma = 1*60
        self.waitsigma = 2*60
        self.point = position
        self.direct = dir
        self.hv = hv
        self.incall = 0
        self.call = 0
        self.waitforcall = 0
        self.signalmap = signalmap
        self.thresholdlim = 20
        self.gap = 25

        self.best = 0
        self.threshold = 0
        self.entropy = 0
        self.my = 0
        self.mymin = 15
        self.mymax = 25
    
        self.waittime()
    def update_position(self):
        self.point[0] = self.point[0] + self.direct[0]
        self.point[1] = self.point[1] + self.direct[1]
    def waittime(self):
        self.waitforcall = int(np.random.normal(self.waitmu,self.waitsigma))
    def calltime(self):
        self.call = int(np.random.normal(self.callmu,self.callsigma))
    def check(self):
        if self.waitforcall == 0:
            self.calltime()
            self.incall = 1
            maxidx = np.argmax(self.signalmap[self.point[0]][self.point[1]])
            self.best = maxidx
            self.threshold = maxidx
            self.entropy = maxidx
            self.my = maxidx
            self.waitforcall -= 1
        else:
            self.waitforcall -= 1

        if self.incall == 1:
            if self.call == 0:
                self.incall = 0
                self.waittime()
                return 0,0,0,0
            else:
                self.call -= 1
                a = self.checkbest()
                b = self.checkthreshold()
                c = self.checkentropy()
                d = self.checkmy()
                return a,b,c,d
        else:
            return 0,0,0,0
    def checkbest(self):
        maxidx = np.argmax(self.signalmap[self.point[0]][self.point[1]])
        if maxidx != self.best:
            self.best = maxidx
            return 1
        else:
            return 0
    def checkthreshold(self):
        sig = self.signalmap[self.point[0]][self.point[1]][self.threshold]
        if sig < self.thresholdlim:
            maxidx = np.argmax(self.signalmap[self.point[0]][self.point[1]])
            if maxidx != self.threshold:
                self.threshold = maxidx
                return 1
        return 0
    def checkentropy(self):
        sig = self.signalmap[self.point[0]][self.point[1]][self.entropy]
        maxsig = max(self.signalmap[self.point[0]][self.point[1]])
        if abs(maxsig - sig) > self.gap:
            maxidx = np.argmax(self.signalmap[self.point[0]][self.point[1]])
            self.entropy = maxidx
            return 1
        else:
            return 0

    def checkmy(self):
        sig = self.signalmap[self.point[0]][self.point[1]][self.my]
        if sig < self.mymin:
            maxsig = max(self.signalmap[self.point[0]][self.point[1]])
            if maxsig >= self.mymin:
                maxidx = np.argmax(self.signalmap[self.point[0]][self.point[1]])
                self.my = maxidx
                return 1
        elif sig < self.mymax:
            change = np.random.randint(0,10)
            if change == 0:
                maxidx = np.argmax(self.signalmap[self.point[0]][self.point[1]])
                if maxidx != self.my:
                    self.my = maxidx
                    return 1
        return 0

class base:
    def __init__(self,position,block_size,freq):
        self.point = position
        self.pt = 120
        self.signal_map = self.makesignalmap(block_size,freq)
    def get_signal(self,position):
        return self.signal_map[position[0]][position[1]]
    def makesignalmap(self,block_size,freq):
        img_size = (block_size*9+21,block_size*9+21)
        signal_map = np.zeros(img_size)
        for i in range(10,img_size[0]-10):
            for j in range(10,img_size[1]-10):
                if (i-10) % block_size == 0:
                    signal_map[i][j] = self.pt - (32.45 + 20*math.log10(freq) + 20*math.log10(self.distance((i,j))/100))
                if (j-10) % block_size == 0:
                    signal_map[i][j] = self.pt - (32.45 + 20*math.log10(freq) + 20*math.log10(self.distance((i,j))/100))
        return signal_map
    def distance(self,position):
        return ((self.point[0] - position[0])**2 + (self.point[1] - position[1])**2)**0.5

        

class map:
    def __init__(self):
        self.time = time.time()
        self.base_size = 15
        self.car_size = 11
        self.car_add_rate = 5       #per min
        self.base_add_rate = 0.1
        self.base_color = [255,0,200] 
        self.car_color = [255,200,0] 
        self.signalmap = 0
        self.cars = []
        self.block_size = 100
        self.img = 0
        self.counter = 0

        self.best = 0
        self.threshold = 0
        self.entropy = 0
        self.my = 0

        self.makemap()

    def point_show(self,point,size,color):
        for i in range(size//2):
            for j in range(size//2):
                self.img[point[0]+i][point[1]+j] = color
                self.img[point[0]+i][point[1]-j] = color
                self.img[point[0]-i][point[1]+j] = color
                self.img[point[0]-i][point[1]-j] = color

    def change_dir(self,i):
        dir = np.random.randint(0,32)    
        if i.hv == 0:
            if dir <= 15:   #straight
                i.direct = [0,1]
                i.hv = 0
            elif 16 <= dir <= 17:   #back
                i.direct = [0,-1]
                i.hv = 1
            elif 18 <= dir <= 24:   #right
                i.direct = [1,0]
                i.hv = 2
            else:   #left
                i.direct = [-1,0]
                i.hv = 3
        elif i.hv == 1:
            if dir <= 15:   #straight
                i.direct = [0,-1]
                i.hv = 1
            elif 16 <= dir <= 17:   #back
                i.direct = [0,1]
                i.hv = 0
            elif 18 <= dir <= 24:   #right
                i.direct = [-1,0]
                i.hv = 3
            else:   #left
                i.direct = [1,0]
                i.hv = 2            
        elif i.hv == 2:
            if dir <= 15:   #straight
                i.direct = [1,0]
                i.hv = 2
            elif 16 <= dir <= 17:   #back
                i.direct = [-1,0]
                i.hv = 3
            elif 18 <= dir <= 24:   #right
                i.direct = [0,-1]
                i.hv = 1
            else:   #left
                i.direct = [0,1]
                i.hv = 0
        else:
            if dir <= 15:   #straight
                i.direct = [-1,0]
                i.hv = 3
            elif 16 <= dir <= 17:   #back
                i.direct = [1,0]
                i.hv = 2
            elif 18 <= dir <= 24:   #right
                i.direct = [0,1]
                i.hv = 0
            else:   #left
                i.direct = [0,-1]
                i.hv = 1    

    def update(self):

        self.addcar()

        with open("map.pickle" , "rb") as f:
            self.img = pickle.load(f)

        self.counter = 0

        for index,i in enumerate(self.cars):

            self.point_show(i.point,self.car_size,self.car_color)
            
            a,b,c,d = i.check()
            self.best += a
            self.threshold += b
            self.entropy += c
            self.my += d

            if(i.incall):
                self.counter += 1
            
            i.update_position()
            
            if (i.point[0] < 10) or (i.point[0] > self.block_size*9+10) or (i.point[1] < 10) or (i.point[1] > self.block_size*9+10):
                self.cars.pop(index)
                continue

            if (((i.point[0]-10) % self.block_size) == 0) and (((i.point[1]-10) % self.block_size) == 0):
                self.change_dir(i)
                
    def addcar(self):
        if  np.random.poisson(self.car_add_rate/60) == 1:
            i = np.random.randint(0,10)
            direct = [0,0]
            hv = 0
            dir = np.random.randint(0,4)
            if dir == 0:
                direct = [0,1]
                hv = 0
            elif dir == 1:
                direct = [0,-1]
                hv = 1
            elif dir == 2:
                direct = [1,0]
                hv = 2
            else:
                direct = [-1,0]
                hv = 3
            if (i == 0) or (i == 9):
                j = np.random.randint(1,9)
                self.cars.append(car([i*self.block_size + 10,j*self.block_size + 10],direct,hv,self.signalmap))
            else:
                j = np.random.randint(0,2)
                if j == 1:
                    j=9
                self.cars.append(car([i*self.block_size + 10,j*self.block_size + 10],direct,hv,self.signalmap))
        
    def create_base(self,img_size):
        bases = []
        for i in range(10,img_size[0]-10):
            for j in range(10,img_size[1]-10):
                if ((i-10) % (self.block_size/2) == 0) and ((i-10) % self.block_size != 0):
                    if ((j-10) % (self.block_size/2) == 0) and ((j-10) % self.block_size != 0):
                        if np.random.randint(0,int(1/self.base_add_rate)) == 0:
                            pos = np.random.randint(0,4)
                            f = np.random.randint(1,11)
                            if pos == 0:
                                self.point_show((i+10,j),self.base_size,self.base_color)
                                bases.append(base((i+10,j),self.block_size,f*100))
                            elif pos == 1:
                                self.point_show((i-10,j),self.base_size,self.base_color)
                                bases.append(base((i-10,j),self.block_size,f*100))
                            elif pos == 2:
                                self.point_show((i,j+10),self.base_size,self.base_color)
                                bases.append(base((i,j+10),self.block_size,f*100))
                            else:
                                self.point_show((i,j-10),self.base_size,self.base_color)
                                bases.append(base((i,j-10),self.block_size,f*100))
        return bases

    def makemap(self):
        img_size = (self.block_size*9+21,self.block_size*9+21,3)
        self.img = np.zeros(img_size)
        for i in range(10,img_size[0]-10):
            for j in range(10,img_size[1]-10):
                if (i-10) % self.block_size == 0:
                    self.img[i][j] = [255,255,255]
                if (j-10) % self.block_size == 0:
                    self.img[i][j] = [255,255,255]
        
        bases = self.create_base(img_size)
        
        self.signalmap = np.zeros((self.block_size*9+21,self.block_size*9+21,len(bases)))
        for i in range(10,img_size[0]-10):
            for j in range(10,img_size[1]-10):
                sig = []
                for k in bases:
                    sig.append(k.signal_map[i][j])
                self.signalmap[i][j] = sig
        
        with open("map.pickle" , "wb") as f:
            pickle.dump(self.img,f)

def main():
    ui = UI()
    img = map()
    print("start")
    cv2.namedWindow("img")
    counter = 0
    while 1:
        img.update()
        cv2.imshow("img",img.img)
        ui.updatalabel(counter,img.best,img.threshold,img.entropy,img.my,len(img.cars),img.counter)
        time.sleep(0.001)
        dead = cv2.waitKey(1)
        counter += 1
        if dead != -1:
            break
if __name__ == "__main__":
    main()



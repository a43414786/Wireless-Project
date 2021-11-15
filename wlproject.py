import cv2
import numpy as np
import time
import pickle

class car:
    def __init__(self,position,dir,hv):
        self.point = position
        self.direct = dir
        self.hv = hv
    def update_position(self):
        self.point[0] = self.point[0] + self.direct[0]
        self.point[1] = self.point[1] + self.direct[1]

class base:
    def __init__(self,position):
        self.point = position

class map:
    def __init__(self):
        self.time = time.time()
        self.base_size = 9
        self.car_size = 7
        self.base_color = [255,0,200] 
        self.car_color = [255,200,0] 
        self.bases = []
        self.cars = []
        self.block_size = 50
        self.img = 0

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
                i.direct = [0,10]
                i.hv = 0
            elif 16 <= dir <= 17:   #back
                i.direct = [0,-10]
                i.hv = 1
            elif 18 <= dir <= 24:   #right
                i.direct = [10,0]
                i.hv = 2
            else:   #left
                i.direct = [-10,0]
                i.hv = 3
        elif i.hv == 1:
            if dir <= 15:   #straight
                i.direct = [0,-10]
                i.hv = 1
            elif 16 <= dir <= 17:   #back
                i.direct = [0,10]
                i.hv = 0
            elif 18 <= dir <= 24:   #right
                i.direct = [-10,0]
                i.hv = 3
            else:   #left
                i.direct = [10,0]
                i.hv = 2            
        elif i.hv == 2:
            if dir <= 15:   #straight
                i.direct = [10,0]
                i.hv = 2
            elif 16 <= dir <= 17:   #back
                i.direct = [-10,0]
                i.hv = 3
            elif 18 <= dir <= 24:   #right
                i.direct = [0,-10]
                i.hv = 1
            else:   #left
                i.direct = [0,10]
                i.hv = 0
        else:
            if dir <= 15:   #straight
                i.direct = [-10,0]
                i.hv = 3
            elif 16 <= dir <= 17:   #back
                i.direct = [10,0]
                i.hv = 2
            elif 18 <= dir <= 24:   #right
                i.direct = [0,10]
                i.hv = 0
            else:   #left
                i.direct = [0,-10]
                i.hv = 1    

    def update(self):

        self.addcar()

        with open("a.pickle" , "rb") as f:
            self.img = pickle.load(f)

        for index,i in enumerate(self.cars):

            self.point_show(i.point,self.car_size,self.car_color)
            
            i.update_position()
            
            if (i.point[0] < 10) or (i.point[0] > self.block_size*9+10) or (i.point[1] < 10) or (i.point[1] > self.block_size*9+10):
                self.cars.pop(index)
                continue

            if (((i.point[0]-10) % self.block_size) == 0) and (((i.point[1]-10) % self.block_size) == 0):
                self.change_dir(i)
                
    def addcar(self):
        if  np.random.randint(0,12) == 0:
            i = np.random.randint(0,10)
            direct = [0,0]
            hv = 0
            dir = np.random.randint(0,4)
            if dir == 0:
                direct = [0,10]
                hv = 0
            elif dir == 1:
                direct = [0,-10]
                hv = 1
            elif dir == 2:
                direct = [10,0]
                hv = 2
            else:
                direct = [-10,0]
                hv = 3
            if (i == 0) or (i == 9):
                j = np.random.randint(0,10)
                self.cars.append(car([i*self.block_size + 10,j*self.block_size + 10],direct,hv))
            else:
                j = np.random.randint(0,2)
                if j == 1:
                    j=9
                self.cars.append(car([i*self.block_size + 10,j*self.block_size + 10],direct,hv))
        
    def create_base(self,img_size):
        for i in range(10,img_size[0]-10):
            for j in range(10,img_size[1]-10):
                if ((i-10) % (self.block_size/2) == 0) and ((i-10) % self.block_size != 0):
                    if ((j-10) % (self.block_size/2) == 0) and ((j-10) % self.block_size != 0):
                        if np.random.randint(0,10) == 0:
                            pos = np.random.randint(0,4)
                            if pos == 0:
                                self.point_show((i+10,j),self.base_size,self.base_color)
                                self.bases.append(base((i+10,j)))
                            elif pos == 1:
                                self.point_show((i-10,j),self.base_size,self.base_color)
                                self.bases.append(base((i-10,j)))
                            elif pos == 2:
                                self.point_show((i,j+10),self.base_size,self.base_color)
                                self.bases.append(base((i,j+10)))
                            else:
                                self.point_show((i,j-10),self.base_size,self.base_color)
                                self.bases.append(base((i,j-10)))

    def makemap(self):
        img_size = (self.block_size*9+21,self.block_size*9+21,3)
        self.img = np.zeros(img_size)
        for i in range(10,img_size[0]-10):
            for j in range(10,img_size[1]-10):
                if (i-10) % self.block_size == 0:
                    self.img[i][j] = [255,255,255]
                if (j-10) % self.block_size == 0:
                    self.img[i][j] = [255,255,255]
        
        self.create_base(img_size)
        with open("a.pickle" , "wb") as f:
            pickle.dump(self.img,f)

def main():
    img = map()
    img.makemap()
    
    cv2.namedWindow("img")
    while 1:
        img.update()
        cv2.imshow("img",img.img)
        time.sleep(0.001)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
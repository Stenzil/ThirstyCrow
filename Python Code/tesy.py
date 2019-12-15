import numpy as np
import cv2
import cv2.aruco as aruco
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import pygame
from objloader import *
import bot_move as pp
import threading 
import time

crowid=pp.crowid
pebble= pp.pebble
water=pp.water
texture_object = None
texture_background = None
camera_matrix = None
dist_coeff = None
cap = cv2.VideoCapture(0)
INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [ 1.0, 1.0, 1.0, 1.0]])
crow = None
pot0=None
pot1=None
pot2=None
pot3=None
fullpeb=None
halfpeb=None
"""
Function Name : getCameraMatrix()
Input: None
Output: camera_matrix, dist_coeff
Purpose: Loads the camera calibration file provided and returns the camera and
         distortion matrix saved in the calibration file.
"""
def getCameraMatrix():
        global camera_matrix, dist_coeff
        with np.load('Camera.npz') as X:
                camera_matrix, dist_coeff, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]
"""
Function Name : main()
Input: None
Output: None
Purpose: Initialises OpenGL window and callback functions. Then starts the event
         processing loop.
"""
def main():
        glutInit()
        getCameraMatrix()
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(625, 100)
        glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
        window_id = glutCreateWindow("OpenGL")
        init_gl()
        glutDisplayFunc(drawGLScene)
        glutIdleFunc(drawGLScene)
        glutReshapeFunc(resize)
        glutMainLoop()
"""
Function Name : init_gl()
Input: None
Output: None
Purpose: Initialises various parameters related to OpenGL scene.
"""  
def init_gl():
        print("LOADING OBJECTS")    
        global texture_object, texture_background
        global crow
        global pot0
        global pot1
        global pot2
        global pot3
        global halfpeb
        global fullpeb
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0) 
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)   
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        texture_background = glGenTextures(1)
        texture_object = glGenTextures(1)
        crow = OBJ('Crow.obj', swapyz=True)
        pot0 = OBJ('game.obj', swapyz=True)
        pot1 = OBJ('untitled1.obj', swapyz=True)
        pot2 = OBJ('untitled2.obj', swapyz=True)
        pot3 = OBJ('untitled3.obj', swapyz=True)
        halfpeb = OBJ('peb2.obj', swapyz=True)
        fullpeb = OBJ('peb1.obj', swapyz=True)
        print("COMPLETED")
 """
Function Name : resize()
Input: None
Output: None
Purpose: Initialises the projection matrix of OpenGL scene
"""        
def resize(w,h):
        ratio =1.125* w / h
        glMatrixMode(GL_PROJECTION)
        glViewport(0,0,w,h)
        gluPerspective(25, ratio, 0.1, 100.0)
"""
Function Name : drawGLScene()
Input: None
Output: None
Purpose: It is the main callback function which is called again and
         again by the event processing loop. In this loop, the webcam frame
         is received and set as background for OpenGL scene. ArUco marker is
         detected in the webcam frame and 3D model is overlayed on the marker
         by calling the overlay() function.
"""
def drawGLScene():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ar_list = []
        ret,frame=cap.read()
        if ret == True:
            
                draw_background(frame)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                ar_list = detect_markers(frame)
                for i in ar_list:
                        overlay(frame, ar_list, i[0],None)
                                
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
        glFlush()
        glutSwapBuffers()
        
"""
Function Name : detect_markers()
Input: img (numpy array)
Output: aruco list in the form [(aruco_id_1, centre_1, rvec_1, tvec_1),(aruco_id_2,
        centre_2, rvec_2, tvec_2), ()....]
Purpose: This function takes the image in form of a numpy array, camera_matrix and
         distortion matrix as input and detects ArUco markers in the image. For each
         ArUco marker detected in image, paramters such as ID, centre coord, rvec
         and tvec are calculated and stored in a list in a prescribed format. The list
         is returned as output for the function
"""      
def detect_markers(img):
        aruco_list = []
        markerLength=100
        ################################################################
        #################### Same code as Task 1.1 #####################
        ################################################################
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        aruco_dict=aruco.Dictionary_get(aruco.DICT_5X5_250)
        parameters=aruco.DetectorParameters_create()
        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        rvec, tvec,  _objPoints = aruco.estimatePoseSingleMarkers(corners, markerLength, camera_matrix, dist_coeff)
        try:    
                for i in range(0,len(ids)):
                        Id=ids[i][0]
                        corn=corners[i][0]
                        t=tvec[i]
                        r=rvec[i]
                        x=int((corn[0][0]+corn[1][0]+corn[2][0]+corn[3][0])/4)    
                        y=int((corn[0][1]+corn[1][1]+corn[2][1]+corn[3][1])/4)
                        d=(Id, (x,y), np.array([r]), np.array([t]))
                        aruco_list.append(d)
                        img = cv2.line(img, (x,y), (x,y), (0,0,255), 4) 
                        img = cv2.aruco.drawDetectedMarkers(img,corners,ids,(0,0,255))
                return aruco_list
        except:
                return []

"""
Function Name : draw_background()
Input: img (numpy array)
Output: None
Purpose: Takes image as input and converts it into an OpenGL texture. That
         OpenGL texture is then set as background of the OpenGL scene
"""
def draw_background(img):
        height,width,channels=img.shape
        glEnable(GL_TEXTURE_2D)
        texid = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D ,0, GL_RGB
		, width, height
		, 0, GL_BGR, GL_UNSIGNED_BYTE
		, img)
        glBindTexture(GL_TEXTURE_2D, texid)
        glPushMatrix()
        glTranslatef(0.0,0.0,-12.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex3f(-4.0, -3.0, 0.0)
        glTexCoord2f(1.0, 1.0); glVertex3f( 4.0, -3.0, 0.0)
        glTexCoord2f(1.0, 0.0); glVertex3f( 4.0,  3.0, 0.0)
        glTexCoord2f(0.0, 0.0); glVertex3f(-4.0,  3.0, 0.0)
        glEnd()
        glPopMatrix()
        return None
"""
Function Name : init_object_texture()
Input: Image file path
Output: None
Purpose: Takes the filepath of a texture file as input and converts it into OpenGL
         texture. The texture is then applied to the next object rendered in the OpenGL
         scene.
"""
def init_object_texture(image_filepath):
        tex = cv2.imread(image_filepath)
        glClear(GL_DEPTH_BUFFER_BIT)
        height,width,channels=tex.shape
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_object)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                        0, GL_BGR, GL_UNSIGNED_BYTE, tex)
        return None
k=1
cut=pp.savepositions1()
shift=1
def play():
    global shift
    global k
    k=2
    time.sleep(7)
    shift=2
    pp.finalmove(cut)
k1 = threading.Thread(target=play)

"""
Function Name : overlay()
Input: img (numpy array), aruco_list, aruco_id, texture_file (filepath of texture file)
Output: None
Purpose: Receives the ArUco information as input and overlays the 3D Model of a teapot
         on the ArUco marker. That ArUco information is used to
         calculate the rotation matrix and subsequently the view matrix. Then that view matrix
         is loaded as current matrix and the 3D model is rendered.
        this function once call the finalmove from bot_move file import above in a different
        thread. This function then continiously keeps running and overlays blender objects in the 
        different cases. 
"""           
def overlay(img, ar_list, ar_id, texture=None):
        global k
        global water 
        global pebble
        global crowid
        wlev=999
        lev=999
        for x in ar_list:
                if ar_id == x[0]:
                        centre, rvec, tvec = x[1], x[2], x[3]
        rmtx = cv2.Rodrigues(rvec)[0]
        view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0][0][0]/350-0.10],
                            [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvec[0][0][1]/300-1.0],
                            [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvec[0][0][2]/100],
                            [0.0       ,0.0       ,0.0       ,1.0    ]])

        view_matrix = view_matrix * INVERSE_MATRIX
        view_matrix = np.transpose(view_matrix)
        glPushMatrix()
        glLoadMatrixd(view_matrix)
        
        if ar_id==crowid:
            glScale(0.5,0.5,0.5)
            glTranslatef(0,0,-1)
            glCallList(crow.gl_list)
        if ar_id==water[0][-2]:
            wlev=water[0][-1]
        if wlev==0:
            glScale(0.8,0.8,0.5)
            glCallList(pot0.gl_list)
        for points in pebble:
            #init_object_texture("rk.png")
            if ar_id==points[-2]:
                lev=points[-1]
                if lev>=1:
                    glScale(0.4,0.4,0.8)
                    glCallList(fullpeb.gl_list)
                elif lev==0:
                    glScale(0.4,0.4,0.8)
                    glCallList(halfpeb.gl_list)
        if k==1:
            k1.start()
        if wlev==1:
            glScale(0.8,0.8,0.5)
            glCallList(pot1.gl_list)
        if wlev==2:
            glScale(0.8,0.8,0.5)
            glCallList(pot2.gl_list)
        if wlev==3:
            glScale(0.8,0.8,0.5)
            glCallList(pot3.gl_list)
        glPopMatrix()
        k=k+1


if __name__=="__main__":
    main()

# -*- coding: utf-8 -*-
"""
Created on Sun May 17 11:59:35 2015

@author: luan
"""

import cv2
import numpy as np
from mpeg import mpeg

if __name__ == '__main__':
	video = cv2.VideoCapture('/home/luan/Dropbox/workspace/sublime_projects/TCC_shared/mpeg/videos/foreman_cif.mp4')
	sspace = 16
	sequence = []
	mbr, mbc = [16, 16]
	
	def resize (frame):
		rR, rC, rD = frame.shape
		aR = aC = 0

		if rR % mbr != 0:
			aR = rR + (mbr - (rR%mbr))
		else:
			aR = rR

		if rC % mbc != 0:
			aC = rC + (mbc - (rC%mbc))
		else:
			aC = rC

		for i in range (0,rR,2):
			for j in range (0,rC,2):
				frame[i+1,j,1] = frame[i,j+1,1] = frame[i+1,j+1,1] = frame[i,j,1]
				frame[i+1,j,2] = frame[i,j+1,2] = frame[i+1,j+1,2] = frame[i,j,2]

		auxImage = np.zeros((aR, aC, rD), np.float32)
		auxImage[:rR,:rC] = frame

		return auxImage
	
	def precover (pastfr, currentfr, motionVecs, sspace):
		result = np.zeros(pastfr.shape, np.float32)
		count = 0
			
		for i in range(0,currentfr.shape[0],16):
			for j in range(0,currentfr.shape[1],16):
				a, b = motionVecs[count]
				aR, aC, aD = currentfr.shape
				backgroundImgPast = np.zeros((aR+2*sspace, aC+2*sspace, aD), np.float32)
				backgroundImgPast[sspace:sspace+aR, sspace:sspace+aC] = pastfr
				result[i:i+16, j:j+16] = backgroundImgPast[i+a+sspace:i+a+sspace+16, j+b+sspace:j+b+sspace+16] + currentfr[i:i+16, j:j+16]
				count += 1
		result[result>255.0] = 255.0
		result[result<0.0] = 0.0
		return result
		
	def brecover (pastfr, currentfr, postfr, motionVecs, sspace):
		result = np.zeros(pastfr.shape, np.float32)
		count = 0
		
		aR, aC, aD = currentfr.shape
		backgroundImgPast = np.zeros((aR+2*sspace, aC+2*sspace, aD), np.float32)
		backgroundImgPast[sspace:sspace+aR, sspace:sspace+aC] = pastfr
		backgroundImgPost= np.zeros((aR+2*sspace, aC+2*sspace, aD), np.float32)
		backgroundImgPost[sspace:sspace+aR, sspace:sspace+aC] = postfr
	
		for i in range(0,currentfr.shape[0],16):
			for j in range(0,currentfr.shape[1],16):
				if motionVecs[count][1] == 'i':
					a, b, c, d = motionVecs[count][2:]
#					aR, aC, aD = currentfr.shape
#					backgroundImgPast = np.zeros((aR+2*sspace, aC+2*sspace, aD), np.float32)
#					backgroundImgPast[sspace:sspace+aR, sspace:sspace+aC] = pastfr
#					backgroundImgPost= np.zeros((aR+2*sspace, aC+2*sspace, aD), np.float32)
#					backgroundImgPost[sspace:sspace+aR, sspace:sspace+aC] = postfr
					result[i:i+16, j:j+16] = (backgroundImgPast[i+a+sspace:i+a+sspace+16, j+b+sspace:j+b+sspace+16] + 2.0*currentfr[i:i+16, j:j+16] + backgroundImgPost[i+c+sspace:i+c+sspace+16, j+d+sspace:j+d+sspace+16])/2.0
					
				if motionVecs[count][1] == 'b':
					a, b = motionVecs[count][2:]
#					aR, aC, aD = currentfr.shape
#					backgroundImgPost = np.zeros((aR+2*sspace, aC+2*sspace, aD), np.float32)
#					backgroundImgPost[sspace:sspace+aR, sspace:sspace+aC] = postfr
					result[i:i+16, j:j+16] = backgroundImgPost[i+a+sspace:i+a+sspace+16, j+b+sspace:j+b+sspace+16] + currentfr[i:i+16, j:j+16]
					
				elif motionVecs[count][1] == 'f':
					a, b = motionVecs[count][2:]
#					aR, aC, aD = currentfr.shape
#					backgroundImgPast = np.zeros((aR+2*sspace, aC+2*sspace, aD), np.float32)
#					backgroundImgPast[sspace:sspace+aR, sspace:sspace+aC] = pastfr
					result[i:i+16, j:j+16] = backgroundImgPast[i+a+sspace:i+a+sspace+16, j+b+sspace:j+b+sspace+16] + currentfr[i:i+16, j:j+16]
					
				count += 1
		result[result>255.0] = 255.0
		result[result<0.0] = 0.0
		return np.uint8(result)
		
	count = 0
	ret = video.isOpened()
	while count <= 200: # ret:
		ret , fr = video.read()
		if ret != False:
			sequence.append(resize(cv2.cvtColor(fr, cv2.COLOR_BGR2YCR_CB)))
		count += 1
	video.release()
			
	def plotvecs(frame, vecs, spc):
		m,n,d = frame.shape
#		new = np.zeros((m+2*spc,n+2*spc,d), np.float32)+255
		
		frame[frame>255.0] = 255.0
		frame[frame<0.0] = 0.0
#		
		frame = cv2.cvtColor(frame, cv2.COLOR_YCR_CB2BGR)
		
		new = frame
		count = 0
		for i in range(0, m, 16):
			for j in range(0, n, 16):
				if vecs[count][1] == 'b':
					cv2.circle(new, (j+vecs[count][2+1], i+vecs[count][1+1]),1,(255,0,0),-1)
					cv2.line(new,(j,i),(j+vecs[count][2+1],i+vecs[count][1+1]),(255,0, 0),1)
				elif vecs[count][1] == 'i':
					cv2.line(new,(j,i),(j+vecs[count][2+1],i+vecs[count][1+1]),(102,255,0),1)
					cv2.circle(new, (j+vecs[count][2+1],i+vecs[count][1+1]),1,(102,255,0),-1)
					cv2.line(new,(j,i),(j+vecs[count][4+1],i+vecs[count][3+1]),(102,255,0),1)
					cv2.circle(new, (j+vecs[count][4+1],i+vecs[count][3+1]),1,(102,255,0),-1)
				elif vecs[count][1] == 'f':
					cv2.circle(new, (j+vecs[count][2+1],i+vecs[count][1+1]),1,(0,0,255),-1)
					cv2.line(new,(j,i),(j+vecs[count][2+1],i+vecs[count][1+1]),(0,0,255),1)
				else:
					cv2.circle(new, (j+vecs[count][1],i+vecs[count][0]),1,(0,0,255),-1)
					cv2.line(new,(j,i),(j+vecs[count][1],i+vecs[count][0]),(0,0,255),1)
				count += 1
				
		new[new>255.0] = 255.0
		new[new<0.0] = 0.0
		return new #cv2.cvtColor(new, cv2.COLOR_YCR_CB2BGR)
			
	pframe = mpeg.Pframe(sequence[15], sequence[18], sspace,1)
	test = precover(sequence[15], pframe.pframe, pframe.motionVec, sspace) 
			
#	bframe = mpeg.Bframe(sequence[15], sequence[16], sequence[18], sspace, 1)
#	test = brecover(sequence[15], bframe.bframe, sequence[18], bframe.motionVec, sspace)
#	
#	ploting = plotvecs(np.uint8(sequence[16]), bframe.motionVec, sspace)
	ploting = plotvecs(np.uint8(test), pframe.motionVec, sspace)
	ploting[ploting>255.0] = 255.0
	ploting[ploting<0.0] = 0.0

	cv2.imshow('Ploting', np.uint8(ploting))
	
	cv2.imshow('Test', cv2.cvtColor(np.uint8(test), cv2.COLOR_YCR_CB2BGR) )
#	cv2.imshow('Test', test )
	cv2.waitKey(0)
	cv2.destroyAllWindows()

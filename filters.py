# -*- coding: utf-8 -*-

import numpy

def topns(matrix, n):

	flatted = matrix.flatten()

	idx_1d = numpy.argpartition(flatted, -n)[-n:]

	x_idx, y_idx = numpy.unravel_index(idx_1d, matrix.shape)

	for x, y in zip(x_idx, y_idx):

		print x, y, matrix[x][y]

		print "----------------------------"

def leven(gnodes, tnodes):

	pass

def start(matrix, gnodes, tnodes):

	numpy.set_printoptions(threshold="nan")

	print matrix

	print gnodes

	print tnodes

	print "============================" 

	topns(matrix, 3)
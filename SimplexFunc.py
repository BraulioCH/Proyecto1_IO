import numpy as np
import pandas as pd
INF = 1000000000000

def Simplex(mat, vb):

	df = pd.DataFrame(a, index=pindex, columns=pcolumns)
	print(df)

	pivotJ = 0
	pivotI = 0
	rowSize = len(mat[0])
	matSize = len(mat)

	#Encontrar columna pivote
	nmin = 0
	firstRow = mat[0]
	for j in range(0, rowSize - 1):
		if firstRow[j] < nmin:
			nmin = firstRow[j]
			pivotJ = j

	#Si ya no hay negativos
	if nmin >= 0:
		return 0

	#Encontrar fila pivote
	nmin = INF
	for i in range(1, matSize):
		if mat[i][pivotJ] > 0:
			aux = mat[i][rowSize-1] / mat[i][pivotJ]
			if aux >= 0:			#ojo el 0 vale?
				if aux < nmin:
					nmin = aux
					pivotI = i

	#Cambia el tag de la tabla
	vb[pivotI] = "x" + str(pivotJ + 1)

	#Divide Fila por pivote
	pivot = mat[pivotI][pivotJ]
	mat[pivotI] = mat[pivotI]/float(pivot)

	#Hace la columna pivote en 0s
	for i in range(0, matSize):
		if i != pivotI:
			mat[i] = mat[i] - (mat[pivotI] * mat[i][pivotJ])
	Simplex(mat,vb)


a = np.array([[-3.0, -5.0,  0.0,  0.0,  0.0,  0.0],[2.0, 1.0, 1.0, 0.0, 0.0, 6.0],[-1.0,  3.0,  0.0,  1.0,  0.0,  9.0],[0.0, 1.0, 0.0, 0.0, 1.0, 4.0]])
#a = numpy.array([[-3, -5,  0,  0,  0,  0],[2, 1, 1, 0, 0, 6],[-1,  3,  0,  1,  0,  9],[0, 1, 0, 0, 1, 4]])
print(a)
pindex = ["U","x3","x4","x5"]
pcolumns = ["x1","x2","x3","x4","x5","LD"]
Simplex(a,pindex)
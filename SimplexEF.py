import codecs
import numpy as np
import pandas as pd
np.set_printoptions(suppress=True)
import pandas as pd
INF = 1000000000000
M = 1000000
variables_desicion = 0
numero_restricciones = 0
coeficientes_funcion_objetivo = []
coeficientes_restricciones = []
signos_restricciones = []
pcolumns = []
pindex = []
mat = np.array([])
metodo_m=False

estado = 0
file = open('Log.txt', 'w')
mat = []
varBasicas = []
pivotJ =0
pivotI=0
pivot=0
esMatFinal = False
rowSize = 0
matSize = 0


def leer_archivo():
    #se referencian las variables globales para poder modificar su contenido
    global variables_desicion
    global numero_restricciones
    global coeficientes_funcion_objetivo
    global coeficientes_restricciones
    #abre el archivo con caracteres unicode
    archivo = codecs.open('problema1.txt',encoding='utf-8')
    #lee el archivo por lineas y guarda las lineas en 'contenido'
    contenido = archivo.read().splitlines()
    
    #guarda el primer elemento de 'contenido' (la primera fila)
    primera_fila = contenido[0].split(',')
    #convierte los valores de la primera fila en enteros y los guarda en las
    #variables globales
    aux = primera_fila[0]
    variables_desicion = int(aux)
    aux = primera_fila[1]
    numero_restricciones = int(aux)
    
    #guarda el primer segundo de 'contenido' (la segunda fila)
    segunda_fila = contenido[1].split(',')
    """convierte a enteros y guarda los valores de la segunda fila en una fila
    global"""
    for elementos in segunda_fila:
        coeficientes_funcion_objetivo.append(float(elementos))
    """guarda los valores de las siguientes lineas en una matriz global y
    una lista global, guarda los coeficientes como enteros y los signos de
    restricción como caracteres en su posicion respectiva en la lista segun la
    restriccion en la matriz a la que pertenece"""
    for i in range(numero_restricciones):
        fila_restricciones = contenido[2+i].split(',')
        coeficientes_restricciones.append([])
        for elementos in fila_restricciones:
            if elementos == '≤' or elementos == '=' or elementos == '≥':
                signos_restricciones.append(elementos)
            else:
                coeficientes_restricciones[i].append(float(elementos))

def writeMatrix():
	global estado
	global pivotJ
	global pivotI
	global pivot
	global esMatFinal
	global rowSize
	global matSize


	rowSize = len(mat[0])
	matSize = len(mat)
	pcolumns = []
	for i in range(0, rowSize - 1):
		pcolumns += ["x" + str(i + 1)]
	pcolumns += ["LD"]
	df = pd.DataFrame(mat, index=varBasicas, columns=pcolumns)
	if (esMatFinal):
		file.write("Estado Final\n\n")
		file.write(str(df))
		file.write("\n\n")
		file.write("Respuesta Final: U= " + str(mat[0][rowSize - 1]))
		return 0
	file.write("Estado " + str(estado) + "\n\n")
	file.write(str(df))
	file.write("\n\n")
	file.write("VB entrante: x" + str(pivotJ + 1) +", VB saliente: " + varBasicas[pivotI]+ ", Número Pivot: " + str(pivot) + "\n\n")
	return 0
	
	


#Realiza el metodo Simplex, mat es la matriz inicial, vd es un arreglo con las variables basicas [x3,x4,x5]
def Simplex():
	global estado
	global pivotJ
	global pivotI
	global pivot
	global esMatFinal
	global rowSize
	global matSize
	global varBasicas
	#Encontrar columna pivote
	nmin = 0
	firstRow = mat[0]
	for j in range(0, rowSize - 1):
		if firstRow[j] < nmin:
			nmin = firstRow[j]
			pivotJ = j

	#Si ya no hay negativos
	if nmin >= 0:
		esMatFinal = True
		writeMatrix()
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

	#Define pivot
	pivot = mat[pivotI][pivotJ]


	#Escribe en e archivo
	writeMatrix()

	
	#Cambia el tag de la tabla
	varBasicas[pivotI] = "x" + str(pivotJ + 1)

	#Divide Fila por pivote
	mat[pivotI] = mat[pivotI]/float(pivot)

	#Hace la columna pivote en 0s
	for i in range(0, matSize):
		if i != pivotI:
			mat[i] = mat[i] - (mat[pivotI] * mat[i][pivotJ])
	estado += 1
	Simplex()

def crear_variables(maximizar):
        global pindex
        pin = ["U"]
        variable = ""
        cantidad = 0
        global numero_restricciones
        global coeficientes_funcion_objetivo
        global coeficientes_restricciones
        global metodo_m
        if maximizar:
                for i in range(0,len(coeficientes_funcion_objetivo)):
                        coeficientes_funcion_objetivo[i] *= -1
        #reviza ≤
        for i in range(0,numero_restricciones):
            if(signos_restricciones[i] == '≤'):
                coeficientes_restricciones[i] = coeficientes_restricciones[i][:len(coeficientes_restricciones[i])-1] + [float(1)] \
                                                + coeficientes_restricciones[i][len(coeficientes_restricciones[i])-1:]
                coeficientes_funcion_objetivo.append(float(0))
                cantidad = len(coeficientes_restricciones[i])
                variable = "x"+str(cantidad-1)
                pin.append(variable)
                for i in range(0,numero_restricciones):
                    if(len(coeficientes_restricciones[i]) < cantidad):
                        coeficientes_restricciones[i] = coeficientes_restricciones[i][:len(coeficientes_restricciones[i])-1] + [float(0)] \
                                                        + coeficientes_restricciones[i][len(coeficientes_restricciones[i])-1:]
        #reviza =
        for i in range(0,numero_restricciones):
            if(signos_restricciones[i] == '='):
                metodo_m=True
                coeficientes_restricciones[i] = coeficientes_restricciones[i][:len(coeficientes_restricciones[i])-1] + [float(1)] \
                                                + coeficientes_restricciones[i][len(coeficientes_restricciones[i])-1:]
                coeficientes_funcion_objetivo.append(float(M))
                cantidad = len(coeficientes_restricciones[i])
                variable = "x"+str(cantidad-1)
                pin.append(variable)
                for i in range(0,numero_restricciones):
                    if(len(coeficientes_restricciones[i]) < cantidad):
                        coeficientes_restricciones[i] = coeficientes_restricciones[i][:len(coeficientes_restricciones[i])-1] + [float(0)] \
                                                        + coeficientes_restricciones[i][len(coeficientes_restricciones[i])-1:]
        #reviza ≥
        for i in range(0,numero_restricciones):
            if(signos_restricciones[i] == '≥'):
                metodo_m=True
                coeficientes_restricciones[i] = coeficientes_restricciones[i][:len(coeficientes_restricciones[i])-1] + [float(-1),float(1)] \
                                                + coeficientes_restricciones[i][len(coeficientes_restricciones[i])-1:]
                coeficientes_funcion_objetivo.append(float(0))
                coeficientes_funcion_objetivo.append(float(M))
                cantidad = len(coeficientes_restricciones[i])
                variable = "x"+str(cantidad-1)
                pin.append(variable)
                for i in range(0,numero_restricciones):
                    if(len(coeficientes_restricciones[i]) < cantidad):
                        coeficientes_restricciones[i] = coeficientes_restricciones[i][:len(coeficientes_restricciones[i])-1] + [float(0),float(0)] \
                                                        + coeficientes_restricciones[i][len(coeficientes_restricciones[i])-1:]
        coeficientes_funcion_objetivo.append(float(0))
        pindex = pin

def preparar_tabla():
    global mat
    global variables_desicion
    global numero_restricciones
    global coeficientes_funcion_objetivo
    global coeficientes_restricciones
    if metodo_m:
        for i in range(0,numero_restricciones):
            if(signos_restricciones[i] == '=' or signos_restricciones[i] == '≥'):
                for j in range(0,len(coeficientes_funcion_objetivo)):
                    coeficientes_funcion_objetivo[j] += (coeficientes_restricciones[i][j]*(-M))
    primera_tabla = []
    primera_tabla.append(coeficientes_funcion_objetivo)
    for i in range(0,numero_restricciones):
        primera_tabla.append(coeficientes_restricciones[i])
    b = np.array(primera_tabla)
    mat = b
    

def main():
    global pcolumns
    global rowSize
    global matSize
    global mat
    global varBasicas

    leer_archivo()
    crear_variables(True)
    preparar_tabla()
    for i in range(1,len(coeficientes_funcion_objetivo)-1):
        variable = "x"+str(i)
        pcolumns.append(variable)
    pcolumns.append("LD")
    varBasicas = pindex
    rowSize = len(mat[0])
    matSize = len(mat)
    Simplex()

if __name__ == "__main__":
    # execute only if run as a script
    main()
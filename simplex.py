import codecs
import pandas as pd
import getopt, sys
from fractions import Fraction

INF = 1000000000000
M = 1000000

#variabls para parseo
variables_desicion = 0
numero_restricciones = 0
coeficientes_funcion_objetivo = []
coeficientes_restricciones = []
signos_restricciones = []
multiplicadores = []
sumadores = []
valores_reales = []
indiceFila = 0
metodo_m=False


#variables para el simplex
inputfile = 0
estado = 0
file = 0
varBasicas = []
pivotJ =0
pivotI=0
pivot=0
esMatFinal = False
rowSize = 0
matSize = 0
minflag = False
maxflag = False
pcolumns = []
pindex = []
mat = []

ayuda = "El programada puede ser ejecutado de las siguientes maneras:\n"\
+"   python simplex.py --min entrada.txt -o salida.txt (para un problema de minimización)\n"\
+"   python simplex.py --max entrada.txt -o salida.txt (para un problema de maximización)\n"\
+"Donde entrada.txt y salida.txt representan ejemplos de los archivos de entrada y salida respectivamente.\n\n"\
+"Archivo de entrada:\n"\
+"Los datos del arhcivo de entrada deben segir la siguiente estructura:\n\n"\
+"Número de variables de decisión, Número de restricciones\n"\
+"Coeficientes de la función objetivo\n"\
+"Coeficientes de las restricciones y signo de restricción\n\n"\
+"Ejemplo:\n"\
+"   2,3\n"\
+"   3,5\n"\
+"   2,1,6,≤\n"\
+"   -1,3,9,=\n"\
+"   0,1,4,≥\n\n"\
+"Archivo de salida:\n"\
+"El archivo de salida se creará en la mimsa carpeta del programa una vez este sea ejecuado,"\
+" a menos que se indique una dirección específica al ingresar el nombre del archivo."


def leer_archivo():
    #se referencian las variables globales para poder modificar su contenido
    global variables_desicion
    global numero_restricciones
    global coeficientes_funcion_objetivo
    global coeficientes_restricciones
    global inputfile
    #abre el archivo con caracteres unicode
    archivo = codecs.open(inputfile,encoding='utf-8')
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

#Escribe en el archivo output y en consola
def writeMatrix():
	global estado
	global pivotJ
	global pivotI
	global pivot
	global esMatFinal
	global rowSize
	global matSize
	global mat
	global output
	global minflag
	global maxflag

	#Crea las columns para la tabla
	pcolumns = []
	for i in range(0, rowSize - 1):
		pcolumns += ["x" + str(i + 1)]
	pcolumns += ["LD"]

	#Crea la tabla para imprimir con pandas
	df = pd.DataFrame(mat, index=varBasicas, columns=pcolumns)

	#Si es la tabla final tiene que imprimir el resultado
	if (esMatFinal):
		result = []
		for x in range(1,rowSize):
			var = "x"+str(x)
			num = 0
			for y in range(1,matSize):
				if(var == varBasicas[y]):
					num = mat[y][rowSize - 1]
			result = result + [num]

		print("Estado Final\n\n")
		print(str(df))
		print("\n\n")

		file.write("Estado Final\n\n")
		file.write(str(df))
		file.write("\n\n")
		#Si es minimizar le cambia el signo a la U
		if(minflag):
		    file.write("Respuesta Final: U= " + str(-mat[0][rowSize - 1]) + " " + str(result))
		    print("Respuesta Final: U= " + str(-mat[0][rowSize - 1]) + " " + str(result))
		elif(maxflag):
		    file.write("Respuesta Final: U= " + str(mat[0][rowSize - 1]) + " " + str(result))
		    print("Respuesta Final: U= " + str(mat[0][rowSize - 1]) + " " + str(result))
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
	global multiplicadores
	global sumadores
	global valores_reales
	global indiceFila

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
	#guarda el valor real de la primera columna para reemplazarla con su expresión en M
		valores_reales = list(mat[0])
		for i in range(0,len(mat[0])):
			if(multiplicadores[i] != 0):
				#si el valor en la tabla tiene un M lo reemplaza con un string con M
				aux = (mat[0][i]-sumadores[i])/multiplicadores[i]
				if((aux==M) or (M-aux<1 and M-aux>0) or (M-aux<0 and M-aux>-1)):
					if(multiplicadores[i]!=1):
						if(sumadores[i]<0):
							mat[0][i] = str(round(multiplicadores[i],2))+"M"+str(round(sumadores[i],2))
						elif(sumadores[i]>0):
							mat[0][i] = str(round(multiplicadores[i],2))+"M+"+str(round(sumadores[i],2))
						else:
							mat[0][i] = str(round(multiplicadores[i],2))+"M"
					else:
						if(sumadores[i]<0):
							mat[0][i] = "M"+str(round(sumadores[i],2))
						elif(sumadores[i]>0):
							mat[0][i] = "M+"+str(round(sumadores[i],2))
						else:
							mat[0][i] = "M"
		writeMatrix()
		mat[0] = list(valores_reales)
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
	#guarda el valor real de la primera columna para reemplazarla con su expresión en M
	valores_reales = list(mat[0])
	for i in range(0,len(mat[0])):
		if(multiplicadores[i] != 0):
			aux = (mat[0][i]-sumadores[i])/multiplicadores[i]
			if((aux==M) or (M-aux<1 and M-aux>0) or (M-aux<0 and M-aux>-1)):
				#si el valor en la tabla tiene un M lo reemplaza con un string con M
				if(multiplicadores[i]!=1):
					if(sumadores[i]<0):
						mat[0][i] = str(round(multiplicadores[i],2))+"M"+str(round(sumadores[i],2))
					elif(sumadores[i]>0):
						mat[0][i] = str(round(multiplicadores[i],2))+"M+"+str(round(sumadores[i],2))
					else:
						mat[0][i] = str(round(multiplicadores[i],2))+"M"
				else:
					if(sumadores[i]<0):
						mat[0][i] = "M"+str(round(sumadores[i],2))
					elif(sumadores[i]>0):
						mat[0][i] = "M+"+str(round(sumadores[i],2))
					else:
						mat[0][i] = "M"
	#Escribe en el archivo
	writeMatrix()
	#regresa los valores reales a la tabla para continuar con las operaciones
	mat[0] = list(valores_reales)

	#Cambia el tag de la tabla
	varBasicas[pivotI] = "x" + str(pivotJ + 1)

	#Divide Fila por pivote
	mat[pivotI] = dividirFila(mat[pivotI],float(pivot))

	#actualiza los operadores que afectan a M en la nueva tabla
	mult = -multiplicadores[pivotJ]
	suma = -sumadores[pivotJ]
	for i in range(0, len(mat[0])):
		nuevoMult = mult*mat[pivotI][i]
		nuevoSum = suma*mat[pivotI][i]
		multiplicadores[i]+=nuevoMult
		sumadores[i]+=nuevoSum

	#Hace la columna pivote en 0s
	for i in range(0, matSize):
		if i != pivotI:
			aux = list(mat[pivotI])
			mat[i] = restarFilas(mat[i],(multiplicarFila(aux,mat[i][pivotJ])))

	estado += 1
	Simplex()

#divide los valores de una fila entre un valor
def dividirFila(fila,valor):
	for i in range(0,len(fila)):
		fila[i] = fila[i]/valor
	return fila

#multiplica los valores de una fila entre un valor
def multiplicarFila(fila,valor):
	for i in range(0,len(fila)):
		fila[i] = fila[i]*valor
	return fila

#resta dos filas
def restarFilas(fila,fila2):
	for i in range(0,len(fila)):
		fila[i] = fila[i]-fila2[i]
	return fila

#crea las variables de holgura,exeso y artificiales
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
        #reviza ≤ y agrega variables de holgura
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
        #reviza = y agrega variables artificiales
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
        #reviza ≥ y agrega variables de exeso y artificiales
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

#crea la primera tabla para la iteración 0
def preparar_tabla():
    global mat
    global variables_desicion
    global numero_restricciones
    global coeficientes_funcion_objetivo
    global coeficientes_restricciones
    global sumadores
    global multiplicadores
    global valores_reales
    #guarda los primeros valores que afectan a M
    for i in range(0,len(coeficientes_funcion_objetivo)):
    	if(coeficientes_funcion_objetivo[i] == M):
    		sumadores.append(float(0));
    		multiplicadores.append(float(1));
    	else:
    		sumadores.append(coeficientes_funcion_objetivo[i]);
    		multiplicadores.append(float(0));
    	valores_reales.append(float(0));

    #resta las restricciones multiplicadas por M a la función objetivo
    if metodo_m:
        for i in range(0,numero_restricciones):
            if(signos_restricciones[i] == '=' or signos_restricciones[i] == '≥'):
                for j in range(0,len(coeficientes_funcion_objetivo)):
                	multiplicadores[j] -= coeficientes_restricciones[i][j]
                	coeficientes_funcion_objetivo[j] += (coeficientes_restricciones[i][j]*(-M))
    #agrega todo a una matriz
    primera_tabla = []
    primera_tabla.append(coeficientes_funcion_objetivo)
    for i in range(0,numero_restricciones):
        primera_tabla.append(coeficientes_restricciones[i])
    mat = primera_tabla

def main():
    global pcolumns
    global rowSize
    global matSize
    global mat
    global varBasicas
    global minflag
    global maxflag
    global file
    global inputfile
    outputfile = 0


    #Obtener los argumentos
    try:
        opt, args = getopt.getopt(sys.argv[1:], "m:M:o:h",["max=", "min="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    for o, a in opt:
        if o == "-h":
            print(ayuda)
            return
        elif o in("-o"):
            outputfile = str(a)
        elif o in("-m", "--min"):
            minflag = True
            inputfile = str(a)
        elif o in("-M", "--max"):
            maxflag = True
            inputfile = str(a)
        else:
            assert False, "La opcion escogida no existe"

    file = open(outputfile, 'w')
    leer_archivo()
    crear_variables(maxflag)
    preparar_tabla()

    #Crea las columnas de la tabla
    for i in range(1,len(coeficientes_funcion_objetivo)-1):
        variable = "x"+str(i)
        pcolumns.append(variable)
    pcolumns.append("LD")

    #Obtiene las variables básicas de la tabla
    varBasicas = pindex
    rowSize = len(mat[0])
    matSize = len(mat)

    #Inicia Simplex
    Simplex()

if __name__ == "__main__":
    # execute only if run as a script
    main()

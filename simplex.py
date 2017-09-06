# -*- coding: utf-8 -*-
import codecs

variables_desicion = 0
numero_restricciones = 0
coeficientes_funcion_objetivo = []
coeficientes_restricciones = []
signos_restricciones = []

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
        coeficientes_funcion_objetivo.append(int(elementos))
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
                coeficientes_restricciones[i].append(int(elementos))

def main():
    leer_archivo()
    print(variables_desicion)
    print(numero_restricciones)
    print(coeficientes_funcion_objetivo)
    print(coeficientes_restricciones)
    print(signos_restricciones)

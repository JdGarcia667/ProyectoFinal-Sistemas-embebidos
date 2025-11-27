import vlc
import pygame
import sys
import threading
import os

import tkinter
#from MenuConexiones import MenuConexiones
from MediosExtraibles import MenuMediosExtraibles
from ServiciosStreaming import ServiciosStreaming
from MusicaStreaming import MusicaStreaming
from WifiScanner import WifiScanner
from time import sleep

# Configuración modo kiosko
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centrar ventana
pygame.init()


# Inicializa pygame
pygame.init()
sleep(1)

#Creamos un hilo para los medios extraibles
menu = MenuMediosExtraibles()
streaming = ServiciosStreaming()
musica = MusicaStreaming() 
red = WifiScanner()
#red = MenuConexiones()


# Configura el tamaño de la ventana y los colores
COLOR_FONDO = (0, 0, 0)  # Negro
COLOR_TEXTO = (0, 0, 0)  # Blanco
COLOR_SELECCION = (255, 64, 0)  # Rojo para resaltar la opción seleccionada
COLOR_OPCIONES= (255, 64, 0) #Gris para la interaccion


# Configura la ventana de pygame
pantalla = pygame.display.set_mode((0, 0),pygame.RESIZABLE)
ancho_ventana, largo_ventana = pantalla.get_size()
pygame.display.set_caption("Centro de Entretenimiento")

fuente = pygame.font.SysFont("Arial", 60)
fuente2 = pygame.font.SysFont("Arial",30)

# Lista de opciones del menú
opciones = ["STREAMING", "MÚSICA", "DISPOSITIVOS", "WIFI", "SALIR"]
indice_opcion = 0  # Para rastrear qué opción está seleccionada
fondo=pygame.image.load('images/fondo.jpg')
icon_streaming=pygame.image.load('images/streaming.png')
icon_music=pygame.image.load('images/music2.png')
icon_usb=pygame.image.load('images/usb.png')
icon_wifi=pygame.image.load('images/wifi3.png')

# Configurar para evitar que se cierre accidentalmente
def manejar_salida_segura():
    """Maneja la salida del programa de forma segura"""
    # Aquí puedes agregar un diálogo de confirmación si quieres
    # o simplemente ignorar ciertas teclas
    pass

def dibujar_menu():
    #Función para establecer el fondo de la ventana
    def Background_sky(fondo):
      size=pygame.transform.scale(fondo,(2048,1500))
      pantalla.blit(size, (0,0))
    #pantalla.fill(COLOR_FONDO)
    textoFlechas = fuente.render("↑↓ - Moverse entre las opciones", True, COLOR_OPCIONES)
    pantalla.blit(textoFlechas,(100,400))
    textoSeleccion = fuente.render("ENTER - Seleccionar opcion", True, COLOR_OPCIONES)
    pantalla.blit(textoSeleccion,(100,450))
    y = 100  # Posición inicial vertical para las opciones
    #Background_sky(fondo) #Dibuja el fondo en la ventana
    Background_sky(fondo)
    #pantalla.fill(COLOR_FONDO)
    textoFlechas = fuente2.render("↑↓ - Moverse entre las opciones", True, COLOR_OPCIONES)
    pantalla.blit(textoFlechas,(100,960))
    textoSeleccion = fuente2.render("ENTER - Seleccionar opcion", True, COLOR_OPCIONES)
    pantalla.blit(textoSeleccion,(100,1000))
    pantalla.blit(icon_streaming,(1100,15))
    pantalla.blit(icon_music, (1100,195))
    pantalla.blit(icon_usb,(1100,375))
    pantalla.blit(icon_wifi, (1100,555))
    #x=30
    y = 30  # Posición inicial vertical para las opciones
    # Dibuja cada opción
    for i, opcion in enumerate(opciones):
        if i == indice_opcion:
            texto = fuente.render(opcion, True, COLOR_SELECCION)  # Opción seleccionada en naranja
        else:
            texto = fuente.render(opcion, True, COLOR_TEXTO)  # Otras opciones en blanco
        #pantalla.blit(texto, (100, y))
        #y += 50  # Espaciado entre opciones
        pantalla.blit(texto, (600, y))
        y += 180  # Espaciado entre opciones
        #x += 30
        
    pygame.display.flip()  # Actualiza la pantalla

def manejar_eventos():
    global indice_opcion, ejecutando
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            # Ignorar cierre de ventana
            continue
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_DOWN:
                indice_opcion = (indice_opcion + 1) % len(opciones)
            elif evento.key == pygame.K_UP:
                indice_opcion = (indice_opcion - 1) % len(opciones)
            elif evento.key == pygame.K_RETURN:
                ejecutar_opcion(indice_opcion)
            elif evento.key == pygame.K_ESCAPE:
                # Opcional: agregar confirmación para salir
                # ejecutando = False
                pass
            elif evento.key == pygame.K_F4 and (pygame.key.get_mods() & pygame.KMOD_ALT):
                # Bloquear Alt+F4
                pass

def mostrar_texto(self, texto, x, y, color=None):
    if color is None:
        color = self.NEGRO
    superficie_texto = self.fuente.render(texto, True, color)
    self.pantalla.blit(superficie_texto, (x, y))

def ejecutar_opcion(indice):
    if indice == 0:
        print("Seleccionado: STREAMING")
        # Llama a la función para manejar servicios de video en línea
        streaming.iniciar_menu()
    elif indice == 1:
        print("Seleccionado: MUSICA")
        # Llama a la función para manejar servicios de música en línea
        musica.iniciar_menu()
    elif indice == 2:
        print("Seleccionado: DISPOSITIVOS")
        menu.iniciar_menu()
    elif indice == 3:
        print("Seleccionado: WIFI")
        red.iniciar_menu()
        
    elif indice == 4:
        print("Saliendo...")
        pygame.quit()
        #os.system("shutdown now")

# Bucle principal
ejecutando = True
while ejecutando:
    manejar_eventos()  # Maneja los eventos de teclado
    dibujar_menu()  # Dibuja el menú en la pantalla


import pyudev
import os
import pygame
import sys

class MenuMediosExtraibles:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.alto_ventana, self.largo_ventana = self.pantalla.get_size()
        pygame.display.set_caption("Menú de Medios Extraíbles")

        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.GRIS = (200, 200, 200)
        self.AZUL_CLARO = (255, 128, 0)

        self.fuente = pygame.font.SysFont("Arial", 60)
        self.opciones = ["Reproducir Videos", "Reproducir Música", "Ver Fotos en Bucle", "Salir"]
        self.opcion_seleccionada = 0
        self.ejecutando = False
        fondo4=pygame.image.load('images/fondo.jpg')

    def mostrar_texto(self, texto, x, y, color=None):
        if color is None:
            color = self.NEGRO
        superficie_texto = self.fuente.render(texto, True, color)
        self.pantalla.blit(superficie_texto, (x, y))

    def iniciar_menu(self):
        self.ejecutando = True
        #fondo4=pygame.image.load('images/fondo.jpg')

        def Background_mediosExtraibles(fondo4):
            size=pygame.transform.scale(fondo4,(2048,1500))
            self.pantalla.blit(size,(0,0))

        while self.ejecutando:
            #self.pantalla.fill(self.BLANCO)
            Background_mediosExtraibles(fondo4)
            self.mostrar_texto("Selecciona una opción:", 50, 50)

            y_offset = 150
            for indice, texto in enumerate(self.opciones):
                color = self.AZUL_CLARO if indice == self.opcion_seleccionada else self.NEGRO
                self.mostrar_texto(texto, 60, y_offset, color)
                y_offset += 100
            self.mostrar_texto("ESC - Volver al menú principal", 50, self.alto_ventana - 60, self.GRIS)
            self.mostrar_texto("ENTER - Seleccionar opcion", 50,self.alto_ventana-30,self.GRIS)
            self.mostrar_texto("↑↓ - Moverse entre las opciones", 50, self.alto_ventana-90, self.GRIS)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_DOWN:
                        self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
                    elif evento.key == pygame.K_UP:
                        self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
                    elif evento.key == pygame.K_RETURN:
                        if self.opciones[self.opcion_seleccionada] == "Reproducir Videos":
                            print("Reproduciendo videos...")
                        elif self.opciones[self.opcion_seleccionada] == "Reproducir Música":
                            print("Reproduciendo música...")
                        elif self.opciones[self.opcion_seleccionada] == "Ver Fotos en Bucle":
                            print("Mostrando fotos en bucle...")
                        elif self.opciones[self.opcion_seleccionada] == "Salir":
                            self.ejecutando = False

            pygame.display.flip()

    def detener_menu(self):
        self.ejecutando = False
        pygame.quit()

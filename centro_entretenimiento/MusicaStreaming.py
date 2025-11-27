import pygame
import sys
import subprocess
from time import sleep
class MusicaStreaming:
    def __init__(self):
        pygame.init()
        sleep(1)
        self.pantalla=pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.ancho_ventana, self.largo_ventana=self.pantalla.get_size()
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.GRIS = (200, 200, 200)
        self.AZUL_CLARO =(255,64,0) # (173, 216, 230)
        self.fuente = pygame.font.SysFont("Arial", 60)
        self.opciones = ["SPOTIFY", "DEEZER", "AMAZON MUSIC", "VOLVER"]
        self.opcion_seleccionada = 0
        self.ejecutando = False
        self.urls = {
            "SPOTIFY": "https://open.spotify.com/intl-es",
            "DEEZER": "https://www.deezer.com/mx/",
            "AMAZON MUSIC": "https://music.amazon.com.mx/"
        }

    def mostrar_texto(self, texto, x, y, color=None):
        if color is None:
            color = self.NEGRO
        superficie_texto = self.fuente.render(texto, True, color)
        self.pantalla.blit(superficie_texto, (x, y))
    def open_service(self, service_name):
      if service_name in self.urls:
          url=self.urls[service_name]
          subprocess.Popen(["chromium", "--kiosk", "--disable-infobars","--disable-notifications","--disable-save-password-bubble",
                            "--disable-popup-blocking","--no-first-run","--no-default-browser-check" "--disable-gpu",
                            "--start-fullscreen","--no-sandbox",f"--user-data-dir=/tmp/chromium-{service_name}", url])
      
    def iniciar_menu(self):
      self.ejecutando = True
      fondo3=pygame.image.load('images/fondo.jpg')
      icon_spotify=pygame.image.load('images/spotify.png')
      icon_deezer=pygame.image.load('images/deezer.jpg')
      icon_amazonmusic=pygame.image.load('images/amazonmusic.jpg')

      def Background_musicaStreaming(fondo3):
          size=pygame.transform.scale(fondo3,(2048,1500))
          self.pantalla.blit(size,(0,0))



      while self.ejecutando:
          #self.pantalla.fill(self.BLANCO)
          Background_musicaStreaming(fondo3)
          self.mostrar_texto("Selecciona una opción:", 50, 50)

          self.pantalla.blit(icon_spotify,(1200,200))
          self.pantalla.blit(icon_deezer,(1200,400))
          self.pantalla.blit(icon_amazonmusic,(1200,600))
        
          y_offset = 250
          for indice, texto in enumerate(self.opciones):
              color = self.AZUL_CLARO if indice == self.opcion_seleccionada else self.NEGRO
              self.mostrar_texto(texto, 600, y_offset, color)
              y_offset += 200

          self.mostrar_texto("ESC - Volver al menú principal", 50, self.ancho_ventana - 60, self.GRIS)
          self.mostrar_texto("ENTER - Seleccionar opción", 50, self.ancho_ventana - 30, self.GRIS)
          self.mostrar_texto("↑↓ - Moverse entre las opciones", 50, self.ancho_ventana - 90, self.GRIS)
        
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
                      if self.opciones[self.opcion_seleccionada] == "SPOTIFY":
                          self.open_service(self.opciones[self.opcion_seleccionada])
                      elif self.opciones[self.opcion_seleccionada] == "DEEZER":
                          self.open_service(self.opciones[self.opcion_seleccionada])
                      elif self.opciones[self.opcion_seleccionada] == "AMAZON MUSIC":
                          self.open_service(self.opciones[self.opcion_seleccionada])
                      elif self.opciones[self.opcion_seleccionada] == "VOLVER":
                          self.ejecutando = False
                  elif evento.key == pygame.K_ESCAPE:
                      self.ejecutando = False  # Agregar acción para el ESC
        
          pygame.display.flip()
                
    def detener_menu(self):
        self.ejecutando = False
        pygame.quit()

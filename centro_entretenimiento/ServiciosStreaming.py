import pygame
import sys
import subprocess
import os
import shutil
from time import sleep

class ServiciosStreaming:
    def __init__(self):
        pygame.init()
        sleep(1)
        self.pantalla = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.ancho_ventana, self.largo_ventana = self.pantalla.get_size()
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.GRIS = (200, 200, 200)
        self.AZUL_CLARO = (255,64,0)
        self.fuente = pygame.font.SysFont("Arial", 60)
        self.opciones = ["NETFLIX", "AMAZON PRIME", "HBO MAX", "VOLVER"]
        self.opcion_seleccionada = 0
        self.ejecutando = False
        self.urls = {
            "NETFLIX": "https://www.netflix.com/",
            "AMAZON PRIME": "https://www.primevideo.com/",
            "HBO MAX": "https://www.hbomax.com/"
        }
        self.navegador = self.detectar_navegador()
    
    def detectar_navegador(self):
        """Detecta automáticamente qué navegador está disponible"""
        navegadores = [
            "chromium",           # Nombre moderno
            "chromium-browser",   # Nombre tradicional
            "firefox",            # Firefox normal
            "firefox-esr",        # Firefox ESR
            "midori",             # Midori ligero
            "epiphany",           # Epiphany
            "falkon"              # Falkon
        ]
        
        for nav in navegadores:
            if shutil.which(nav):
                print(f"✅ Navegador detectado: {nav}")
                return nav
        
        print("❌ No se encontró ningún navegador instalado")
        return None
    
    def open_service(self, service_name):
        if service_name in self.urls:
            url = self.urls[service_name]
            
            if not self.navegador:
                self.mostrar_error_navegador()
                return
            
            try:
                if self.navegador in ["chromium", "chromium-browser"]:
                    subprocess.Popen([
                        self.navegador, 
                        "--kiosk",
                        "--disable-infobars",
                        "--disable-notifications",
                        "--no-first-run",
                        "--no-default-browser-check",
                        url
                    ])
                elif self.navegador in ["firefox", "firefox-esr"]:
                    subprocess.Popen([
                        self.navegador,
                        "--kiosk",
                        url
                    ])
                elif self.navegador == "midori":
                    subprocess.Popen([
                        self.navegador,
                        "-e", "Fullscreen",
                        "-a", url
                    ])
                else:
                    # Para otros navegadores, abrir normalmente
                    subprocess.Popen([self.navegador, url])
                    
                print(f"🌐 Abriendo {service_name} con {self.navegador}")
                
            except Exception as e:
                print(f"❌ Error al abrir {service_name}: {e}")
                self.mostrar_error_apertura(str(e))
    
    def mostrar_error_navegador(self):
        """Muestra mensaje de error cuando no hay navegador"""
        print("""
        ❌ ERROR: No hay navegador web instalado
        
        Soluciones:
        1. Instalar Firefox: sudo apt install firefox-esr
        2. Instalar Chromium: sudo apt install chromium
        3. Instalar Midori: sudo apt install midori
        """)
    
    def mostrar_error_apertura(self, error):
        """Muestra mensaje de error en Pygame"""
        fondo = pygame.Surface((self.ancho_ventana, self.largo_ventana))
        fondo.fill((50, 0, 0))  # Fondo rojo oscuro
        
        self.pantalla.blit(fondo, (0, 0))
        
        mensajes = [
            "Error al abrir navegador",
            f"Detalle: {error}",
            "",
            "Presiona cualquier tecla para continuar"
        ]
        
        y = 200
        for mensaje in mensajes:
            texto = self.fuente.render(mensaje, True, self.BLANCO)
            self.pantalla.blit(texto, (100, y))
            y += 80
        
        pygame.display.flip()
        
        # Esperar a que presione una tecla
        esperando = True
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN:
                    esperando = False
                elif evento.type == pygame.QUIT:
                    esperando = False
    
    # ... el resto de tu código permanece igual ...
    def mostrar_texto(self, texto, x, y, color=None):
        if color is None:
            color = self.NEGRO
        superficie_texto = self.fuente.render(texto, True, color)
        self.pantalla.blit(superficie_texto, (x, y))
    
    def iniciar_menu(self):
        self.ejecutando = True
        fondo2 = pygame.image.load('images/fondo.jpg')
        icon_netflix = pygame.image.load('images/netflix.jpg')
        icon_primevideo = pygame.image.load('images/primevideo.jpg')
        icon_max = pygame.image.load('images/max.jpg')

        def Background_videoStreaming(fondo2):
            size = pygame.transform.scale(fondo2, (2048, 1500))
            self.pantalla.blit(size, (0, 0))

        while self.ejecutando:
            Background_videoStreaming(fondo2)
            self.mostrar_texto("Selecciona una opción:", 50, 50)

            self.pantalla.blit(icon_netflix, (1200, 200))
            self.pantalla.blit(icon_primevideo, (1200, 400))
            self.pantalla.blit(icon_max, (1200, 600))

            y_offset = 250
            for indice, texto in enumerate(self.opciones):
                color = self.AZUL_CLARO if indice == self.opcion_seleccionada else self.NEGRO
                self.mostrar_texto(texto, 600, y_offset, color)
                y_offset += 200

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
                        if self.opciones[self.opcion_seleccionada] == "VOLVER":
                            self.ejecutando = False
                        else:
                            self.open_service(self.opciones[self.opcion_seleccionada])
                    elif evento.key == pygame.K_ESCAPE:
                        self.ejecutando = False

            pygame.display.flip()
    
    def detener_menu(self):
        self.ejecutando = False
        pygame.quit()

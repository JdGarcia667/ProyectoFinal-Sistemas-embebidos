import pyudev
import os
import pygame
import sys
import glob
import subprocess
import threading
import time
from time import sleep

class MenuMediosExtraibles:
    def __init__(self):
        pygame.init()
        self.contexto = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.contexto)
        self.monitor.filter_by(subsystem='block', device_type='partition')
        
        # Rutas donde Raspberry Pi monta automáticamente los USB
        self.rutas_montaje_auto = [
            "/media/pi/*",
            "/media/*/*", 
            "/run/media/pi/*",
            "/mnt/*"
        ]
        
        self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.ancho_ventana, self.alto_ventana = self.pantalla.get_size()
        pygame.display.set_caption("Menú de Medios Extraíbles")

        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.GRIS = (200, 200, 200)
        self.AZUL_CLARO = (255, 64, 0)
        self.VERDE = (0, 255, 0)
        self.ROJO = (255, 0, 0)

        self.fuente = pygame.font.SysFont("Arial", 60)
        self.fuente_mediana = pygame.font.SysFont("Arial", 40)
        self.fuente_pequena = pygame.font.SysFont("Arial", 24)
        
        self.opciones = ["VIDEOS", "MÚSICA", "FOTOS", "VOLVER"]
        self.opcion_seleccionada = 0
        self.ejecutando = False
        
        # Estados para mensajes
        self.mensaje_usb = None
        self.tiempo_mensaje = 0
        self.usb_conectado = False
        self.contenido_detectado = []
        self.ruta_usb_actual = None
        
        # Control de reproducción
        self.reproduciendo = False
        self.proceso_vlc = None
        self.hilo_reproduccion = None

    def buscar_usb_montados(self):
        """Busca dispositivos USB montados automáticamente por el sistema"""
        dispositivos_encontrados = []
        
        for patron_ruta in self.rutas_montaje_auto:
            try:
                rutas = glob.glob(patron_ruta)
                for ruta in rutas:
                    if os.path.isdir(ruta) and os.path.ismount(ruta):
                        if self.es_dispositivo_usb(ruta):
                            dispositivos_encontrados.append(ruta)
            except Exception as e:
                print(f"Error buscando en {patron_ruta}: {e}")
        
        return dispositivos_encontrados

    def es_dispositivo_usb(self, ruta):
        """Verifica si la ruta corresponde a un dispositivo USB"""
        try:
            contenido = os.listdir(ruta)
            return len(contenido) > 0
        except:
            return False

    def detectar_usb_automatico(self):
        """Detecta si hay USBs montados automáticamente"""
        dispositivos = self.buscar_usb_montados()
        
        if dispositivos:
            self.ruta_usb_actual = dispositivos[0]
            self.usb_conectado = True
            self.contenido_detectado = self.analizar_contenido_general(self.ruta_usb_actual)
            
            mensaje = f"✓ USB DETECTADO: {os.path.basename(self.ruta_usb_actual)} - {len(self.contenido_detectado)} archivos"
            self.mostrar_mensaje_temporal(mensaje, self.VERDE, 4)
            return True
        else:
            self.usb_conectado = False
            self.ruta_usb_actual = None
            self.contenido_detectado = []
            return False

    def manejar_evento_dispositivo(self, action, device):
        """Maneja la conexión/desconexión de dispositivos USB"""
        if action == 'add':
            print(f"Dispositivo conectado: {device.device_node}")
            sleep(2)
            self.detectar_usb_automatico()
                
        elif action == 'remove':
            print(f"Dispositivo desconectado: {device.device_node}")
            self.usb_conectado = False
            self.ruta_usb_actual = None
            self.contenido_detectado = []
            self.mostrar_mensaje_temporal("USB DESCONECTADO", self.ROJO, 2)

    def mostrar_texto(self, texto, x, y, color=None, fuente=None):
        if color is None:
            color = self.NEGRO
        if fuente is None:
            fuente = self.fuente
            
        superficie_texto = fuente.render(texto, True, color)
        self.pantalla.blit(superficie_texto, (x, y))

    def mostrar_mensaje_temporal(self, mensaje, color=None, duracion=3):
        """Muestra un mensaje temporal en pantalla"""
        self.mensaje_usb = mensaje
        self.tiempo_mensaje = pygame.time.get_ticks()
        self.color_mensaje = color if color else self.VERDE
        self.duracion_mensaje = duracion * 1000

    def dibujar_mensaje_usb(self):
        """Dibuja el mensaje de estado del USB si existe"""
        if self.mensaje_usb and (pygame.time.get_ticks() - self.tiempo_mensaje) < self.duracion_mensaje:
            mensaje_surface = pygame.Surface((self.ancho_ventana - 100, 80))
            mensaje_surface.fill((0, 0, 0))
            mensaje_surface.set_alpha(200)
            
            x_pos = 50
            y_pos = 100
            
            self.pantalla.blit(mensaje_surface, (x_pos, y_pos))
            pygame.draw.rect(self.pantalla, self.color_mensaje, (x_pos, y_pos, self.ancho_ventana - 100, 80), 3)
            
            texto = self.fuente_mediana.render(self.mensaje_usb, True, self.BLANCO)
            texto_x = x_pos + (self.ancho_ventana - 100 - texto.get_width()) // 2
            texto_y = y_pos + (80 - texto.get_height()) // 2
            self.pantalla.blit(texto, (texto_x, texto_y))

    def dibujar_estado_usb(self):
        """Dibuja el estado actual del USB en la esquina superior derecha"""
        if self.usb_conectado and self.ruta_usb_actual:
            nombre_usb = os.path.basename(self.ruta_usb_actual)
            estado_texto = f"USB: {nombre_usb}"
            color = self.VERDE
            
            if self.contenido_detectado:
                info_texto = f"Archivos: {len(self.contenido_detectado)}"
                self.mostrar_texto(info_texto, self.ancho_ventana - 300, 160, self.BLANCO, self.fuente_pequena)
        else:
            estado_texto = "INSERTE USB"
            color = self.ROJO
            
        self.mostrar_texto(estado_texto, self.ancho_ventana - 400, 100, color, self.fuente_mediana)

    def analizar_contenido_general(self, ruta_montaje):
        """Analiza y cuenta todo el contenido del USB"""
        if not os.path.exists(ruta_montaje):
            return []
            
        extensiones_todas = [
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
            '.mp3', '.wav', '.ogg', '.m4a', '.flac',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp'
        ]
        
        archivos_encontrados = []
        try:
            for root, dirs, files in os.walk(ruta_montaje):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensiones_todas):
                        archivos_encontrados.append(os.path.join(root, file))
        except Exception as e:
            print(f"Error analizando contenido: {e}")
            
        return archivos_encontrados

    def analizar_contenido_images(self, ruta_montaje):
        extensiones_imagen = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        image_files = []
        try:
            for root, dirs, files in os.walk(ruta_montaje):
                for file in files:
                    if file.lower().endswith(extensiones_imagen):
                        ruta_completa = os.path.join(root, file)
                        if os.path.isfile(ruta_completa):
                            image_files.append(ruta_completa)
        except Exception as e:
            print(f"Error al buscar imágenes: {str(e)}")

        if not image_files:
            self.mostrar_mensaje_temporal("No se encontraron imágenes", self.ROJO, 2)
            return []

        return image_files

    def analizar_contenido_videos(self, ruta_montaje):
        extensiones_video = ('.mp4', '.avi', '.mkv', '.mov', '.wmv','.flv')
        video_files = []
        try:
            for root, dirs, files in os.walk(ruta_montaje):
                for file in files:
                    if file.lower().endswith(extensiones_video):
                        ruta_completa = os.path.join(root, file)
                        if os.path.isfile(ruta_completa):
                            video_files.append(ruta_completa)
        except Exception as e:
            print(f"Error al buscar videos: {str(e)}")

        if not video_files:
            self.mostrar_mensaje_temporal("No se encontraron videos", self.ROJO, 2)
            return []

        return video_files

    def analizar_contenido_musica(self, ruta_montaje):
        extensiones_musica = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')
        music_files = []
        try:
            for root, dirs, files in os.walk(ruta_montaje):
                for file in files:
                    if file.lower().endswith(extensiones_musica):
                        ruta_completa = os.path.join(root, file)
                        if os.path.isfile(ruta_completa):
                            music_files.append(ruta_completa)
        except Exception as e:
            print(f"Error al buscar música: {str(e)}")

        if not music_files:
            self.mostrar_mensaje_temporal("No se encontró música", self.ROJO, 2)
            return []

        return music_files

    def reproducir_videos_vlc(self, video_files):
        """Reproduce videos con VLC en un hilo separado"""
        def reproducir():
            try:
                video_files.sort()
                
                # Configuración de VLC para permitir control
                vlc_params = [
                    "vlc",
                    "--fullscreen",
                    "--no-osd",
                    "--no-video-title-show",
                    "--mouse-hide-timeout=0",
                    "--key-quit=Esc"  # Mapear ESC para salir
                ]
                
                # Agregar archivos de video
                vlc_params.extend(video_files)
                
                # Matar cualquier instancia previa de VLC
                os.system("pkill vlc 2>/dev/null")
                sleep(1)
                
                print("Iniciando VLC con archivos:", video_files)
                self.proceso_vlc = subprocess.Popen(
                    vlc_params,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Esperar a que el proceso termine
                self.proceso_vlc.wait()
                
            except Exception as e:
                print(f"Error al reproducir videos: {e}")
            finally:
                self.reproduciendo = False
                self.proceso_vlc = None

        self.reproduciendo = True
        self.hilo_reproduccion = threading.Thread(target=reproducir)
        self.hilo_reproduccion.daemon = True
        self.hilo_reproduccion.start()
        
        # Mostrar mensaje de control
        self.mostrar_mensaje_temporal("Reproduciendo videos... Presiona ESC en VLC para volver", self.VERDE, 5)

    def reproducir_musica_vlc(self, music_files):
        """Reproduce música con VLC en un hilo separado"""
        def reproducir():
            try:
                music_files.sort()
                
                vlc_params = [
                    "cvlc",  # VLC sin interfaz
                    "--no-video",
                    "--no-osd",
                    "--mouse-hide-timeout=0",
                    "--key-quit=Esc"
                ]
                
                vlc_params.extend(music_files)
                
                os.system("pkill vlc 2>/dev/null")
                sleep(1)
                
                print("Iniciando VLC para música con archivos:", music_files)
                self.proceso_vlc = subprocess.Popen(
                    vlc_params,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                self.proceso_vlc.wait()
                
            except Exception as e:
                print(f"Error al reproducir música: {e}")
            finally:
                self.reproduciendo = False
                self.proceso_vlc = None

        self.reproduciendo = True
        self.hilo_reproduccion = threading.Thread(target=reproducir)
        self.hilo_reproduccion.daemon = True
        self.hilo_reproduccion.start()
        
        self.mostrar_mensaje_temporal("Reproduciendo música... Presiona ESC en VLC para volver", self.VERDE, 5)

    def reproducir_imagenes_slideshow(self, image_files):
        """Reproduce imágenes como slideshow con pygame"""
        if not image_files:
            return
            
        image_files.sort()
        index_actual = 0
        corriendo = True
        
        clock = pygame.time.Clock()
        
        while corriendo and index_actual < len(image_files):
            try:
                # Cargar y mostrar imagen
                imagen = pygame.image.load(image_files[index_actual])
                imagen = pygame.transform.scale(imagen, (self.ancho_ventana, self.alto_ventana))
                self.pantalla.blit(imagen, (0, 0))
                
                # Mostrar controles
                self.mostrar_texto(f"Imagen {index_actual + 1}/{len(image_files)}", 50, 50, self.BLANCO, self.fuente_mediana)
                self.mostrar_texto("ESC: Salir  →: Siguiente  ←: Anterior", 50, 120, self.BLANCO, self.fuente_pequena)
                
                pygame.display.flip()
                
                # Esperar 5 segundos o hasta que presione tecla
                start_time = pygame.time.get_ticks()
                esperando = True
                
                while esperando:
                    tiempo_actual = pygame.time.get_ticks()
                    if tiempo_actual - start_time > 5000:  # 5 segundos por imagen
                        esperando = False
                    
                    for evento in pygame.event.get():
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_ESCAPE:
                                corriendo = False
                                esperando = False
                            elif evento.key == pygame.K_RIGHT:
                                esperando = False  # Siguiente imagen
                            elif evento.key == pygame.K_LEFT:
                                index_actual = max(0, index_actual - 2)  # Imagen anterior
                                esperando = False
                            elif evento.key == pygame.K_SPACE:
                                esperando = False  # También espacio para siguiente
                    
                    clock.tick(30)
                
                index_actual += 1
                
            except Exception as e:
                print(f"Error cargando imagen: {e}")
                index_actual += 1
                continue

    def detener_reproduccion(self):
        """Detiene cualquier reproducción en curso"""
        try:
            if self.proceso_vlc:
                self.proceso_vlc.terminate()
                self.proceso_vlc = None
            os.system("pkill vlc 2>/dev/null")
            self.reproduciendo = False
            print("Reproducción detenida")
        except Exception as e:
            print(f"Error al detener reproducción: {e}")

    def verificar_reproduccion(self):
        """Verifica si la reproducción sigue activa"""
        if self.proceso_vlc and self.proceso_vlc.poll() is not None:
            self.reproduciendo = False
            self.proceso_vlc = None

    def iniciar_menu(self):
        self.ejecutando = True
        
        # INICIAR EL OBSERVER
        observer = pyudev.MonitorObserver(self.monitor, self.manejar_evento_dispositivo)
        observer.start()
        
        # Buscar USBs ya conectados al iniciar
        self.detectar_usb_automatico()
        
        # Cargar recursos
        try:
            fondo = pygame.image.load('images/fondo.jpg')
            icon_videos = pygame.image.load('images/videos.png')
            icon_musica = pygame.image.load('images/music3.png')
            icon_fotos = pygame.image.load('images/fotos.jpg')
        except:
            fondo = pygame.Surface((self.ancho_ventana, self.alto_ventana))
            fondo.fill((50, 50, 50))
            icon_videos = icon_musica = icon_fotos = None

        def dibujar_fondo():
            size = pygame.transform.scale(fondo, (self.ancho_ventana, self.alto_ventana))
            self.pantalla.blit(size, (0, 0))

        while self.ejecutando:
            dibujar_fondo()
            
            # Título
            self.mostrar_texto("MEDIOS EXTRAÍBLES", 50, 50)
            
            # Dibujar estado del USB
            self.dibujar_estado_usb()
            self.dibujar_mensaje_usb()
            
            # Iconos
            if icon_videos:
                self.pantalla.blit(icon_videos, (1200, 200))
                self.pantalla.blit(icon_musica, (1200, 400))
                self.pantalla.blit(icon_fotos, (1200, 600))

            # Opciones del menú
            y_offset = 250
            for indice, texto in enumerate(self.opciones):
                color = self.AZUL_CLARO if indice == self.opcion_seleccionada else self.BLANCO
                self.mostrar_texto(texto, 600, y_offset, color)
                y_offset += 200
            
            # Instrucciones
            instrucciones = [
                "ESC - Volver al menú principal",
                "ENTER - Seleccionar opción", 
                "↑↓ - Moverse entre opciones"
            ]
            
            y_inst = self.alto_ventana - 90
            for instruccion in instrucciones:
                self.mostrar_texto(instruccion, 50, y_inst, self.GRIS, self.fuente_pequena)
                y_inst += 30

            # Verificar si la reproducción terminó
            self.verificar_reproduccion()

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
                        if self.opciones[self.opcion_seleccionada] == "VIDEOS":
                            if self.usb_conectado and self.ruta_usb_actual:
                                videos = self.analizar_contenido_videos(self.ruta_usb_actual)
                                if videos:
                                    self.reproducir_videos_vlc(videos)
                            else:
                                self.mostrar_mensaje_temporal("Primero inserte un USB", self.ROJO, 2)
                        elif self.opciones[self.opcion_seleccionada] == "MÚSICA":
                            if self.usb_conectado and self.ruta_usb_actual:
                                musica = self.analizar_contenido_musica(self.ruta_usb_actual)
                                if musica:
                                    self.reproducir_musica_vlc(musica)
                            else:
                                self.mostrar_mensaje_temporal("Primero inserte un USB", self.ROJO, 2)
                        elif self.opciones[self.opcion_seleccionada] == "FOTOS":
                            if self.usb_conectado and self.ruta_usb_actual:
                                imagenes = self.analizar_contenido_images(self.ruta_usb_actual)
                                if imagenes:
                                    self.reproducir_imagenes_slideshow(imagenes)
                            else:
                                self.mostrar_mensaje_temporal("Primero inserte un USB", self.ROJO, 2)
                        elif self.opciones[self.opcion_seleccionada] == "VOLVER":
                            self.ejecutando = False
                    elif evento.key == pygame.K_ESCAPE:
                        # Detener reproducción si está activa
                        if self.reproduciendo:
                            self.detener_reproduccion()
                        else:
                            self.ejecutando = False

            pygame.display.flip()

    def detener_menu(self):
        self.detener_reproduccion()
        self.ejecutando = False
        pygame.quit()

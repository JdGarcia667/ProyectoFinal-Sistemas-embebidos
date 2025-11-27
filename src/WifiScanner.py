import pygame
import subprocess
import re
import time
import os
import sys
from time import sleep

class WifiScanner:
    def __init__(self):
        pygame.init()
        sleep(1)
        self.pantalla = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.ancho_ventana, self.largo_ventana = self.pantalla.get_size()
        
        # Colores
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.GRIS = (200, 200, 200)
        self.AZUL_CLARO = (0, 100, 255)
        self.ROJO = (255, 50, 50)
        self.VERDE = (50, 200, 50)
        
        # Fuentes
        self.fuente = pygame.font.SysFont("Arial", 30)
        self.fuente_pequena = pygame.font.SysFont("Arial", 20)
        
        # Estado de la aplicación
        self.networks = []
        self.red_seleccionada = None
        self.scroll_offset = 0
        self.password_input = ""
        self.modo_password = False
        self.mensaje = ""
        self.mensaje_timer = 0
        self.ejecutando = False
        
        # Botones
        self.boton_escanear = pygame.Rect(20, 20, 150, 40)
        self.boton_conectar = pygame.Rect(190, 20, 150, 40)
        self.boton_volver = pygame.Rect(self.ancho_ventana - 170, 20, 150, 40)
        
        # Área de lista de redes
        self.area_redes = pygame.Rect(20, 80, self.ancho_ventana - 40, self.largo_ventana - 100)
    
    def mostrar_texto(self, texto, x, y, color=None):
        if color is None:
            color = self.NEGRO
        superficie_texto = self.fuente.render(texto, True, color)
        self.pantalla.blit(superficie_texto, (x, y))

    def escanear_redes(self):
        """Escanea redes WiFi usando iwlist"""
        self.networks = []
        try:
            cmd = "sudo iwlist wlan0 scan | grep -E 'ESSID|Quality|Encryption'"
            output = subprocess.check_output(cmd, shell=True).decode()
            
            current_network = {}
            for line in output.split('\n'):
                if 'ESSID' in line:
                    essid = re.search('ESSID:"(.*?)"', line)
                    if essid and essid.group(1):
                        current_network['ssid'] = essid.group(1)
                        if current_network not in self.networks:
                            self.networks.append(current_network)
                        current_network = {}
                elif 'Quality' in line:
                    quality = re.search('Quality=(\d+)/70', line)
                    if quality:
                        current_network['signal'] = int(quality.group(1))
                elif 'Encryption' in line:
                    current_network['encrypted'] = 'on' in line.lower()
            
            self.mensaje = f"Se encontraron {len(self.networks)} redes"
            self.mensaje_timer = 60
            
        except subprocess.CalledProcessError as e:
            self.mensaje = "Error al escanear. ¿Tienes permisos de sudo?"
            self.mensaje_timer = 60

    def conectar_red(self, password=None):
        """Conecta a la red seleccionada usando wpa_supplicant"""
        if self.red_seleccionada is None:
            self.mensaje = "Por favor seleccione una red"
            self.mensaje_timer = 60
            return
        
        network = self.networks[self.red_seleccionada]
        
        if network.get('encrypted', True) and not password:
            self.modo_password = True
            return
            
        try:
            config = f'''
network={{
    ssid="{network['ssid']}"
    {'psk="' + password + '"' if password else 'key_mgmt=NONE'}
}}
'''
            with open('/tmp/wpa_supplicant.conf', 'w') as f:
                f.write(config)
            
            os.system('sudo cp /tmp/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')
            os.system('sudo wpa_cli -i wlan0 reconfigure')
            
            time.sleep(5)
            
            status = subprocess.check_output(['iwgetid']).decode()
            if network['ssid'] in status:
                self.mensaje = f"Conectado a {network['ssid']}"
                self.modo_password = False
            else:
                self.mensaje = "No se pudo conectar a la red"
            
        except Exception as e:
            self.mensaje = f"Error al conectar: {str(e)}"
        
        self.mensaje_timer = 60

    def dibujar_lista_redes(self):
        pygame.draw.rect(self.pantalla, self.BLANCO, self.area_redes)
        pygame.draw.rect(self.pantalla, self.NEGRO, self.area_redes, 1)
        
        y_offset = self.area_redes.top + 5 - self.scroll_offset
        for i, network in enumerate(self.networks):
            if y_offset + 30 > self.area_redes.top and y_offset < self.area_redes.bottom:
                network_rect = pygame.Rect(
                    self.area_redes.left + 5,
                    y_offset,
                    self.area_redes.width - 10,
                    25
                )
                
                if i == self.red_seleccionada:
                    pygame.draw.rect(self.pantalla, self.AZUL_CLARO, network_rect, 0)
                    text_color = self.BLANCO
                else:
                    text_color = self.NEGRO
                
                security = "🔒" if network.get('encrypted', True) else "🔓"
                signal = network.get('signal', 0)
                signal_text = "📶" if signal > 50 else "📶" if signal > 30 else "📶"
                
                network_text = f"{security} {network['ssid']} {signal_text}"
                superficie_texto = self.fuente_pequena.render(network_text, True, text_color)
                self.pantalla.blit(superficie_texto, (network_rect.left + 5, network_rect.top + 2))
            
            y_offset += 30

    def dibujar_dialogo_password(self):
        s = pygame.Surface((self.ancho_ventana, self.largo_ventana))
        s.set_alpha(128)
        s.fill(self.NEGRO)
        self.pantalla.blit(s, (0, 0))
        
        dialog_rect = pygame.Rect(
            self.ancho_ventana//4,
            self.largo_ventana//3,
            self.ancho_ventana//2,
            self.largo_ventana//3
        )
        pygame.draw.rect(self.pantalla, self.BLANCO, dialog_rect)
        pygame.draw.rect(self.pantalla, self.NEGRO, dialog_rect, 2)
        
        self.mostrar_texto(
            "Ingrese la contraseña",
            dialog_rect.centerx - 150,
            dialog_rect.top + 20
        )
        
        password_rect = pygame.Rect(
            dialog_rect.left + 20,
            dialog_rect.centery - 20,
            dialog_rect.width - 40,
            40
        )
        pygame.draw.rect(self.pantalla, self.BLANCO, password_rect)
        pygame.draw.rect(self.pantalla, self.NEGRO, password_rect, 1)
        
        password_display = "*" * len(self.password_input)
        self.mostrar_texto(
            password_display,
            password_rect.left + 5,
            password_rect.centery - 10
        )

    def iniciar_menu(self):
        self.ejecutando = True
        clock = pygame.time.Clock()
        
        while self.ejecutando:
            self.pantalla.fill(self.GRIS)
            
            # Dibujar botones
            pygame.draw.rect(self.pantalla, self.AZUL_CLARO, self.boton_escanear)
            pygame.draw.rect(self.pantalla, self.VERDE, self.boton_conectar)
            pygame.draw.rect(self.pantalla, self.ROJO, self.boton_volver)
            
            self.mostrar_texto("Escanear", self.boton_escanear.centerx - 50, self.boton_escanear.centery - 15, self.BLANCO)
            self.mostrar_texto("Conectar", self.boton_conectar.centerx - 50, self.boton_conectar.centery - 15, self.BLANCO)
            self.mostrar_texto("VOLVER", self.boton_volver.centerx - 50, self.boton_volver.centery - 15, self.BLANCO)
            
            self.dibujar_lista_redes()
            
            # Mostrar mensaje si existe
            if self.mensaje_timer > 0:
                self.mostrar_texto(self.mensaje, 20, self.largo_ventana - 40)
                self.mensaje_timer -= 1
            
            # Mostrar diálogo de contraseña si está activo
            if self.modo_password:
                self.dibujar_dialogo_password()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                    sys.exit()
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if not self.modo_password:
                        if self.boton_escanear.collidepoint(evento.pos):
                            self.escanear_redes()
                        elif self.boton_conectar.collidepoint(evento.pos):
                            self.conectar_red()
                        elif self.boton_volver.collidepoint(evento.pos):
                            self.ejecutando = False
                        elif self.area_redes.collidepoint(evento.pos):
                            y_rel = evento.pos[1] - self.area_redes.top + self.scroll_offset
                            clicked_index = y_rel // 30
                            if 0 <= clicked_index < len(self.networks):
                                self.red_seleccionada = clicked_index
                
                elif evento.type == pygame.MOUSEWHEEL:
                    if self.networks:
                        self.scroll_offset = max(0, min(
                            self.scroll_offset - evento.y * 20,
                            len(self.networks) * 30 - self.area_redes.height
                        ))
                
                elif evento.type == pygame.KEYDOWN and self.modo_password:
                    if evento.key == pygame.K_RETURN:
                        self.conectar_red(self.password_input)
                        self.password_input = ""
                    elif evento.key == pygame.K_BACKSPACE:
                        self.password_input = self.password_input[:-1]
                    elif evento.key == pygame.K_ESCAPE:
                        self.modo_password = False
                        self.password_input = ""
                    else:
                        self.password_input += evento.unicode
                
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.ejecutando = False
            
            pygame.display.flip()
            clock.tick(60)
    
    def detener_menu(self):
        self.ejecutando = False
        pygame.quit()

if __name__ == "__main__":
    scanner = WifiScanner()
    scanner.iniciar_menu()
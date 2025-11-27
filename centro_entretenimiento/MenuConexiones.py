import pygame
import subprocess
import re
import time
import os
import logging

class MenuConexiones:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.alto_ventana, self.largo_ventana = self.pantalla.get_size()
        pygame.display.set_caption("Menú de Conexiones de Red")

        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.GRIS = (200, 200, 200)
        self.AZUL_CLARO = (255, 64, 0)

        self.fuente = pygame.font.SysFont("Arial", 60)
        self.opciones = ["CONFIGURAR WIFI", "VOLVER"]
        self.opcion_seleccionada = 0
        self.ejecutando = False

    def mostrar_texto(self, texto, x, y, color=None):
        if color is None:
            color = self.NEGRO
        superficie_texto = self.fuente.render(texto, True, color)
        self.pantalla.blit(superficie_texto, (x, y))
        
    def cuadro_texto(self, mensaje):
        opciones=["REGRESAR"]
        indice_opcion=0
        fondo7=pygame.image.load('images/fondo.jpg')
        def Background_cuadro(fondo7):
            size=pygame.transform.scale(fondo7,(2048,1500))
            self.pantalla.blit(size,(0,0))



        texto_ingresado = ""
        entrada_activa = True

        while entrada_activa:
            #self.pantalla.fill(self.BLANCO)
            Background_cuadro(fondo7)
            self.mostrar_texto(mensaje, 50, 50)
            self.mostrar_texto("Escribe y presiona TAB para continuar", 50, 500, self.AZUL_CLARO)
            self.mostrar_texto("Usa las flechas y Enter para volver",50, 560, self.AZUL_CLARO)

            pygame.draw.rect(self.pantalla, self.NEGRO, (50, 200, 600, 70), 2)
            superficie_texto = self.fuente.render(texto_ingresado, True, self.NEGRO)
            self.pantalla.blit(superficie_texto, (55, 205))
            y=1000
            for i, opcion in enumerate(opciones):
                if i==indice_opcion:
                    texto=self.fuente.render(opcion, True, self.AZUL_CLARO)
                else:
                    texto=self.fuente.render(opcion, True, self.NEGRO)
                self.pantalla.blit(texto,(200,y))
            y+=70

            pygame.display.flip()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    entrada_activa = False
                    self.ejecutando = False
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key==pygame.K_DOWN:
                        indice_opcion = (indice_opcion+1)%len(opciones)
                    elif evento.key==pygame.K_UP:
                        indice_opcion = (indice_opcion-1)%len(opcion)
                    elif evento.key == pygame.K_a:
                        #ejecutar_opcion(indice_opcion)
                        self.ejecutando=False
                    elif evento.key == pygame.K_TAB:
                        entrada_activa=False #TAB para confirmar
                    elif evento.key == pygame.K_BACKSPACE:  # Borrar
                        texto_ingresado = texto_ingresado[:-1]
                    else:  # Agregar caracteres
                        texto_ingresado += evento.unicode

        return texto_ingresado
    
    def configurar_wifi(self):
        fondo6=pygame.image.load('images/fondo.jpg')
        def Background_wifi(fondo6):
            size=pygame.transform.scale(fondo6,(2048,1500))
            self.pantalla.blit(size,(0,0))


        try:
            ssid = self.cuadro_texto("Ingresa el nombre de la red WiFi (SSID):")
            clave = self.cuadro_texto("Ingresa la contraseña de la red WiFi:")

            #self.pantalla.fill(self.BLANCO)
            Background_wifi(fondo6)
            self.mostrar_texto(f"Intentando conectar a {ssid}...", 50, 200)
            pygame.display.flip()

            exito = self.conectar_wifi(ssid, clave)

            #self.pantalla.fill(self.BLANCO)
            Background_wifi(fondo6)
            if exito:
                self.mostrar_texto(f"Conectado a {ssid} con éxito.", 50, 200)
            else:
                self.mostrar_texto(f"No se pudo conectar a {ssid}. Verifica los datos.", 50, 200)
            pygame.display.flip()
            pygame.time.wait(3000)

        except Exception as e:
            #self.pantalla.fill(self.BLANCO)
            Background_wifi(fondo6)
            self.mostrar_texto(f"Ocurrió un error: {e}", 50, 200)
            pygame.display.flip()
            pygame.time.wait(3000)

    def conectar_wifi(self, red, clave):
        archivo_conf = '/etc/wpa_supplicant/wpa_supplicant.conf'

        #try:
            #with open(archivo_conf, 'r') as f:
            #    contenido = f.read()
            #if f'ssid="{red}"' in contenido:
            #    print(f"La red {red} ya está configurada.")
            #    return True

            #with open(archivo_conf, 'a') as f:
            #    f.write(f'\nnetwork={{\n\tssid="{red}"\n\tpsk="{clave}"\n\tkey_mgmt=WPA-PSK\n\tpriority=1\n}}\n')
            #print(f"Configuración para {red} añadida correctamente.")

            #resultado = subprocess.run(["sudo", "systemctl", "restart", "wpa_supplicant"], capture_output=True, text=True)
            #if resultado.returncode != 0:
            #    print(f"Error al reiniciar wpa_supplicant: {resultado.stderr}")
            #    return False

            #resultado = subprocess.run(["sudo", "dhclient", "wlan0"], capture_output=True, text=True)
            #if resultado.returncode != 0:
            #    print(f"Error al ejecutar dhclient: {resultado.stderr}")
            #    return False



        try:
            with open(archivo_conf, 'r') as f:
              contenido = f.read()


            if f'network={{\n\tssid="{red}"' in contenido:
              contenido = contenido.replace(f'network={{\n\tssid="{red}"\n\tpsk="*" }}', "")


            with open(archivo_conf, 'w') as f:
              f.write(contenido)
              f.write(f'\nnetwork={{\n\tssid="{red}"\n\tpsk="{clave}"\n\tkey_mgmt=WPA-PSK\n}}\n')

            with open(archivo_conf, 'a') as f:
              f.write(f'\nnetwork={{\n\tssid="{red}"\n\tpsk="{clave}"\n\tkey_mgmt=WPA-PSK\n\tpriority=1\n}}\n')

            print(f"Configuración para {red} añadida correctamente.")

            resultado = subprocess.run(["sudo", "systemctl", "restart", "wpa_supplicant"], capture_output=True, text=True)
            if resultado.returncode != 0:
                print(f"Error al reiniciar wpa_supplicant: {resultado.stderr}")
                return False

            resultado = subprocess.run(["sudo", "dhclient", "wlan0"], capture_output=True, text=True)
            if resultado.returncode != 0:
                print(f"Error al ejecutar dhclient: {resultado.stderr}")
                return False


            print(f"Reiniciando servicios de red para {red}...")
            return True
        except subprocess.CalledProcessError:
            logging.error("Faltan dependencias de red")
            self.message = "Error: Instala wireless-tools y wpasupplicant"
            self.message_timer = 120
            return False

    def iniciar_menu(self):
        self.ejecutando = True
        fondo5=pygame.image.load('images/fondo.jpg')

        def Background_conexiones(fondo5):
            size=pygame.transform.scale(fondo5,(2048,1500))
            self.pantalla.blit(size,(0,0))

        while self.ejecutando:
            #self.pantalla.fill(self.BLANCO)
            Background_conexiones(fondo5)
            self.mostrar_texto("Selecciona una opción:", 50, 50)

            y_offset = 350
            for indice, texto in enumerate(self.opciones):
                color = self.AZUL_CLARO if indice == self.opcion_seleccionada else self.NEGRO
                self.mostrar_texto(texto, 700, y_offset, color)
                y_offset += 200
            self.mostrar_texto("ESC - Volver al menú principal", 50, self.alto_ventana - 60, self.GRIS)
            self.mostrar_texto("ENTER - Seleccionar opción", 50, self.alto_ventana - 30, self.GRIS)
            self.mostrar_texto("↑↓ - Moverse entre las opciones", 50, self.alto_ventana - 90, self.GRIS)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.ejecutando = False
                        sys.exit()
                    elif evento.key == pygame.K_DOWN:
                        self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
                    elif evento.key == pygame.K_UP:
                        self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
                    elif evento.key == pygame.K_RETURN:
                        if self.opciones[self.opcion_seleccionada] == "CONFIGURAR WIFI":
                            self.configurar_wifi()
                        elif self.opciones[self.opcion_seleccionada] == "VOLVER":
                            self.ejecutando = False

network={{
    ssid="{network['ssid']}"
    {'psk="' + password + '"' if password else 'key_mgmt=NONE'}
}}
'''
            
            # Guardar y aplicar configuración
            with open('/tmp/wpa_supplicant.conf', 'w') as f:
                f.write(config)
            
            # Comandos de conexión con más información
            os.system(f'sudo cp /tmp/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')
            os.system(f'sudo wpa_cli -i {self.NETWORK_INTERFACE} reconfigure')
            
            # Esperar y verificar conexión
            time.sleep(10)  # Tiempo más largo para conexión
            
            # Verificación de conexión más robusta
            connection_check = subprocess.run(
                ['iwgetid', self.NETWORK_INTERFACE], 
                capture_output=True, 
                text=True
            )
            
            if network['ssid'] in connection_check.stdout:
                logging.info(f"Conectado exitosamente a {network['ssid']}")
                self.message = f"Conectado a {network['ssid']}"
                self.password_mode = False
            else:
                logging.warning("Falló la conexión")
                self.message = "No se pudo conectar a la red"
            
        except Exception as e:
            logging.error(f"Error de conexión: {e}")
            self.message = f"Error al conectar: {str(e)}"
        
        self.message_timer = 60
    
    def draw_network_list(self):
        pygame.draw.rect(self.screen, self.WHITE, self.networks_area)
        pygame.draw.rect(self.screen, self.BLACK, self.networks_area, 1)
        
        y_offset = self.networks_area.top + 5 - self.scroll_offset
        for i, network in enumerate(self.networks):
            if y_offset + 30 > self.networks_area.top and y_offset < self.networks_area.bottom:
                network_rect = pygame.Rect(self.networks_area.left + 5, y_offset, 
                                        self.networks_area.width - 10, 25)
                
                if i == self.selected_network:
                    pygame.draw.rect(self.screen, self.BLUE, network_rect, 0)
                    text_color = self.WHITE
                else:
                    text_color = self.BLACK
                
                security = "🔒" if network.get('encrypted', True) else "🔓"
                signal = network.get('signal', 0)
                signal_text = "📶" if signal > 50 else "📶" if signal > 30 else "📶"
                
                network_text = f"{security} {network['ssid']} {signal_text}"
                text_surface = self.font.render(network_text, True, text_color)
                self.screen.blit(text_surface, (network_rect.left + 5, network_rect.top + 2))
            
            y_offset += 30
    
    def draw_password_dialog(self):
        # Dibujar fondo semitransparente
        s = pygame.Surface((self.WIDTH, self.HEIGHT))
        s.set_alpha(128)
        s.fill(self.BLACK)
        self.screen.blit(s, (0, 0))
        
        # Dibujar diálogo
        dialog_rect = pygame.Rect(self.WIDTH//4, self.HEIGHT//3, self.WIDTH//2, self.HEIGHT//3)
        pygame.draw.rect(self.screen, self.WHITE, dialog_rect)
        pygame.draw.rect(self.screen, self.BLACK, dialog_rect, 2)
        
        title = self.font.render("Ingrese la contraseña", True, self.BLACK)
        self.screen.blit(title, (dialog_rect.centerx - title.get_width()//2, 
                                dialog_rect.top + 20))
        
        password_rect = pygame.Rect(dialog_rect.left + 20, dialog_rect.centery - 20, 
                                  dialog_rect.width - 40, 40)
        pygame.draw.rect(self.screen, self.WHITE, password_rect)
        pygame.draw.rect(self.screen, self.BLACK, password_rect, 1)
        
        password_display = "*" * len(self.password_input)
        password_surface = self.font.render(password_display, True, self.BLACK)
        self.screen.blit(password_surface, (password_rect.left + 5, password_rect.centery - 10))
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.password_mode:
                        if self.scan_button.collidepoint(event.pos):
                            self.scan_networks()
                        elif self.connect_button.collidepoint(event.pos):
                            self.connect_to_network()
                        elif self.networks_area.collidepoint(event.pos):
                            y_rel = event.pos[1] - self.networks_area.top + self.scroll_offset
                            clicked_index = y_rel // 30
                            if 0 <= clicked_index < len(self.networks):
                                self.selected_network = clicked_index
                
                elif event.type == pygame.MOUSEWHEEL:
                    if self.networks:
                        self.scroll_offset = max(0, min(self.scroll_offset - event.y * 20,
                                                      len(self.networks) * 30 - self.networks_area.height))
                
                elif event.type == pygame.KEYDOWN and self.password_mode:
                    if event.key == pygame.K_RETURN:
                        self.connect_to_network(self.password_input)
                        self.password_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.password_input = self.password_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.password_mode = False
                        self.password_input = ""
                    else:
                        self.password_input += event.unicode
            
            self.screen.fill(self.GRAY)
            
            pygame.draw.rect(self.screen, self.BLUE, self.scan_button)
            pygame.draw.rect(self.screen, self.GREEN, self.connect_button)
            
            # Añadir bordes negros a los botones
            pygame.draw.rect(self.screen, self.BLACK, self.scan_button, 2)
            pygame.draw.rect(self.screen, self.BLACK, self.connect_button, 2)
            
            scan_text = self.font.render("Escanear", True, self.BLACK)
            connect_text = self.font.render("Conectar", True, self.BLACK)
            
            self.screen.blit(scan_text, (self.scan_button.centerx - scan_text.get_width()//2,
                                       self.scan_button.centery - scan_text.get_height()//2))
            self.screen.blit(connect_text, (self.connect_button.centerx - connect_text.get_width()//2,
                                          self.connect_button.centery - connect_text.get_height()//2))
            
            self.draw_network_list()
            
            if self.message_timer > 0:
                message_surface = self.font.render(self.message, True, self.BLACK)
                self.screen.blit(message_surface, (20, self.HEIGHT - 40))
                self.message_timer -= 1
            
            if self.password_mode:
                self.draw_password_dialog()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

    def iniciar_menu(self):
        """Método para iniciar el menú con verificaciones"""
        try:
            logging.info("Iniciando menú de conexiones WiFi")
            self.run()
        except Exception as e:
            logging.critical(f"Error crítico al iniciar menú: {e}")
            print(f"Error crítico: {e}")
 '''           
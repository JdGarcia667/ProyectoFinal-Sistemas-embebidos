#!/bin/bash
# Script de inicio automático para Centro Multimedia

# Esperar a que el sistema esté listo
sleep 5

# Ocultar el cursor del mouse
unclutter -idle 0.01 -root &

# Deshabilitar el protector de pantalla
xset s off
xset -dpms

# Ocultar la barra de tareas (si usas LXDE)
# pkill lxpanel

# Ejecutar el centro multimedia
cd /home/raspi/centro_entretenimiento
python3 prueba1.py

# Si la aplicación se cierra, forzar apagado o reinicio
sudo poweroff

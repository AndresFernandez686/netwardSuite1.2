#!/usr/bin/env python3
"""Limpiar main.py - remover menú HTML y dejar selectbox"""

import re

filepath = 'main.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

#  Encontrar el inicio del bloque administrador
start = content.find('        elif rol == "administrador":')
if start == -1:
    print("No encontré el bloque administrador")
    exit(1)

# Encontrar donde termina el st.markdown CSS
css_start = content.find('st.markdown("""', start)
css_end = content.find('""", unsafe_allow_html=True)', css_start) + len('""", unsafe_allow_html=True)')

# Encontrar la siguiente línea "# Inicializar"
next_line = content.find('# Inicializar opcion del menu', css_end)

# Extraer la parte que vamos a mantener
before = content[:start + len('        elif rol == "administrador":') + len('\n')]
after = content[next_line:]

# Nueva content sin el CSS/HTML
new_content = before + '            ' + after

# Escribir
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Limpiado exitosamente")
with open(filepath, 'r') as f:
    lines = f.readlines()
    for i in range(310, min(330, len(lines))):
        print(f"{i+1}: {lines[i][:70]}")

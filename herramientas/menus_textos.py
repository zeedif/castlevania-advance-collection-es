# -*- coding: utf-8 -*-
"""Textos en español de las imágenes del menú de la colección (sprites con el texto ya dibujado).

Cada entrada: (id del icono, clase de estilo, texto original en inglés (solo sirve para calibrar), texto en español).
Para las descripciones largas el texto en español es una lista de líneas ya partidas.
Las áreas de Aria of Sorrow existen también en francés y alemán (el juego elige según el idioma de la ROM), por eso
cada una se traduce tres veces con el mismo texto.
"""

# --- pausemenu.psb (system/motion/pausemenu) ----------------------------------------------------------------------
PAUSA = [
    # botones del menú de pausa
    ('0076', 'btn', 'Save', 'Guardar'),
    ('0077', 'btn', 'Load', 'Cargar'),
    ('0078', 'btn', 'Save Replay', 'Guardar repetición'),
    ('0079', 'btn', 'Play Replay', 'Ver repetición'),
    ('0080', 'btn', 'Screen Settings', 'Ajustes de pantalla'),
    ('0081', 'btn', 'Control Settings', 'Ajustes de controles'),
    ('0082', 'btn', 'Encyclopedia', 'Enciclopedia'),
    ('0084', 'btn', 'Wallpaper', 'Fondo de pantalla'),
    ('0085', 'btn', 'Return to Game', 'Volver al juego'),
    ('0086', 'btn', 'Credits', 'Créditos'),
    ('0087', 'btn', 'Reset Game', 'Reiniciar juego'),
    ('0088', 'btn', 'End Game', 'Terminar juego'),
    ('0104', 'btn', 'Gadget Settings', 'Ajustes de gadgets'),
    ('0106', 'btn', 'Sound Settings', 'Ajustes de sonido'),
    # cabeceras de la enciclopedia
    ('0090', 'hdr', 'ITEM', 'OBJETO'),
    ('0092', 'hdr', 'EQUIP', 'EQUIPO'),
    ('0097', 'hdr', 'FUSION-SPELL', 'FUSIÓN'),
    ('0099', 'hdr', 'TACTICAL SOUL', 'ALMA TÁCTICA'),
    ('0101', 'hdr', 'ENEMY', 'ENEMIGO'),
    # pantalla de controles
    ('0131', 'bind', 'Rewind with', 'Rebobinar con'),
    ('0135', 'bind', 'Move', 'Mover'),
    ('0136', 'bind', 'Crouch', 'Agacharse'),
    ('0137', 'bind', 'Sub-Weapon Attack', 'Ataque con subarma'),
    ('0138', 'bind', 'Bullet Soul Attack', 'Ataque con alma de bala'),
    ('0139', 'bind', 'Drop Down', 'Bajar de plataforma'),
    ('0140', 'bind', 'Pause Menu', 'Menú de pausa'),
    ('0141', 'bind', 'Close Game', 'Cerrar juego'),
    ('0143', 'bind', 'Attack / Cancel', 'Ataque / Cancelar'),
    ('0145', 'bind', 'Jump / Confirm', 'Salto / Confirmar'),
    ('0146', 'bind', 'Display the Status Screen', 'Mostrar pantalla de estado'),
    ('0147', 'bind', 'Display the Map Screen', 'Mostrar mapa'),
    ('0149', 'bind', 'Special Move', 'Movimiento especial'),
    ('0150', 'bind', 'Dash (Left Direction)', 'Carrera (izquierda)'),
    ('0151', 'bind', 'Dash (Right Direction)', 'Carrera (derecha)'),
    ('0152', 'bind', 'Activate Ability', 'Activar habilidad'),
    ('0153', 'bind', 'Activate Guardian Soul', 'Activar alma guardiana'),
    ('0156', 'bind', 'Start / Pause', 'Inicio / Pausa'),
    ('0157', 'bind', 'Password Item Select (Left)', 'Contraseña: elegir objeto (izq.)'),
    ('0158', 'bind', 'Password Item Select (Right)', 'Contraseña: elegir objeto (der.)'),
    ('0159', 'bind', 'Jump x 2', 'Salto × 2'),
    ('0163', 'bind', 'Collection Gadget', 'Gadget de colección'),
    ('0164', 'bind', 'Soul Gadget', 'Gadget de almas'),
    ('0166', 'bind', 'High Quality Sound', 'Sonido de alta calidad'),
    ('0168', 'bind', 'Confirm', 'Confirmar'),
    ('0171', 'bind', 'Attack', 'Ataque'),
    ('0172', 'bind', 'Jump', 'Salto'),
    ('0177', 'bind', 'Backflip', 'Voltereta atrás'),
    ('0178', 'bind', 'Jump on the Stairs', 'Saltar en las escaleras'),
    ('0180', 'bind', 'DSS Gadget', 'Gadget DSS'),
    # títulos y opciones de los submenús
    ('0183', 'cy_s', 'Load', 'Cargar'),
    ('0185', 'cy_s', 'Save Replay', 'Guardar repetición'),
    ('0187', 'cy_s', 'Screen Setting', 'Ajustes de pantalla'),
    ('0189', 'cy_s', 'Wallpaper', 'Fondo de pantalla'),
    ('0207', 'cy_s', 'Play Replay', 'Ver repetición'),
    ('0218', 'cy_s', 'Gadget Settings', 'Ajustes de gadgets'),
    ('0220', 'cy_s', 'Sound Settings', 'Ajustes de sonido'),
    ('0224', 'cy_s', 'Save', 'Guardar'),
    ('0193', 'cy_b', 'Pause Menu', 'Menú de pausa'),
    ('0212', 'cy_b', 'Control Settings', 'Ajustes de controles'),
    ('0222', 'cy_b', 'Encyclopedia', 'Enciclopedia'),
    ('0191', 'opt', 'Standard', 'Estándar'),
    ('0194', 'opt', 'Pixel Perfect', 'Píxel perfecto'),
    ('0196', 'opt', 'Full', 'Completa'),
    ('0198', 'opt', 'With Filter', 'Con filtro'),
    ('0203', 'opt', 'Type A', 'Tipo A'),
    ('0205', 'opt', 'Type B', 'Tipo B'),
    ('0209', 'opt', 'Type C', 'Tipo C'),
    ('0214', 'opt', 'Type D', 'Tipo D'),
    ('0215', 'opt', 'Type E', 'Tipo E'),
    ('0216', 'opt', 'Type F', 'Tipo F'),
    # enciclopedia
    ('0231', 'stat', 'DROP 1', 'OBJETO 1'),
    ('0232', 'stat', 'DROP 2', 'OBJETO 2'),
    ('0234', 'stat', 'ATTR', 'ATRIB.'),
    ('0236', 'stat', 'TOLERANCE', 'RESISTENCIA'),
    ('0239', 'stat', 'WEAKNESS', 'DEBILIDAD'),
    ('0241', 'stat', 'Price', 'Precio'),
    # textos de ayuda
    ('0251', 'desc', 'Displays the DSS Attribute & Action cards that are obtainable', ['Muestra las cartas DSS de Atributo y Acción que se pueden', 'obtener de los monstruos en combate.']),
    ('0252', 'desc', 'Displays obtainable collection items in the current area.', ['Muestra los objetos de colección que se pueden obtener en el área actual.']),
    ('0253', 'desc', 'Displays whether or not soul is obtained from monster in battle.', ['Muestra si ya se obtuvo el alma del monstruo en combate.']),
    ('0254', 'desc', 'You can change the frequency and bitrate of the sound while playing.', ['Puedes cambiar la frecuencia y la tasa de bits del sonido durante el juego.', 'Actívalo (ON) para obtener sonido de alta calidad.']),
    ('0257', 'desc', 'Keyboard settings cannot be changed.', ['No se puede cambiar la configuración del teclado.']),
]

# 0255 lleva los iconos de las teclas dibujados encima en los huecos: se trata aparte (tres tramos y dos huecos)
PAUSA_CIERRE = ('0255', 'desc', ['Selecciona mientras presionas', '+', 'para cerrar la aplicación.'])

# nombres de áreas: (id inglés, [ids fr, de], español)
_AREAS_CIRCLE = [
    ('0263', 'Catacumbas'), ('0264', 'Escalera del abismo'), ('0265', 'Sala de audiencias'), ('0266', 'Pasillo del triunfo'),
    ('0267', 'Torre de máquinas'), ('0268', 'Corredor eterno'), ('0269', 'Torre de la capilla'), ('0270', 'Almacén subterráneo'),
    ('0271', 'Galería subterránea'), ('0273', 'Canal subterráneo'), ('0275', 'Muralla exterior'), ('0277', 'Torre de observación'),
    ('0279', 'Sala ceremonial'), ('0281', 'Arena de batalla'),
]
_EN_CIRCLE = {
    '0263': 'Catacomb', '0264': 'Abyss Stairway', '0265': 'Audience Room', '0266': 'Triumph Hallway', '0267': 'Machine Tower',
    '0268': 'Eternal Corridor', '0269': 'Chapel Tower', '0270': 'Underground Warehouse', '0271': 'Underground Gallery',
    '0273': 'Underground Waterway', '0275': 'Outer Wall', '0277': 'Observation Tower', '0279': 'Ceremonial Room', '0281': 'Battle Arena',
}

# Harmony of Dissonance: nombre, id base, ids con (A), ids con (B)
_HARMONY = [
    ('Entrance', 'Entrada', '0291', '0310', '0339'),
    ('Marble Corridor', 'Pasillo de mármol', '0292', '0312', '0341'),
    ('Shrine of the Apostates', 'Santuario de los apóstatas', '0293', '0314', '0344'),
    ('Castle Treasury', 'Tesoro del castillo', '0294', '0317', '0346'),
    ('Cave of Skeletons', 'Cueva de esqueletos', '0295', '0319', '0348'),
    ('Luminous Cavern', 'Caverna luminosa', '0296', '0321', '0350'),
    ('Aqueduct of Dragons', 'Acueducto de los dragones', '0297', '0323', '0352'),
    ('Sky Walkway', 'Pasarela celestial', '0298', '0325', '0355'),
    ('Clock Tower', 'Torre del reloj', '0299', '0328', '0357'),
    ('Castle Treasury', 'Tesoro del castillo', '0301', '0330', '0359'),
    ('Room of Illusion', 'Sala de la ilusión', '0303', '0332', '0361'),
    ('The Wailing Way', 'El camino de los lamentos', '0305', '0334', '0363'),
    ('Chapel of Dissonance', 'Capilla de la disonancia', '0307', '0336', '0366'),
]

# Aria of Sorrow: inglés, español, id en, id fr, id de
_ARIA = [
    ('Castle Corridor', 'Pasillo del castillo', '0369', '0390', '0391'),
    ('Chapel', 'Capilla', '0370', '0392', '0393'),
    ('Study', 'Estudio', '0371', '0394', '0395'),
    ('Dance Hall', 'Salón de baile', '0372', '0396', '0398'),
    ('Inner Quarters', 'Aposentos interiores', '0373', '0399', '0400'),
    ('Floating Garden', 'Jardín flotante', '0374', '0401', '0402'),
    ('Clock Tower', 'Torre del reloj', '0375', '0403', '0404'),
    ('Underground Reservoir', 'Depósito subterráneo', '0376', '0405', '0406'),
    ('The Arena', 'La arena', '0377', '0407', '0409'),
    ('Top Floor', 'Piso superior', '0379', '0410', '0411'),
    ('Forbidden Area', 'Zona prohibida', '0381', '0412', '0413'),
    ('Chaotic Realm', 'Reino caótico', '0383', '0414', '0415'),
    ('Underground Cemetery', 'Cementerio subterráneo', '0385', '0386', '0387'),
]

for _id, _es in _AREAS_CIRCLE:
    PAUSA.append((_id, 'area', _EN_CIRCLE[_id], _es))
for _en, _es, _base, _ia, _ib in _HARMONY:
    PAUSA.append((_base, 'area', _en, _es))
    PAUSA.append((_ia, 'area', _en + ' (A)', _es + ' (A)'))
    PAUSA.append((_ib, 'area', _en + ' (B)', _es + ' (B)'))
for _en, _es, _i1, _i2, _i3 in _ARIA:
    PAUSA.append((_i1, 'area', _en, _es))
    PAUSA.append((_i2, 'area', None, _es))
    PAUSA.append((_i3, 'area', None, _es))

# --- title_grandmenu (carrusel de juegos) ---------------------------------------------------------------------
GRANDMENU = [
    ('0028', 'gm_note', '(Save data cannot be used between different versions.)', '(Los datos guardados no se pueden usar entre versiones distintas.)'),
    ('0029', 'gm_ver', 'American Version', 'Versión americana'),
    ('0031', 'gm_ver', 'European Version', 'Versión europea'),
    ('0033', 'gm_ver', 'Japanese Version', 'Versión japonesa'),
    ('0036', 'gm_sel', 'Select a game version.', 'Selecciona una versión del juego.'),
    ('0060', 'gm_title', 'Gallery', 'Galería'),
    ('0061', 'gm_title', 'Music Player', 'Reproductor de música'),
    ('0062', 'gm_title', 'Game Version', 'Versión del juego'),
    ('0079', 'gm_last', 'Last Played', 'Última partida'),
]

HISTORIAS = {   # id -> (clase, párrafos)
    '0004': ['El año es 1830.',
             'En un antiguo castillo en las afueras del Imperio austriaco, un señor demoníaco capaz de unir los poderes de las tinieblas estaba siendo resucitado por obra de un malvado ansioso de caos.',
             'En este castillo demoníaco, Camilla, una de las sirvientas de Drácula, comenzó la invocación de un ritual para devolver a la vida a su señor, Drácula.',
             'El cazavampiros Morris y sus dos aprendices, Nathan y Hugh, percibieron una anomalía en el equilibrio de la naturaleza y corrieron a impedir el impío regreso de Drácula.',
             '«¡Ese monstruo impío no debe volver jamás!»',
             'Sin embargo, llegaron demasiado tarde para evitar que Drácula saliera de su encierro. Drácula usó sus poderes mágicos para encarcelar a Morris y arrojó a Nathan y a Hugh a un cementerio bajo el castillo demoníaco.',
             'Juntos, los dos comenzaron a recorrer el castillo para derrotar a Drácula y rescatar a su maestro.'],
    '0008': ['Han pasado cincuenta años desde que Simon Belmont venció la maldición de Drácula.',
             'El destino ha dispuesto que Juste Belmont, descendiente de sangre de la familia Belmont, cace las reliquias de Drácula.',
             'Un día, el mejor amigo de Juste, Maxim, que dos años antes había partido en una expedición de entrenamiento, regresó inesperadamente... con el cuerpo cubierto de heridas.',
             'Le informa a Juste de que Lydie, una amiga de la infancia a quien ambos aprecian profundamente, ha sido secuestrada.',
             'Maxim ha perdido por completo la memoria del tiempo que pasó entrenando lejos de casa, y solo conserva imágenes vagas del secuestro.',
             'Sin hacer caso de sus heridas, Maxim guía a Juste hasta el lugar donde cree que Lydie permanece cautiva.',
             'Atravesando una densa niebla, los dos hombres dieron con un castillo que no figuraba en ningún mapa. ¿Sería el legendario castillo de Drácula?',
             'Erguido solemnemente en la noche, este castillo amenazante da la bienvenida a sus inesperados huéspedes mientras la luz de la luna lo baña...'],
    '0011': ['El año es 2035. Japón.',
             'Multitudes de espectadores se reúnen a la espera del primer eclipse solar total del siglo XXI.',
             'Me llamo Soma Cruz y soy un estudiante de intercambio de secundaria que estudia en Japón. Vivo cerca del santuario Hakuba, un antiguo santuario con fuertes lazos con la mitología japonesa.',
             'Mina Hakuba, la única hija del cuidador del santuario, es mi compañera de clase y mi amiga de la infancia. Me puse en camino hacia el santuario para ver el eclipse solar con Mina.',
             'Pero, por alguna extraña razón, la escalera que sube al santuario se sentía más larga de lo normal, como si algo intentara impedirnos llegar a nuestro destino. Cuando por fin logré cruzar la puerta del santuario, mis sentidos empezaron a nublarse.',
             'A lo lejos, el eclipse solar se acercaba a la totalidad, pero el sol, negro como la noche, parecía atrapar una oscuridad caótica. En ese momento, Mina y yo quedamos inconscientes, solo para despertar dentro de un castillo misterioso. Ahora debo encontrar la forma de salir de este laberinto y escapar sano y salvo con mi amiga.'],
    '0014': ['El escenario: la Transilvania medieval. Han pasado varios cientos de años desde que el legendario héroe Simon Belmont derrotó al malvado conde Drácula y lo selló por lo que debía ser la eternidad. La gente hace tiempo que olvidó el horror de los no muertos, lo que permitió que unos cuantos individuos depravados devolvieran al Príncipe de las Tinieblas a su estado anterior: duerme en su ataúd de día y acecha a víctimas indefensas por la noche.',
             'Drácula planea ahora vengarse de su viejo enemigo a través de sus descendientes, encerrando en su oscuro y lúgubre castillo a Annette, la novia del bisnieto de Belmont, Richter, y a su hermana María.',
             'Al enterarse, Richter toma el sagrado látigo de su antepasado, transmitido de padre a hijo a lo largo de los años, y parte hacia el castillo de Drácula para rescatar a Annette y a María y sellar al malvado conde para siempre.'],
}

# --- title_ui_parts ---------------------------------------------------------------------------------------------
UI_PARTS = [
    ('0002', 'ready', 'READY?', '¿LISTO?'),
    ('0003', 'ready', 'PLEASE WAIT', 'POR FAVOR, ESPERA'),
    ('0007', 'load', 'Now Loading...', 'Cargando…'),
    ('0008', 'load_blur', 'Now Loading...', 'Cargando…'),
    ('0069', 'btn', 'Pause Menu', 'Menú de pausa'),
    ('0070', 'btn', 'Game Start', 'Iniciar juego'),
    ('0073', 'load', 'Saving', 'Guardando'),
]

# --- music_player -----------------------------------------------------------------------------------------------
MUSICA = [
    ('0021', 'cy_b', 'Music Player', 'Reproductor de música'),
    ('0022', 'cy_b', 'Playlist Edit', 'Editar lista'),
]
MUSICA_VACIA = ('0043', ['Aún no hay pistas registradas en esta lista.'], ['Registra pistas con ', '«Editar lista»', '.'])

# --- nowloading / title_opening_screen --------------------------------------------------------------------------
CARGA = [
    ('0001', 'load', 'Now Loading...', 'Cargando…'),
    ('0002', 'load_blur', 'Now Loading...', 'Cargando…'),
]
APERTURA = [
    ('0007', 'press', 'PRESS ANY BUTTON', 'PULSA CUALQUIER BOTÓN'),
]

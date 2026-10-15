# Archivo TIC IA — decisiones de diseño

Web académica HTML + Bootstrap + JavaScript, servida por FastAPI. Su tarea es consultar una biblioteca autorizada y contrastar las respuestas con documentos originales.

## Dirección
Biblioteca técnica tranquila: identidad azul, jerarquía clara y lectura cómoda. La marca conserva Archivo TIC IA y una señal de libro; la consulta recibe el acento principal. Sin animación ornamental, fotografías ni nuevas dependencias.

UI UX Pro Max: consulta `knowledge base search productivity`, estilo Minimalism & Swiss Style, prioridad a búsqueda visible, contraste y foco. Se adapta la recomendación documental a la consulta existente; se descartan FAQ, marketing y contacto porque no corresponden al producto. La primera consulta académica se descartó por devolver un portafolio. Tipografía del sistema evita otra descarga de fuentes.

Apple Design: se aplican fundamentos web, no convenciones de aplicaciones Apple. Referencias consultadas: accessibility.md › Vision / Mobility, layout.md › Visual hierarchy / Adaptability, typography.md › Ensuring legibility / Conveying hierarchy, color.md, buttons.md, entering-data.md, loading.md › Showing progress, writing.md › Best practices y cross-platform.md.

## Tokens — paleta vigente
- Blanco #FFFFFF: fondo y tarjetas; reemplaza completamente al crema #F9F5EB.
- Coral #EA5455: línea de consulta/respuesta y subrayado de marca.
- Naranja #F07B3F: contador documental y acento lateral.
- Azul grisáceo #2D4059: texto secundario, hover y línea de biblioteca.
- Azul profundo #002B5B: texto principal, enlaces, botones y foco.
- Mezclas con blanco para separadores y hover de documentos.
Los colores coral y naranja se usan como acentos, evitando texto pequeño de estos tonos sobre blanco.
El fondo permanece blanco independientemente del tema del sistema.

Texto base 16 px relativo a rem; auxiliares 12–14 px, títulos 18–36 px. Controles principales al menos 44 px de alto. Espacios 8/12/16/20/24/28/40 px. Radios 10/14/20 px. Foco de 3 px con separación de 4 px. Transiciones de color de 160 ms, desactivadas al solicitar movimiento reducido. Fondo blanco fijo solicitado.

## Composición
Escritorio: [marca y estado] / [introducción] / [cuenta] / [biblioteca | consulta y respuesta].
Móvil: [marca] / [introducción] / [cuenta] / [biblioteca] / [consulta] / [respuesta]. Se conserva el orden visual, de lectura y teclado. El enlace inicial permite saltar directamente a la consulta.

## Criterio
La identidad deriva de la biblioteca y sus fuentes; no se agrega un hero promocional, estadísticas inventadas ni paneles de diagnóstico. Los IDs, los permisos, el inventario, la sincronización y las consultas permanecen en su flujo existente.

## Ajustes finales de interacción
Footer fijo con espacio reservado. Desde 700 px de ancho y 680 px de alto, el escritorio ocupa la ventana y cada panel largo tiene su propio desplazamiento. En ventanas pequeñas se conserva desplazamiento normal para no ocultar controles. Pregunta sin redimensionamiento manual.
Puntos de espera mientras responde la API; después, presentación progresiva del texto (hasta 6 segundos). No es streaming de tokens del servidor. Con movimiento reducido, el texto aparece completo. La respuesta se desplaza al final, salvo que la persona suba para releer. Las fuentes se mantienen enlazadas y se anuncia una sola finalización accesible.

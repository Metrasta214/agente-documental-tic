# Evidencias de la práctica 2.3 — Archivo TIC IA

Validación realizada el 14 de octubre de 2026 en el proyecto local de VS Code.

## Resultado comprobado

La interfaz consultó FastAPI, el backend usó File Search con el índice real y la respuesta mostró citas con enlaces de Google Drive. Se conserva una captura en consulta-con-fuentes.png. Se ejecutaron 12 pruebas automáticas aprobadas; existe una advertencia de deprecación de TestClient/httpx.

En la primera validacion habia cinco documentos TXT distintos de prueba. Los datos son ficticios y no constituyen prácticas técnicas oficiales de AWS. Había diez registros por una carga duplicada; se enviaron las cinco copias a la papelera y el índice confirmó cinco bajas.

## Consultas reales

| Prueba | HTTP | Citas anotadas | Documentos recuperados |
|---|---|---|---|
| comparacion_sin_rag | 200 | 0 | 0 |
| localizar_con_rag | 200 | 0 | 8 |
| resumir | 200 | 3 | 8 |
| comparar | 200 | 4 | 8 |
| ausencia | 200 | 0 | 8 |

Los documentos recuperados no equivalen a citas del modelo. La interfaz los identifica expresamente. Las cifras de consultas corresponden al índice previo a la limpieza; la captura posterior muestra cinco documentos.

### comparacion_sin_rag

Pregunta: ¿Cuál es el código exclusivo de la práctica de AWS RDS?

El "código exclusivo" de una práctica de AWS RDS no es un término estándar o comúnmente reconocido. Si te refieres a un código específico, como un identificador único de laboratorio, ejercicio o práctica en alguna plataforma educativa, curso o sistema de gestión, necesitaría que me indiques en qué contexto o plataforma está esa práctica, ya que AWS RDS (Amazon Relational Database Service) es un servicio y no tiene un "código exclusivo" propio.

Si estás hablando de algún curso, laboratorio o práctica específica (por ejemplo, en una plataforma como AWS Training, Udemy, Coursera u otra), ese código lo maneja el sistema o la institución que la imparte.

Si puedes aclarar un poco más el contexto o la fuente del "código exclusivo" que buscas, podré ayudarte mejor.

### localizar_con_rag

Pregunta: ¿Cuál es el código exclusivo de la práctica de AWS RDS? Cita el documento.

El código exclusivo de la práctica de AWS RDS es: **RDS-ATLAS-427**.

Esto se menciona en el documento ficticio de prueba donde se indica que en el escenario inventado Atlas se asignan 40 puntos a la base de datos y el responsable es el Equipo Azul, con ese código exclusivo para la práctica de AWS RDS .

### resumir

Pregunta: Resume el escenario ficticio de VPC Peering y sus puntos. Cita el documento.

El escenario ficticio de VPC Peering conecta las redes "Laboratorio Norte" y "Laboratorio Sur". Este escenario pertenece a la práctica B y se le asignan 25 puntos. El equipo responsable es el "Equipo Verde" y el código exclusivo de esta práctica es PEER-DELTA-815. Se aclara que este texto no es una guía técnica de AWS.

Respecto a los puntos, en comparación con otra práctica (práctica A) que trata sobre AWS RDS y recibe 40 puntos, la práctica B de VPC Peering recibe 25 puntos. Ambas prácticas exigen entregar un informe: la práctica A entrega un inventario de tablas, mientras que la práctica B entrega un diagrama de redes. La diferencia en puntos entre ambas es de 15.

En resumen, la práctica B de VPC Peering consiste en la conexión ficticia de dos redes (Laboratorio Norte y Sur), con un enfoque en la entrega de un diagrama de redes y una valoración de 25 puntos bajo responsabilidad del Equipo Verde.

Esta información fue tomada textualmente de los documentos: tmpgp7vwgo9.txt y tmpoqqp3kfm.txt para el escenario y puntos; y tmpfpj1gqui.txt para la comparación de puntos entre A y B.

Fuente anotada: [02-peering.txt](https://drive.google.com/file/d/1jQswZklEelXB8DZ7_Ahan6Pslrats5FD/view?usp=drivesdk)

Fuente anotada: [02-peering.txt](https://drive.google.com/file/d/1GUdqe4s9lw3STgtYWwkz39gAw9Gh0GH0/view?usp=drivesdk)

Fuente anotada: [03-comparacion.txt](https://drive.google.com/file/d/1HVadtQSj6VgpNx3Y_vYWbZ7_5PHyR8Jx/view?usp=drivesdk)

### comparar

Pregunta: Compara las prácticas A y B: puntos y entregables. Cita documentos.

La comparación entre las prácticas A y B, en cuanto a puntos y entregables, es la siguiente:

- La práctica A trata sobre AWS RDS, tiene una asignación de 40 puntos, y el entregable obligatorio es un informe que incluye un inventario de tablas. Además, el responsable es el Equipo Azul y su código exclusivo es RDS-ATLAS-427.
- La práctica B aborda VPC Peering, está valorada en 25 puntos y también requiere la entrega de un informe, pero en este caso el entregable es un diagrama de redes. El responsable es el Equipo Verde y su código exclusivo es PEER-DELTA-815.

La diferencia en puntuación entre ambas prácticas es de 15 puntos, siendo la práctica A la que tiene mayor valor. También se diferencian en los entregables específicos: inventario de tablas (A) frente a diagrama de redes (B).

Esta información procede de los documentos que describen ambas prácticas, destacando sus puntos y entregables respectivos.

Fuente anotada: [03-comparacion.txt](https://drive.google.com/file/d/1MrAlOCZmVK4XyJEo4-5Y8eXyJeL5VH7L/view?usp=drivesdk)

Fuente anotada: [03-comparacion.txt](https://drive.google.com/file/d/1HVadtQSj6VgpNx3Y_vYWbZ7_5PHyR8Jx/view?usp=drivesdk)

Fuente anotada: [02-peering.txt](https://drive.google.com/file/d/1jQswZklEelXB8DZ7_Ahan6Pslrats5FD/view?usp=drivesdk)

Fuente anotada: [01-rds.txt](https://drive.google.com/file/d/1zFKS5KI9g6D8JLKa_9lsTtC2gtN1dcd3/view?usp=drivesdk)

### ausencia

Pregunta: ¿Cuál es la contraseña de producción del servidor de pagos?

No he encontrado información sobre la contraseña de producción del servidor de pagos en los documentos proporcionados. Algunos archivos mencionan explícitamente que no contienen información sobre precios reales o credenciales, incluyendo contraseñas  . Por lo tanto, no puedo proporcionar esa información.

## Sincronización incremental real

| Operación | Resultado observado |
|---|---|
| Alta de 06-sincronizacion.txt | added=1, unchanged=5, errors=[] |
| Subir versión 2 manteniendo ID de Drive | updated=1, unchanged=5, errors=[] |
| Preguntar por el código actualizado | SYNC-ORQUIDEA-242; una cita verificada |
| Enviar archivo de ensayo a papelera y sincronizar | removed=1, unchanged=5, errors=[] |
| Repetir sin modificar | unchanged=5, errors=[] |

El archivo de ensayo se retiró al terminar. Las eliminaciones del índice pueden tardar en reflejarse en búsquedas.

## Interpretación de la comparación

Con RAG se recuperó el código exclusivo y datos del corpus. Sin RAG no se proporcionó el código. Esto demuestra el valor de recuperar contenido privado del índice; no prueba que RAG elimine errores. Una respuesta correcta puede carecer de anotaciones, y un documento recuperado no demuestra por sí mismo que sustente cada afirmación.

Se corrigió la instrucción de la consulta sin RAG para declarar que no tiene acceso al índice. Se solicitan resultados de recuperación y uso de File Search cuando está activo. Las fuentes anotadas conservan su validación por ID del manifiesto.

## Reto Vercel: investigación y estado

Vercel admite FastAPI y reconoce una instancia app en puntos de entrada compatibles, incluido app.py. La compatibilidad del framework no resuelve la autenticación ni la persistencia de esta aplicación.

El prototipo actual sigue usando InstalledAppFlow de escritorio, token.json y data/manifest.json locales. Antes de publicar una aplicación funcional se necesitan OAuth Web Application con callback HTTPS, state y sesiones, almacenamiento persistente seguro de tokens y manifiesto, autorización por usuario, control de /api/ask y sincronización, y cuotas. local_only solo protege la operación local y no proporciona autenticación pública.

No se realizó un deployment. Conforme a la alternativa del punto 54 de la guía, se documenta el impedimento y se conserva el prototipo local validado. No se presenta un deployment público incompleto como si fuera una aplicación segura terminada.

Fuentes oficiales consultadas:

- https://developers.openai.com/api/docs/guides/tools-file-search
- https://vercel.com/docs/frameworks/backend/fastapi
- https://vercel.com/docs/functions/runtimes/python

## Pendientes de la entrega

- Formatos completados: TXT, PDF y Google Docs nativo; detalles en la validacion adicional.
- Publicar código en GitHub: Git local ya está inicializado; la pestaña de GitHub solicita iniciar sesión. No hay URL remota creada.
- Vercel: adaptación web pendiente; impedimento documentado arriba.
- Revisar y personalizar las conclusiones del alumno. Este informe registra observaciones técnicas y no sustituye sus conclusiones personales.

## Temas para las conclusiones personales

Drive API obtiene archivos; OAuth autoriza acceso; el servicio de sincronización prepara el índice; File Search recupera fragmentos y Responses genera la respuesta. Las clases separan responsabilidades. Git conserva hitos reproducibles y .gitignore excluye claves y estado privado. Una aplicación que funciona en localhost requiere cambios de seguridad y persistencia antes de servir a usuarios por Internet.

## Validacion adicional de formatos

La sincronizacion final anadio dos archivos sin errores: un Google Docs nativo y un PDF. El inventario final contiene siete documentos distintos (cinco TXT, un Google Docs y un PDF). La consulta real recupero DOCS-LUNA-707 y PDF-SOL-808; devolvio 1 cita anotada. La fuente de VPC Peering se abrio y su texto coincidio con la respuesta.

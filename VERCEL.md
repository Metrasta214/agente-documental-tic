# Modo web en Vercel

El modo local conserva OAuth Desktop, token.json y manifiesto local. Vercel activa siempre el modo web aunque APP_MODE no esté definido. También puede activarse explícitamente con APP_MODE=web.

## Autenticación

Cliente Google OAuth de tipo Web Application, con el callback exacto PUBLIC_BASE_URL/auth/callback. El flujo utiliza state, nonce y PKCE; valida el ID token firmado por Google, audiencia, email_verified y la cuenta única OWNER_EMAIL. Las cookies son Secure, HttpOnly y SameSite=Lax. La sesión dura ocho horas. Ninguna cookie contiene tokens de Drive ni la clave de OpenAI.

El propietario debe iniciar sesión y consentir la lectura de Drive. El inventario, las consultas y la sincronización requieren su sesión. Las operaciones POST también requieren un Origin igual al origen HTTPS configurado. Los documentos siguen limitados por código a GOOGLE_DRIVE_FOLDER_ID; el alcance OAuth drive.readonly tiene más amplitud que ese filtro.

## Persistencia y límites

El almacén Vercel Blob conectado debe ser privado. Su autenticación usa BLOB_STORE_ID y OIDC del proyecto. Tokens y manifiesto se cifran adicionalmente con una clave derivada de SESSION_SECRET. No se copian token.json ni credentials.json de escritorio a Vercel.

La sincronización utiliza un bloqueo persistente creado sin permitir sobrescritura; evita que dos instancias escriban el mismo manifiesto simultáneamente. Ante una ejecución terminada forzosamente, falla de forma cerrada: el administrador debe comprobar que ya no haya sincronizaciones en ejecución y retirar archivo-tic/sync.lock desde el almacén privado. Los bloqueos de cuotas tienen el sufijo .lock y se recuperan de la misma forma. No retirar un bloqueo de una operación activa.

Límites del laboratorio: 20 documentos, 20 MB por archivo, 30 preguntas y 6 sincronizaciones por hora. Las cuotas se comparten entre instancias mediante estado persistente. La función tiene un máximo de 300 segundos; para corpus mayores se requiere un trabajo asíncrono y recuperación de tareas.

Cambiar SESSION_SECRET invalida sesiones y el estado cifrado. Respaldar la clave en un gestor seguro y conservarla entre despliegues. No publicar variables ni capturas de secretos. El contenido documental se transmite a OpenAI al indexarlo.

## Variables

Configurar las variables de .env.web.example en el servidor. SESSION_SECRET debe ser aleatoria y tener al menos 40 caracteres. La cuenta OWNER_EMAIL coincide con el propietario del corpus. BLOB_STORE_ID se incorpora al conectar el almacén; usar OIDC en el deployment.

## Validación

Probar que el visitante anónimo recibe 401 en inventario, preguntas y sincronización. Iniciar sesión con el propietario, sincronizar y consultar. Verificar persistencia después de otro despliegue, rechazo de cuentas distintas, control de Origin, enlaces de Drive y ausencia de secretos en frontend/repositorio. Las pruebas automáticas cubren controles de acceso, state, PKCE, cookies, cifrado y cuotas.

Documentación: https://vercel.com/docs/frameworks/backend/fastapi ; https://vercel.com/docs/vercel-blob/private-storage ; https://developers.google.com/identity/protocols/oauth2/web-server

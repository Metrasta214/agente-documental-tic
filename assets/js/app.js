import {ApiClient} from './api.js';
const api = new ApiClient();
const el = id => document.getElementById(id);
const msg = (text, danger=false) => {el('message').textContent=text;el('message').className='small mt-3 '+(danger?'text-danger':'text-secondary');};
function linkFor(source) { if(!source.url) return null; try { const u=new URL(source.url); if(u.protocol==='https:' && ['drive.google.com','docs.google.com'].includes(u.hostname)) return u.href; }catch(_) {} return null; }
let authorized = false, syncing = false, serverRunning = false, asking = false;
let pollTimer, documentRequest=0;
function controls(){
  el('sync').disabled = !authorized || syncing || serverRunning;
  el('ask').disabled = !authorized || syncing || serverRunning || asking;
  el('sync').textContent = syncing || serverRunning ? 'Sincronizando…' : 'Sincronizar desde Drive';
}
function schedulePoll(){
  clearTimeout(pollTimer);
  if(authorized && (syncing || serverRunning)) pollTimer=setTimeout(async()=>{
    try { await loadDocuments(); }
    catch(e){el('sync-status').textContent='No se pudo actualizar el progreso. Reintentando…'; schedulePoll();}
  }, 3000);
}
async function loadDocuments(){
  const currentRequest=++documentRequest;
  const r=await api.documents();
  if(currentRequest!==documentRequest)return;
  el('doc-count').textContent=r.indexed;
  const box=el('documents');box.replaceChildren();
  if(!r.documents.length)box.textContent='Aún no hay documentos indexados.';
  for(const d of r.documents){
    const div=document.createElement('div');div.className='doc-item';
    const a=document.createElement('a');a.textContent=d.name;const href=linkFor(d);
    if(href){a.href=href;a.target='_blank';a.rel='noopener noreferrer';}
    div.append(a);box.append(div);
  }
  const progress=r.sync || {};
  serverRunning=progress.state==='running';
  const status=el('sync-status');
  if(serverRunning){
    status.textContent=`Indexando: ${progress.processed || 0} de ${progress.total || 0} documentos procesados. El inventario se actualiza automáticamente.`;
    if(Date.now()/1000-progress.updated_at>360)status.textContent='La sincronización no ha reportado avances recientemente. Comprueba los registros antes de volver a iniciarla.';
  }else if(progress.state==='completed'){
    const st=progress.stats || {};
    status.textContent=`Sincronización terminada: ${r.indexed} documentos indexados. ${st.added || 0} nuevos, ${st.updated || 0} actualizados, ${st.removed || 0} eliminados, ${st.unchanged || 0} sin cambios. Errores: ${(st.errors || []).length}.`;
    for(const err of st.errors || []){const line=document.createElement('div');line.textContent=`${err.file}: ${err.error}`;status.append(line);}
  }else if(progress.state==='failed')status.textContent='La sincronización falló. Se conserva el inventario procesado; revisa el error antes de reintentar.';
  controls(); schedulePoll();
}
async function ask(){if(!authorized || syncing || serverRunning || asking)return;const q=el('question').value.trim();if(q.length<3){msg('Escribe una pregunta de al menos 3 caracteres.',true);return;}asking=true;controls();msg('Consultando al agente…');try {const data=await api.ask(q,el('use-search').checked);el('answer').textContent=data.answer||'Sin respuesta.';const src=el('sources');src.replaceChildren();for(const source of data.sources){const li=document.createElement('li');li.className='list-group-item px-0';const href=linkFor(source);if(href){const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=source.name;li.append(a);}else{li.textContent=source.name;}src.append(li);}if(!data.sources.length){const li=document.createElement('li');li.className='list-group-item px-0 text-secondary';li.textContent='No se recibieron citas verificables para esta respuesta.';src.append(li);}for(const source of (data.retrieved_sources || [])){const li=document.createElement('li');li.className='list-group-item px-0';const href=linkFor(source);li.append(document.createTextNode('Recuperado por File Search (no equivale a cita): '));if(href){const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=source.name;li.append(a);}else{li.append(document.createTextNode(source.name));}src.append(li);}msg('Consulta finalizada.');}catch(e){msg(e.message,true);}finally{asking=false;controls();}}
async function sync(){
  if(syncing || serverRunning || !authorized)return;
  if(!confirm('¿Sincronizar archivos de la carpeta autorizada de Google Drive?'))return;
  syncing=true;controls();el('sync-status').textContent='Preparando la sincronización…';schedulePoll();
  try { await api.sync(); }
  catch(e){msg(e.message,true);}
  finally{
    syncing=false;
    try{await loadDocuments();}catch(e){msg(e.message,true);}
    controls();schedulePoll();
  }
}
el('ask').addEventListener('click',ask);el('sync').addEventListener('click',sync);el('question').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey))ask();});async function initialize(){
  try{
    const status = await api.request('/api/session');
    const health = await api.health();
    el('health').textContent=health.configured?'Servidor listo':'Configuración pendiente';
    authorized = status.authenticated;
    controls();
    if(status.web){
      el('account').hidden=false;
      el('login').hidden=status.authenticated;
      el('logout').hidden=!status.authenticated;
      el('account-status').textContent=status.authenticated?'Sesión autorizada.':'Conecta la cuenta de Google autorizada para consultar tus documentos.';
      el('sync-help').textContent='Sincroniza los cambios de la carpeta autorizada. Hasta 20 documentos de 20 MB.';
      controls();
      if(!status.authenticated){el('documents').textContent='Inicia sesión para ver el inventario.';return;}
    }
    await loadDocuments();
  }catch(e){msg(e.message,true);}
}
initialize();

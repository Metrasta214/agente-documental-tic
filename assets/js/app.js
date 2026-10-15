import {ApiClient} from './api.js';
const api = new ApiClient();
const el = id => document.getElementById(id);
const msg = (text, danger=false) => {el('message').textContent=text;el('message').className='small mt-3 '+(danger?'text-danger':'text-secondary');};
function linkFor(source) { if(!source.url) return null; try { const u=new URL(source.url); if(u.protocol==='https:' && ['drive.google.com','docs.google.com'].includes(u.hostname)) return u.href; }catch(_) {} return null; }
let canSync = false;
let authorized = false, syncing = false, serverRunning = false, asking = false;
let pollTimer, documentRequest=0;
function controls(){
  el('ask').textContent = asking ? 'Consultando…' : 'Consultar agente';
  el('sync').disabled = !canSync || syncing || serverRunning;
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
let documentsExpanded = false;
function documentDisclosure(hasDocuments) {
  const toggle=el('toggle-documents');
  if(!hasDocuments)documentsExpanded=false;
  toggle.hidden=!hasDocuments;
  toggle.setAttribute('aria-expanded',String(documentsExpanded));
  toggle.setAttribute('aria-label',documentsExpanded?'Ocultar archivos':'Mostrar archivos');
  el('documents').hidden=!hasDocuments || !documentsExpanded;
}
el('toggle-documents').addEventListener('click',()=>{
  documentsExpanded=!documentsExpanded;
  documentDisclosure(true);
});
async function loadDocuments(){
  const currentRequest=++documentRequest;
  const r=await api.documents();
  if(currentRequest!==documentRequest)return;
  el('doc-count').textContent=r.indexed;
  documentDisclosure(r.documents.length>0);
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
let followResponse = true;
const responseScroll = el('response-scroll');
responseScroll.addEventListener('scroll', () => {
  followResponse = responseScroll.scrollHeight - responseScroll.clientHeight - responseScroll.scrollTop < 48;
});
function followAnswer() {
  if (followResponse) responseScroll.scrollTop = responseScroll.scrollHeight;
}
function showSearching(useSearch) {
  const answer=el('answer'); answer.replaceChildren(); answer.className='answer is-waiting';
  const label=document.createElement('span');label.textContent=useSearch?'Buscando en los documentos…':'Preparando la respuesta…';
  const dots=document.createElement('span');dots.className='typing-dots';dots.setAttribute('aria-hidden','true');
  for(let i=0;i<3;i++)dots.append(document.createElement('i'));
  answer.append(label,dots);
  el('response-announcement').textContent=label.textContent;
}
async function writeAnswer(text) {
  const answer=el('answer'); answer.className='answer is-writing';answer.textContent='';
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    answer.textContent=text;followAnswer();return;
  }
  // Presentation animation after the API completes; this is not token streaming.
  const characters=Array.from(text), duration=Math.min(6000,characters.length*5);
  await new Promise(resolve=>{
    let start;
    function frame(now){
      start ??= now;
      const count=Math.min(characters.length,Math.max(1,Math.floor((now-start)/Math.max(1,duration)*characters.length)));
      answer.textContent=characters.slice(0,count).join('');followAnswer();
      if(count<characters.length)requestAnimationFrame(frame);else resolve();
    }
    requestAnimationFrame(frame);
  });
}
async function ask(){
  if(!authorized || syncing || serverRunning || asking)return;
  const q=el('question').value.trim();
  if(q.length<3){msg('Escribe una pregunta de al menos 3 caracteres.',true);return;}
  asking=true;followResponse=true;controls();
  const useSearch=el('use-search').checked;
  el('sources').replaceChildren();showSearching(useSearch);
  el('answer').setAttribute('aria-busy','true');
  msg(useSearch?'Buscando información para tu consulta…':'Preparando la respuesta…');
  try {
    const data=await api.ask(q,useSearch);
    await writeAnswer(data.answer||'Sin respuesta.');
    const src=el('sources');src.replaceChildren();for(const source of data.sources){const li=document.createElement('li');li.className='list-group-item px-0';const href=linkFor(source);if(href){const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=source.name;li.append(a);}else{li.textContent=source.name;}src.append(li);}if(!data.sources.length){const li=document.createElement('li');li.className='list-group-item px-0 text-secondary';li.textContent='No se recibieron citas verificables para esta respuesta.';src.append(li);}for(const source of (data.retrieved_sources || [])){const li=document.createElement('li');li.className='list-group-item px-0';const href=linkFor(source);li.append(document.createTextNode('Recuperado por File Search (no equivale a cita): '));if(href){const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=source.name;li.append(a);}else{li.append(document.createTextNode(source.name));}src.append(li);}
    followAnswer();msg('Consulta finalizada.');
    el('response-announcement').textContent='Respuesta completa. Puedes leerla y consultar sus fuentes.';
  }catch(e){
    el('answer').textContent='No se pudo completar la consulta. Revisa el mensaje e inténtalo de nuevo.';
    msg(e.message,true);el('response-announcement').textContent='La consulta no se pudo completar.';
  }finally{
    el('answer').className='answer';el('answer').setAttribute('aria-busy','false');
    asking=false;controls();
  }
}
async function sync(){
  if(syncing || serverRunning || !canSync)return;
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
    authorized = status.can_query ?? status.authenticated;
    canSync = status.can_sync ?? status.authenticated;
    controls();
    if(status.web){
      el('sync').hidden=!canSync;
      el('sync-help').textContent=canSync?'Sincroniza los cambios de la carpeta autorizada. Hasta 20 documentos de 20 MB.':'Los documentos están listos para consultar. La sincronización está reservada al administrador.';
      controls();
      if(!authorized)return;
    }
    await loadDocuments();
  }catch(e){msg(e.message,true);}
}
initialize();

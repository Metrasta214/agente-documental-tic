import {ApiClient} from './api.js';
const api = new ApiClient();
const el = id => document.getElementById(id);
const msg = (text, danger=false) => {el('message').textContent=text;el('message').className='small mt-3 '+(danger?'text-danger':'text-secondary');};
function linkFor(source) { if(!source.url) return null; try { const u=new URL(source.url); if(u.protocol==='https:' && ['drive.google.com','docs.google.com'].includes(u.hostname)) return u.href; }catch(_) {} return null; }
async function loadDocuments(){const r=await api.documents();el('doc-count').textContent=r.indexed;const box=el('documents');box.replaceChildren();if(!r.documents.length){box.textContent='Aún no hay documentos indexados.';return;}for(const d of r.documents){const div=document.createElement('div');div.className='doc-item';const a=document.createElement('a');a.textContent=d.name;const href=linkFor(d);if(href){a.href=href;a.target='_blank';a.rel='noopener noreferrer';}else {a.removeAttribute('href');}div.append(a);box.append(div);}}
async function ask(){const q=el('question').value.trim();if(q.length<3){msg('Escribe una pregunta de al menos 3 caracteres.',true);return;}el('ask').disabled=true;msg('Consultando al agente…');try {const data=await api.ask(q,el('use-search').checked);el('answer').textContent=data.answer||'Sin respuesta.';const src=el('sources');src.replaceChildren();for(const source of data.sources){const li=document.createElement('li');li.className='list-group-item px-0';const href=linkFor(source);if(href){const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=source.name;li.append(a);}else{li.textContent=source.name;}src.append(li);}if(!data.sources.length){const li=document.createElement('li');li.className='list-group-item px-0 text-secondary';li.textContent='No se recibieron citas verificables para esta respuesta.';src.append(li);}for(const source of (data.retrieved_sources || [])){const li=document.createElement('li');li.className='list-group-item px-0';const href=linkFor(source);li.append(document.createTextNode('Recuperado por File Search (no equivale a cita): '));if(href){const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=source.name;li.append(a);}else{li.append(document.createTextNode(source.name));}src.append(li);}msg('Consulta finalizada.');}catch(e){msg(e.message,true);}finally{el('ask').disabled=false;}}
async function sync(){if(!confirm('¿Sincronizar archivos de la carpeta autorizada de Google Drive?'))return;el('sync').disabled=true;msg('Sincronizando documentos…');try{const r=await api.sync();await loadDocuments();msg(`Sincronización: ${r.stats.added} nuevos, ${r.stats.updated} actualizados, ${r.stats.removed} eliminados, ${r.stats.unchanged} sin cambios. Errores: ${r.stats.errors.length}.`);}catch(e){msg(e.message,true);}finally{el('sync').disabled=false;}}
el('ask').addEventListener('click',ask);el('sync').addEventListener('click',sync);el('question').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey))ask();});async function initialize(){
  try{
    const status = await api.request('/api/session');
    const health = await api.health();
    el('health').textContent=health.configured?'Servidor listo':'Configuración pendiente';
    if(status.web){
      el('account').hidden=false;
      el('login').hidden=status.authenticated;
      el('logout').hidden=!status.authenticated;
      el('account-status').textContent=status.authenticated?'Sesión autorizada.':'Conecta la cuenta de Google autorizada para consultar tus documentos.';
      el('sync-help').textContent='Sincroniza los cambios de la carpeta autorizada. Hasta 20 documentos de 20 MB.';
      el('ask').disabled=el('sync').disabled=!status.authenticated;
      if(!status.authenticated){el('documents').textContent='Inicia sesión para ver el inventario.';return;}
    }
    await loadDocuments();
  }catch(e){msg(e.message,true);}
}
initialize();

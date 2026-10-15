const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const nodes = new Map();
const node = () => ({textContent:'',className:'',disabled:false,children:[],append(...c){this.children.push(...c)},replaceChildren(){this.children=[]},addEventListener(){}});
const element = id => {if(!nodes.has(id))nodes.set(id,node());return nodes.get(id)};
let response, timer, pendingSync;
class ApiClient {
  documents(){return Promise.resolve(structuredClone(response))}
  sync(){return new Promise(resolve=>{pendingSync=resolve})}
}
const context = vm.createContext({ApiClient, URL, Date, console, confirm:()=>true, document:{getElementById:element,createElement:node},setTimeout:f=>{timer=f;return 1},clearTimeout:()=>{timer=null}});
let source = fs.readFileSync('assets/js/app.js','utf8').replace("import {ApiClient} from './api.js';",'').replace(/initialize\(\);\s*$/,'');
vm.runInContext(source,context);
const run = code => vm.runInContext(code,context);
(async()=>{
 run('authorized=true');
 response={indexed:2,documents:[{name:'A'},{name:'B'}],sync:{state:'running',processed:2,total:7,updated_at:Date.now()/1000}};
 await run('loadDocuments()');
 assert.equal(element('doc-count').textContent,2);
 assert.match(element('sync-status').textContent,/2 de 7/);
 assert.equal(element('sync').disabled,true);
 assert.equal(typeof timer,'function');
 response={indexed:7,documents:Array.from({length:7},(_,i)=>({name:String(i)})),sync:{state:'completed',stats:{added:7,errors:[]}}};
 await timer();
 assert.equal(element('doc-count').textContent,7);
 assert.match(element('sync-status').textContent,/terminada/);
 assert.equal(element('sync').disabled,false);
 assert.equal(timer,null);
 const task=run('sync()');
 assert.equal(element('sync').disabled,true);
 response.sync={state:'running',processed:4,total:7,updated_at:Date.now()/1000};
 await timer();
 assert.match(element('sync-status').textContent,/4 de 7/);
 response.sync={state:'completed',stats:{added:7,errors:[]}};
 pendingSync({});await task;
 assert.equal(element('sync').disabled,false);
 assert.equal(element('ask').disabled,false);
 assert.equal(timer,null);
 console.log('Frontend: progreso automatico, reanudacion y controles correctos');
})().catch(e=>{console.error(e);process.exitCode=1});

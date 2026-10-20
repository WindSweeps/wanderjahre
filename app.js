const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
const refs=$$('.reference'), search=$('#source-search'), filter=$('#source-filter');
function filterSources(){const q=search.value.trim().toLocaleLowerCase();let n=0;refs.forEach(r=>{r.hidden=!(r.textContent.toLocaleLowerCase().includes(q)&&(filter.value==='all'||r.dataset.group===filter.value));if(!r.hidden)n++});$('#source-count').textContent=`显示 ${n} / ${refs.length} 条资料` ;$('#source-empty').hidden=n>0;}
search.addEventListener('input',filterSources);filter.addEventListener('change',filterSources);
let citeIndex=0;
$$('.cite').forEach(a=>{a.id=`citation-${++citeIndex}`;a.addEventListener('click',()=>{search.value='';filter.value='all';filterSources();const r=$(a.hash);if(r){r.classList.add('has-back');r.querySelector('.back-link').href='#'+a.id;}})});
$('#expand-questions').addEventListener('click',()=>{const expand=$('#expand-questions').getAttribute('aria-expanded')!=='true';$$('.why').forEach(d=>d.open=expand);$('#expand-questions').setAttribute('aria-expanded',String(expand));$('#expand-questions').textContent=expand?'收起全部问题':'展开全部问题';});
$$('.why').forEach(d=>d.addEventListener('toggle',()=>{const all=$$('.why').every(x=>x.open);$('#expand-questions').setAttribute('aria-expanded',String(all));$('#expand-questions').textContent=all?'收起全部问题':'展开全部问题';}));
$$('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
let previousDetails=[];
window.addEventListener('beforeprint',()=>{previousDetails=$$('details').map(d=>[d,d.open]);$$('details').forEach(d=>d.open=true);});
window.addEventListener('afterprint',()=>{previousDetails.forEach(([d,o])=>d.open=o);});
const navs=$$('.nav a'), sections=$$('main section');
function updateScroll(){const total=document.documentElement.scrollHeight-window.innerHeight;$('.progress').style.width=(total>0?window.scrollY/total*100:0)+'%';let id='overview';for(const s of sections){if(s.getBoundingClientRect().top<170)id=s.id;}navs.forEach(a=>a.setAttribute('aria-current',String(a.hash==='#'+id)));}
let ticking=false;window.addEventListener('scroll',()=>{if(!ticking){requestAnimationFrame(()=>{updateScroll();ticking=false;});ticking=true;}},{passive:true});updateScroll();filterSources();
$('#download-sources').addEventListener('click',()=>{const b=new Blob([$('#sources-data').textContent],{type:'application/json;charset=utf-8'}),url=URL.createObjectURL(b),a=document.createElement('a');a.href=url;a.download='wanderjahre-sources.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);});

const $=(s,c=document)=>c.querySelector(s), $$=(s,c=document)=>[...c.querySelectorAll(s)];

const header=$('[data-header]');
addEventListener('scroll',()=>header?.classList.toggle('is-scrolled',scrollY>20),{passive:true});

const menu=$('[data-menu-toggle]'), mobile=$('[data-mobile-nav]');
const setMenuState=(open)=>{
  if(!menu||!mobile)return;
  mobile.classList.toggle('is-open',open);
  mobile.toggleAttribute('inert',!open);
  menu.setAttribute('aria-expanded',String(open));
  menu.setAttribute('aria-label',open?'Close menu':'Open menu');
  menu.innerHTML=open
    ? '<svg aria-hidden="true" class="icon" viewBox="0 0 20 20"><path d="m5 5 10 10M15 5 5 15"/></svg>'
    : '<svg aria-hidden="true" class="icon" viewBox="0 0 20 20"><path d="M3 6h14M3 10h14M3 14h14"/></svg>';
};
if(mobile)mobile.setAttribute('inert','');
menu?.addEventListener('click',()=>setMenuState(!mobile?.classList.contains('is-open')));
$$('a',mobile||document.createElement('div')).forEach(link=>link.addEventListener('click',()=>setMenuState(false)));

if('IntersectionObserver' in window){
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('is-visible');io.unobserve(e.target)}}),{threshold:.08});
  $$('[data-reveal]').forEach(el=>io.observe(el));
}else{$$('[data-reveal]').forEach(el=>el.classList.add('is-visible'))}

const toast=(msg)=>{const t=$('[data-toast]');if(!t)return;t.textContent=msg;t.classList.add('is-visible');clearTimeout(window.__tt);window.__tt=setTimeout(()=>t.classList.remove('is-visible'),5000)};

$$('form[data-lead-form]').forEach(form=>{
  let status=form.querySelector('[data-form-status]');
  if(!status){status=document.createElement('p');status.dataset.formStatus='';status.className='form-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');form.append(status)}
  form.addEventListener('submit',async e=>{
    e.preventDefault();
    if(!form.reportValidity())return;
    const button=form.querySelector('button[type="submit"]');
    const original=button?.innerHTML;
    if(button){button.disabled=true;button.setAttribute('aria-busy','true');button.textContent='Sending…'}
    status.textContent='Sending your enquiry securely…';status.classList.remove('is-error','is-success');
    const payload=Object.fromEntries(new FormData(form).entries());
    payload.form=form.dataset.leadForm;
    payload.page=location.origin+location.pathname;
    try{
      const response=await fetch('/api/leads',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)});
      let result={};try{result=await response.json()}catch{}
      if(!response.ok)throw new Error(result.error||'Delivery failed');
      form.reset();
      const delivered=result.delivered===true;
      const message=delivered
        ? 'Thank you. Your enquiry has been received by NorthEdge and sent to the team.'
        : 'Thank you. Your enquiry has been securely stored by NorthEdge. For anything time-sensitive, please call 0430 595 481.';
      status.textContent=message;status.classList.add('is-success');
      toast(message);
      const success=form.querySelector('[data-success]');if(success){success.hidden=false;success.textContent=message}
    }catch(err){
      status.textContent='We could not securely receive this enquiry. Your details have not been cleared. Please try again or call 0430 595 481.';status.classList.add('is-error');
      toast('We could not securely receive this enquiry. Please try again or call 0430 595 481.');
    }finally{
      if(button){button.disabled=false;button.removeAttribute('aria-busy');button.innerHTML=original}
    }
  });
});

const searchForm=$('[data-property-search]');
searchForm?.addEventListener('submit',e=>{
  e.preventDefault();
  const p=new URLSearchParams(new FormData(searchForm));
  const journey=p.get('journey')||'buy';
  p.delete('journey');
  if(journey==='rent'){
    location.href='/rent#rent-register';
    return;
  }
  const query=p.toString();
  location.href='/buy'+(query?'?'+query:'');
});

function filterProperties(){
  const cards=$$('[data-property]'),empty=$('[data-empty]');
  if(!cards.length)return;
  const q=($('#filter-location')?.value||'').toLowerCase(),beds=+($('#filter-beds')?.value||0),max=+($('#filter-price')?.value||0);
  let shown=0;
  cards.forEach(c=>{
    const match=(!q||c.dataset.suburb.toLowerCase().includes(q)||c.textContent.toLowerCase().includes(q))&&(!beds||+c.dataset.beds>=beds)&&(!max||+c.dataset.price===0||+c.dataset.price<=max);
    c.hidden=!match;if(match)shown++;
  });
  if(empty)empty.style.display=shown?'none':'block';
}
['filter-location','filter-beds','filter-price'].forEach(id=>$('#'+id)?.addEventListener('input',filterProperties));
const params=new URLSearchParams(location.search);
if($('#filter-location')&&params.get('location'))$('#filter-location').value=params.get('location');
if($('#filter-beds')&&params.get('beds'))$('#filter-beds').value=params.get('beds');
if($('#filter-price')&&params.get('price'))$('#filter-price').value=params.get('price');
filterProperties();

const savedKey='northedge_saved_properties';
const readSaved=()=>{try{return new Set(JSON.parse(localStorage.getItem(savedKey)||'[]'))}catch{return new Set()}};
const writeSaved=set=>{try{localStorage.setItem(savedKey,JSON.stringify([...set]));return true}catch{return false}};
$$('[data-favourite]').forEach(btn=>{
  const propertyId=location.pathname.split('/').pop()||document.title;
  const saved=readSaved();
  const active=saved.has(propertyId);
  btn.classList.toggle('is-active',active);btn.setAttribute('aria-pressed',String(active));
  btn.addEventListener('click',()=>{
    const current=readSaved();
    current.has(propertyId)?current.delete(propertyId):current.add(propertyId);
    const now=current.has(propertyId);
    btn.classList.toggle('is-active',now);btn.setAttribute('aria-pressed',String(now));
    toast(writeSaved(current)?(now?'Property saved on this device.':'Property removed from saved homes.'):'Saved-property storage is unavailable in this browser.');
  });
});

$$('[data-share]').forEach(btn=>btn.addEventListener('click',async()=>{
  try{
    if(navigator.share){await navigator.share({title:document.title,url:location.href});return}
    if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(location.href);toast('Property link copied.');return}
    toast('Copy the address from your browser to share this property.');
  }catch(err){if(err?.name!=='AbortError')toast('Sharing is unavailable in this browser. Copy the page address instead.')}
}));

const lb=$('[data-lightbox]'),lbImg=lb?.querySelector('img'),lbClose=$('[data-lightbox-close]');
let lightboxReturnFocus=null;
const closeLightbox=()=>{
  if(!lb)return;
  lb.classList.remove('is-open');document.body.style.overflow='';
  lightboxReturnFocus?.focus?.();lightboxReturnFocus=null;
};
$$('[data-gallery-open]').forEach(b=>b.addEventListener('click',()=>{
  if(!lb||!lbImg)return;
  lightboxReturnFocus=b;
  const source=b.querySelector('img');
  lbImg.src=b.dataset.full||source?.src||'';lbImg.alt=source?.alt||'Property gallery image';
  lb.classList.add('is-open');document.body.style.overflow='hidden';
  requestAnimationFrame(()=>lbClose?.focus());
}));
lbClose?.addEventListener('click',closeLightbox);
lb?.addEventListener('click',e=>{if(e.target===lb)closeLightbox()});
addEventListener('keydown',e=>{
  if(e.key==='Escape'){
    if(lb?.classList.contains('is-open'))closeLightbox();
    else if(mobile?.classList.contains('is-open')){setMenuState(false);menu?.focus()}
  }
  if(e.key==='Tab'&&lb?.classList.contains('is-open')){
    const focusable=$$('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])',lb).filter(el=>!el.disabled);
    if(!focusable.length){e.preventDefault();lb.focus();return}
    const first=focusable[0],last=focusable.at(-1);
    if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}
    else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
  }
});

const areaVisual=$('[data-area-visual]'),areaCaption=$('[data-area-caption]'),areaRows=$$('[data-area-image]');
let areaRequest=0;
const activateArea=row=>{
  if(!row||row.classList.contains('is-active'))return;
  areaRows.forEach(r=>r.classList.toggle('is-active',r===row));
  const request=++areaRequest,nextSrc=row.dataset.areaImage,nextCaption=row.dataset.areaCaption;
  if(areaCaption){areaCaption.animate?.([{opacity:.35,transform:'translateY(4px)'},{opacity:1,transform:'none'}],{duration:420,easing:'cubic-bezier(.16,1,.3,1)'});areaCaption.textContent=nextCaption}
  if(!areaVisual||areaVisual.getAttribute('src')===nextSrc)return;
  areaVisual.classList.add('is-changing');
  const preload=new Image();
  preload.onload=()=>{if(request!==areaRequest)return;requestAnimationFrame(()=>{areaVisual.src=nextSrc;areaVisual.removeAttribute('srcset');areaVisual.alt=(row.querySelector('h3')?.textContent||'Melbourne north')+' local landscape';requestAnimationFrame(()=>areaVisual.classList.remove('is-changing'))})};
  preload.onerror=()=>{if(request===areaRequest)areaVisual.classList.remove('is-changing')};
  preload.src=nextSrc;
};
areaRows.forEach((row,index)=>{row.addEventListener('mouseenter',()=>activateArea(row));row.addEventListener('focus',()=>activateArea(row));row.addEventListener('pointerdown',()=>activateArea(row),{passive:true});if(index===0)row.classList.add('is-active')});

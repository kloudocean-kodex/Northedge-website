(()=>{
  const lightbox=document.querySelector('[data-lightbox]');
  const triggers=[...document.querySelectorAll('[data-gallery-open]')];
  if(!lightbox||!triggers.length)return;

  const image=lightbox.querySelector('img');
  const close=lightbox.querySelector('[data-lightbox-close]');
  if(!image||!close)return;

  const address=[document.querySelector('.property-head h1')?.textContent?.trim(),document.querySelector('.property-location')?.textContent?.trim()].filter(Boolean).join(', ')||'property';
  const items=triggers.map((button,index)=>{
    const thumb=button.querySelector('img');
    const alt=(thumb?.alt||'').trim()||`${address} — property image ${index+1}`;
    button.setAttribute('aria-label',`Open photo ${index+1} of ${triggers.length} for ${address}`);
    return {src:button.dataset.full||thumb?.currentSrc||thumb?.src||'',alt};
  });

  const badge=triggers[0].querySelector('.gallery-count');
  if(badge)badge.textContent=`View all ${items.length} photo${items.length===1?'':'s'}`;

  const nav=document.createElement('div');
  nav.className='lightbox-nav';
  nav.innerHTML=`
    <button type="button" class="lightbox-arrow lightbox-prev" data-gallery-prev aria-label="Previous photo">
      <svg aria-hidden="true" class="icon" viewBox="0 0 20 20"><path d="M12.5 4.5 7 10l5.5 5.5M7.5 10H17"/></svg>
    </button>
    <span class="lightbox-counter" data-gallery-counter aria-live="polite"></span>
    <button type="button" class="lightbox-arrow lightbox-next" data-gallery-next aria-label="Next photo">
      <svg aria-hidden="true" class="icon" viewBox="0 0 20 20"><path d="M7.5 4.5 13 10l-5.5 5.5M3 10h9.5"/></svg>
    </button>`;
  lightbox.append(nav);

  const caption=document.createElement('p');
  caption.className='lightbox-caption';
  caption.id='property-gallery-caption';
  caption.dataset.galleryCaption='';
  lightbox.append(caption);
  lightbox.setAttribute('aria-describedby',caption.id);

  const counter=nav.querySelector('[data-gallery-counter]');
  const prev=nav.querySelector('[data-gallery-prev]');
  const next=nav.querySelector('[data-gallery-next]');
  let current=0;
  let touchStartX=null;

  const preload=index=>{
    const item=items[(index+items.length)%items.length];
    if(!item?.src)return;
    const p=new Image();p.decoding='async';p.src=item.src;
  };

  const render=index=>{
    current=(index+items.length)%items.length;
    const item=items[current];
    image.src=item.src;
    image.alt=item.alt;
    caption.textContent=item.alt;
    counter.textContent=`${current+1} / ${items.length}`;
    prev.disabled=items.length<2;
    next.disabled=items.length<2;
    preload(current+1);
    preload(current-1);
  };

  triggers.forEach((button,index)=>button.addEventListener('click',()=>{
    current=index;
    render(current);
  }));
  prev.addEventListener('click',event=>{event.stopPropagation();render(current-1)});
  next.addEventListener('click',event=>{event.stopPropagation();render(current+1)});

  document.addEventListener('keydown',event=>{
    if(!lightbox.classList.contains('is-open'))return;
    if(event.key==='ArrowLeft'){event.preventDefault();render(current-1)}
    if(event.key==='ArrowRight'){event.preventDefault();render(current+1)}
  });

  lightbox.addEventListener('touchstart',event=>{
    if(event.touches.length===1)touchStartX=event.touches[0].clientX;
  },{passive:true});
  lightbox.addEventListener('touchend',event=>{
    if(touchStartX===null||event.changedTouches.length!==1)return;
    const delta=event.changedTouches[0].clientX-touchStartX;
    touchStartX=null;
    if(Math.abs(delta)<48)return;
    render(delta>0?current-1:current+1);
  },{passive:true});

  render(0);
})();

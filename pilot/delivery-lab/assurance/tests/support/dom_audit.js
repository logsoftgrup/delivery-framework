// TC-1 DOM scanner: limited automated checks, never a WCAG conformance verdict.
() => {
  const issues=[], all=[...document.querySelectorAll('input,button,a[href]')];
  const visible=e=>!!(e.offsetWidth||e.offsetHeight||e.getClientRects().length)&&getComputedStyle(e).visibility!=='hidden';
  if(!document.documentElement.lang)issues.push('page language missing');
  if(!document.title)issues.push('page title missing');
  if(document.querySelectorAll('main').length!==1)issues.push('one main required');
  if(document.querySelectorAll('h1').length!==1)issues.push('one h1 required');
  if(document.querySelectorAll('form').length!==1)issues.push('one create form required');
  if(!document.querySelector('ul,ol,[role=list]'))issues.push('semantic list missing');
  const statuses=[...document.querySelectorAll('[role=status],[aria-live=polite]')];
  if(!statuses.length)issues.push('polite status missing');
  for(const input of document.querySelectorAll('input:not([type=hidden])')){
    if(!input.labels?.length&&!input.getAttribute('aria-label')&&!input.getAttribute('aria-labelledby'))issues.push('input label missing');
    for(const id of (input.getAttribute('aria-describedby')||'').split(/\s+/).filter(Boolean))if(!document.getElementById(id))issues.push('description reference missing: '+id);
    if(input.getAttribute('aria-invalid')==='true'){
      const ids=(input.getAttribute('aria-describedby')||'').split(/\s+/).concat((input.getAttribute('aria-errormessage')||'').split(/\s+/));
      if(!ids.some(id=>{const e=document.getElementById(id);return e&&visible(e)&&/Enter|Name|name|characters/.test(e.textContent)&&!/^Use 1/.test(e.textContent)}))issues.push('visible field error association missing');
    }
  }
  const bounds=[];
  for(const e of all.filter(visible)){
    const r=e.getBoundingClientRect(),s=getComputedStyle(e);
    bounds.push({tag:e.tagName,name:e.getAttribute('aria-label')||e.textContent||e.name,x:r.x,y:r.y,width:r.width,height:r.height,outline:s.outline,disabled:e.disabled});
    if(r.left<-.5||r.right>innerWidth+.5)issues.push('control outside viewport');
    if(e.scrollWidth>e.clientWidth+1&&s.overflowX==='hidden')issues.push('clipped control text');
  }
  if(document.documentElement.scrollWidth>innerWidth+1)issues.push('horizontal page overflow');
  for(const e of document.querySelectorAll('[role=status],p')){
    if(visible(e)&&e.scrollHeight>e.clientHeight+1&&getComputedStyle(e).overflowY==='hidden')issues.push('clipped status/help/error');
  }
  return {scanner:'TC-1-dom-audit',issues,bounds,viewport:{width:innerWidth,height:innerHeight,deviceScale:devicePixelRatio},manual:['screen reader','focus visibility and obstruction','contrast including backgrounds','keyboard transitions','pointer exceptions','all applicable WCAG criteria']};
}

// Suite-controlled browser contract double. Not a production application.
const form=document.querySelector('form'), field=document.querySelector('#name'), create=document.querySelector('#create'), refresh=document.querySelector('#refresh'), status=document.querySelector('#status'), error=document.querySelector('#error'), list=document.querySelector('#items');
const trim=/^[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+|[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+$/gu;
let pending=false, ready=false, uncertain=false, confirmed=false;
const mutation=window.fixtureMutation;
if(mutation==='missing-label')document.querySelector('label').remove();
if(mutation==='detached-error')field.setAttribute('aria-describedby','help');
if(mutation==='hidden-focus'){const s=document.createElement('style');s.textContent='*:focus-visible{outline:none}';document.head.append(s);}
if(mutation==='clipped-error')error.style.cssText='height:1px;overflow:hidden';
if(mutation==='low-contrast')document.body.style.color='#eeeeee';
if(mutation==='duplicate-form')document.querySelector('main').append(form.cloneNode(true));
function controls(){create.disabled=pending||!ready;field.readOnly=pending;create.textContent=pending?'Creating…':uncertain?'Create another item':'Create';}
function render(rows){list.replaceChildren();for(const row of rows){const li=document.createElement('li');if(mutation==='innerhtml')li.innerHTML=row.name;else li.textContent=row.name;list.append(li);}document.querySelector('#count').textContent=rows.length+(rows.length===1?' item':' items');document.querySelector('#empty').hidden=rows.length!==0;}
async function load(){
  try{const r=await fetch('/api/items',{cache:'no-store'});if(!r.ok)throw new Error('list');const data=await r.json();render(data.items);ready=true;refresh.hidden=true;status.textContent=uncertain?'Check the list. A matching name may already exist. Create another item only if you intend to add one.':confirmed?'Item created.':'';confirmed=false;}
  catch{ready=mutation==='reenable-failed-get';refresh.hidden=false;status.textContent=uncertain?'We still cannot check the list. Refresh the list before creating another item.':confirmed?'Item was created, but the list could not be refreshed. Refresh the list to see it.':'Items could not be loaded. Refresh the list to try again.';}
  controls();
}
function validation(message){error.textContent=message;field.setAttribute('aria-invalid','true');field.focus();}
async function submit(){
  if(pending||!ready)return;
  const original=field.value, name=original.replace(trim,'');
  if([...name].length<1||[...name].length>80){validation('Enter 1–80 characters after trimming surrounding whitespace.');return;}
  pending=true;controls();error.textContent='';field.removeAttribute('aria-invalid');status.textContent='Creating item…';
  let result;
  try{result=await fetch('/api/items',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:original})});}
  catch{result=null;}
  pending=false;
  if(result&&result.status===201){field.value='';uncertain=false;confirmed=true;ready=false;status.textContent='Item created. Updating the list…';controls();await load();return;}
  if(result&&result.status===422){const body=await result.json();validation(body.error.fields[0].message);controls();return;}
  if(result&&result.status===503){status.textContent='Item was not created. Try again.';controls();return;}
  if(mutation==='automatic-retry'){fetch('/api/items',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:original})});}
  if(mutation==='500-definite'){status.textContent='Item was not created. Try again.';controls();return;}
  uncertain=true;ready=false;status.textContent='We could not confirm whether the item was created. Refreshing the list before you retry.';controls();await load();
}
form.addEventListener('submit',e=>{e.preventDefault();submit();});
refresh.addEventListener('click',()=>load());
load();

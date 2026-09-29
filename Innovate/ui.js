export const $=s=>document.querySelector(s);
export const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
export function toast(message){const el=$("#toast");el.textContent=message;el.classList.remove("hidden");clearTimeout(window.__toastTimer);window.__toastTimer=setTimeout(()=>el.classList.add("hidden"),2600)}
export function status(s){return `<span class="status ${esc(s)}">${esc(s.replace("_"," "))}</span>`}
export function showView(name){document.querySelectorAll(".view").forEach(v=>v.classList.toggle("active",v.id===name));document.querySelectorAll(".nav").forEach(b=>b.classList.toggle("active",b.dataset.view===name));$("#heading").textContent=({overview:"Pipeline overview",deployments:"Deployment history",risk:"Risk analysis",memory:"Failure memory"})[name]||"PulseOps"}
export function openModal(title,html){$("#modalTitle").textContent=title;$("#modalContent").innerHTML=html;$("#modal").classList.remove("hidden")}
export function closeModal(){$("#modal").classList.add("hidden")}
export function fmtDate(value){try{return new Date(value).toLocaleString()}catch{return value}}

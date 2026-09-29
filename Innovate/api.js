const BASE="/api";
async function request(path,options={}){
  const response=await fetch(BASE+path,{headers:{"Content-Type":"application/json",...(options.headers||{})},...options});
  const data=await response.json().catch(()=>({error:"Invalid server response"}));
  if(!response.ok)throw new Error(data.error||`Request failed (${response.status})`);
  return data;
}
export const api={
 overview:()=>request("/overview"),
 deployments:(env="All")=>request("/deployments?environment="+encodeURIComponent(env)),
 createDeployment:p=>request("/deployments",{method:"POST",body:JSON.stringify(p)}),
 completeDeployment:(id,p)=>request(`/deployments/${id}/complete`,{method:"POST",body:JSON.stringify(p)}),
 incidents:q=>request("/incidents?q="+encodeURIComponent(q||"")),
 addIncident:p=>request("/incidents",{method:"POST",body:JSON.stringify(p)}),
 assess:p=>request("/risk",{method:"POST",body:JSON.stringify(p)}),
 health:()=>fetch("/health").then(r=>r.json())
};

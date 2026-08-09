const redirect=(request,path)=>Response.redirect(new URL(path,request.url).toString(),301);

export function onRequest({request}){
  const url=new URL(request.url);
  const transaction=(url.searchParams.get('x')||'').toLowerCase();
  const status=(url.searchParams.get('r')||'').toLowerCase();

  if(transaction==='lease') return redirect(request,'/rent.html');
  if(transaction==='sale'&&status==='sold') return redirect(request,'/sold.html');
  if(transaction==='sale') return redirect(request,'/buy.html');

  // Unknown historic filters fall back to the complete current property index
  // rather than returning a broken WordPress/VaultRE route.
  return redirect(request,'/buy.html');
}

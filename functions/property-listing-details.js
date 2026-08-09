const redirect=(request,path)=>Response.redirect(new URL(path,request.url).toString(),301);

const byLegacyId=new Map([
  ['34688552','/property-27-design-way-kalkallo'],
  ['35074581','/property-7-rulingia-road-donnybrook'],
  ['35680034','/property-6-mathoura-road-mickleham'],
  ['36424213','/property-31-roseneath-way-mickleham'],
  ['36479751','/property-105-tungsten-drive-kalkallo'],
  ['36459858','/property-6-alisterus-road-kalkallo'],
  ['39835309','/property-27-design-way-kalkallo'],
  ['40243735','/property-7-rulingia-road-donnybrook'],
  ['40905535','/property-6-mathoura-road-mickleham'],
  ['41675613','/property-31-roseneath-way-mickleham'],
  ['41733004','/property-105-tungsten-drive-kalkallo'],
  ['41711139','/property-6-alisterus-road-kalkallo'],
]);

export function onRequest({request}){
  const url=new URL(request.url);
  const legacyIds=[url.searchParams.get('v'),url.searchParams.get('x')].filter(Boolean);
  for(const id of legacyIds){
    const destination=byLegacyId.get(id);
    if(destination) return redirect(request,destination);
  }

  const type=(url.searchParams.get('type')||'').toLowerCase();
  const status=(url.searchParams.get('stype')||'').toLowerCase();
  if(type==='lease') return redirect(request,'/rent');
  if(type==='sale'&&status==='sold') return redirect(request,'/sold');
  return redirect(request,'/buy');
}

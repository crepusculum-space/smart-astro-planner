
(async()=>{
  const sc=new URLSearchParams(location.search).get('s');
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  for(let i=0;i<200&&!(typeof SAP_CATALOG!=='undefined'&&SAP_CATALOG);i++) await wait(100);
  const _tt=Date.prototype.toLocaleTimeString; Date.prototype.toLocaleTimeString=function(l,o){return _tt.call(this,'en-GB',o)};
  const _td=Date.prototype.toLocaleDateString; Date.prototype.toLocaleDateString=function(l,o){return _td.call(this,'en-US',o)};
  const now=new Date().toISOString();
  const locs=[
   {id:'demo',name:'Backyard',description:'Suburban yard, house to the south',lat:45.5,lon:-73.6,elevation_ft:100,timezone:'America/New_York',bortle:6,clear_nights_year:120,min_altitude:35,horizon_sectors:[true,true,true,false,false,false,true,true],updated_at:now,protected:false},
   {id:'dark',name:'Dark Site',description:'Open field, 45 min from home',lat:45.2,lon:-72.0,elevation_ft:900,timezone:'America/New_York',bortle:3,clear_nights_year:140,min_altitude:30,horizon_sectors:[true,true,true,true,true,true,true,true],updated_at:now,protected:false}];
  const mk=(id,name,fl,ap,red)=>({id,name,telescope:{name:'Refractor',focal_length:fl,aperture:ap,reducer:null,effective_focal_length:fl,fratio:+(fl/ap).toFixed(1)},sensor:{name:'Mono camera',width_mm:11.2,height_mm:6.3,pixel_size_um:2.9,resolution_x:3856,resolution_y:2180},mount:{name:'Equatorial mount'},controller:{name:'Controller'},filters:['L','R','G','B','Hα','OIII','SII'],coverage_min:40,coverage_max:90,updated_at:now});
  const eqs=[mk('e1','Refractor 490mm + Mono',490,71),mk('e2','Wide 180mm + Mono',180,40)];
  LS.set('sap_locations',locs); LS.set('sap_active_location','demo');
  LS.set('sap_equipment',eqs); LS.set('sap_active_equipment','e1');
  LS.set('sap_preferences',{detail:'Standard',listSize:15,wiki:true,skyview:true});
  LS.set('sap_mode','assisted'); LS.set('sap_claude_key','sk-demo');
  const start='2026-09-26';
  const ids=['NGC 7000','NGC 281','NGC 6888','NGC 6853','IC 5146','NGC 7635','IC 1805','NGC 7380','NGC 6992','NGC 253'];
  const fov=calcFOV(eqs[0]); const targets=[];
  for(const id of ids){ const o=SAP_CATALOG.find(x=>x.id===id); if(!o) continue; const wv=calcWeeklyVisibility(o.ra,o.dec,45.5,-73.6,start,6,locs[0].horizon_sectors,35); targets.push(catalogToTarget(o,wv,fov)); }
  LS.set('sap_targets',targets);
  LS.set('sap_target_meta',{name:'Sep–Nov 2026 · Bortle 6 · Refractor 490mm',numWeeks:6,period_start:start,location_id:'demo',equipment_id:'e1',min_altitude:35,generated:now});
  const T=targets.find(t=>t.catalog==='NGC 7000')||targets[0];
  LS.set('sap_meridian',[{id:'m1',name:'NGC 7000 (framing)',ra:T.ra,dec:T.dec,location_id:'demo',updated_at:now},{id:'m2',name:'NGC 281',ra:targets.find(t=>t.catalog==='NGC 281')?.ra||13.5,dec:targets.find(t=>t.catalog==='NGC 281')?.dec||56.6,location_id:'demo',updated_at:now}]);
  const mtSeed=[
   {id:'mt1',catalog:'NGC 7000',name:'North America Nebula',type:'Emission Nebula',ra:T.ra,dec:T.dec,angle:15,equipment_id:'e2',location_id:'demo',filters:['Hα','OIII','SII'],size_arcmin:120,status:'in_progress',
     advice:{text:"## Filter strategy\nHα, OIII and SII all carry usable signal in this frame — an **SHO** palette suits it well.\n\n## Integration split\n- Hα: 45%\n- OIII: 30%\n- SII: 25%\n\n## Notes\nBortle 6 skies make the faint OIII edges the limiting factor — favor longer OIII subs. The frame is a good fit for a wide-field refractor; no mosaic needed.",date:now}},
   {id:'mt2',catalog:'NGC 6888',name:'Crescent Nebula',type:'Emission Nebula',ra:(targets.find(t=>t.catalog==='NGC 6888')?.ra)||303.2,dec:(targets.find(t=>t.catalog==='NGC 6888')?.dec)||38.4,angle:0,equipment_id:'e1',location_id:'demo',filters:['Hα','OIII'],size_arcmin:20,status:'todo'},
   {id:'mt3',catalog:'IC 5146',name:'Cocoon Nebula',type:'Emission Nebula',ra:(targets.find(t=>t.catalog==='IC 5146')?.ra)||328.4,dec:(targets.find(t=>t.catalog==='IC 5146')?.dec)||47.3,angle:30,equipment_id:'e2',location_id:'demo',filters:['L','R','G','B'],size_arcmin:12,status:'done'}
  ].map(m=>({...m,added_at:now,updated_at:now}));
  LS.set('sap_mytargets',mtSeed);
  const tab=(name,idx)=>{ switchTab(name,document.querySelectorAll('nav button')[idx]); };
  const scrollTo=async(sel,off=0)=>{ await wait(300); const el=document.querySelector(sel); if(!el) return; const sc2=el.closest('.modal,#detail-content,#target-detail')||window; el.scrollIntoView({block:'start'}); };
  const detail=async()=>{ tab('targets',0); renderTargets(); openTargetDetail(T.id); await wait(6000); };
  if(sc==='locations'){ tab('locations',3); renderLocations(); }
  else if(sc==='locform'){ tab('locations',3); renderLocations(); openLocationForm('demo'); await wait(500); ['loc-lat','loc-lon'].forEach(i=>{const e=document.getElementById(i); if(e){const v=e.value; e.type='text'; e.value=v;}}); document.querySelectorAll('.form-section').forEach(f=>{ if(f.textContent.includes('Horizon Mask')) f.scrollIntoView({block:'center'}); }); }
  else if(sc==='newsearch'){ tab('targets',0); renderTargets(); openNewTargets(); await wait(500); }
  else if(sc==='list'){ tab('targets',0); renderTargets(); }
  else if(sc==='detailtop'){ await detail(); }
  else if(sc==='sky'){ await detail(); await analyzeFraming(); await wait(1500); document.getElementById('sky-frame-card').scrollIntoView({block:'start'}); }
  else if(sc==='info'){ await detail(); const w=document.getElementById('wiki-section')||document.getElementById('simbad-section'); w.scrollIntoView({block:'start'}); }
  else if(sc==='mytargets'){ tab('plan',1); renderMyTargets(); await wait(2500); }
  else if(sc==='nightinfo'){ tab('meridian',4); renderMeridian(); await wait(300); window.scrollTo(0,0); document.querySelectorAll('.tab,#tab-meridian').forEach(e=>{e.scrollTop=0;}); }
  else if(sc==='settings'){ tab('settings',5); renderSettings(); await wait(300); [...document.querySelectorAll('h3')].find(h=>h.textContent.includes('Backup')).scrollIntoView({block:'start'}); }
  else if(sc==='equipment'){ tab('equipment',2); renderEquipment(); }
  await wait(1500);
  document.title='READY';
})();

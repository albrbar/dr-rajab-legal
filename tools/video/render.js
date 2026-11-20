const {chromium}=require('playwright');const dir=process.argv[2];const FPS=30,T=40;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+dir+'/template.html');
for(let i=0;i<FPS*T;i++){await p.evaluate(t=>render(t),i/FPS);await p.screenshot({path:`${dir}/f/${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});}
await b.close()})();

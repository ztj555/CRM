const http = require('http');
function get(url) {
  return new Promise((resolve) => {
    const options = { hostname:'localhost', port:8080, path:url, method:'GET' };
    const req = http.request(options, (res) => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve(d)); });
    req.end();
  });
}
async function main() {
  // Test docs endpoint (FastAPI auto-generated docs)
  const docs = await get('/docs');
  console.log('/docs:', docs.substring(0, 100));
}
main().catch(console.error);

const http = require('http');
function post(port, url, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body);
    const options = { hostname:'localhost', port, path:url, method:'POST', headers:{'Content-Type':'application/json','Content-Length':Buffer.byteLength(data)} };
    const req = http.request(options, (res) => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve({status:res.statusCode, data:d})); });
    req.write(data); req.end();
  });
}
function get(port, url, token) {
  return new Promise((resolve) => {
    const options = { hostname:'localhost', port, path:url, headers:{'Authorization':'Bearer '+token} };
    const req = http.request(options, (res) => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve({status:res.statusCode, data:d})); });
    req.end();
  });
}
async function main() {
  const login = await post(8081, '/api/auth/login', {username:'admin',password:'admin123'});
  const token = JSON.parse(login.data).token;
  console.log('Login:', login.status);
  
  for (const ep of ['/api/departments', '/api/team/members', '/api/team/customers']) {
    const r = await get(8081, ep, token);
    console.log(ep, '->', r.status, r.data.substring(0,200));
  }
}
main().catch(console.error);

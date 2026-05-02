const http = require('http');
function post(url, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body);
    const options = { hostname:'localhost', port:8080, path:url, method:'POST', headers:{'Content-Type':'application/json','Content-Length':Buffer.byteLength(data)} };
    const req = http.request(options, (res) => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve({status:res.statusCode, data:d})); });
    req.write(data); req.end();
  });
}
function get(url, token) {
  return new Promise((resolve) => {
    const options = { hostname:'localhost', port:8080, path:url, headers:{'Authorization':'Bearer '+token} };
    const req = http.request(options, (res) => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>resolve({status:res.statusCode, data:d})); });
    req.end();
  });
}
async function main() {
  const login = await post('/api/auth/login', {username:'admin',password:'admin123'});
  const token = JSON.parse(login.data).token;
  
  // Test various endpoints
  for (const ep of ['/api/auth/me', '/api/users', '/api/users/team', '/api/team/customers', '/api/team/members']) {
    const r = await get(ep, token);
    console.log(ep, '->', r.status, r.data.substring(0,100));
  }
}
main().catch(console.error);

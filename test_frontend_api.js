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
  // Login via frontend (port 5173 proxy)
  const login = await post(5173, '/api/auth/login', {username:'admin',password:'admin123'});
  const token = JSON.parse(login.data).token;
  console.log('Login:', login.status);
  
  // Test team/members via frontend proxy
  const members = await get(5173, '/api/team/members', token);
  console.log('/api/team/members:', members.status, members.data.substring(0, 400));
  
  // Test enhanced team/customers
  const customers = await get(5173, '/api/team/customers?page=1', token);
  console.log('/api/team/customers:', customers.status, customers.data.substring(0, 200));
}
main().catch(console.error);

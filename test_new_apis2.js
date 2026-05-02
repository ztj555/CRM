const http = require('http');

function post(url, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const options = {
      hostname: 'localhost',
      port: 8080,
      path: url,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
    };
    const req = http.request(options, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, data: d }));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function get(url, token) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost', port: 8080, path: url,
      headers: token ? { 'Authorization': 'Bearer ' + token } : {}
    };
    http.get(options, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve({ status: res.statusCode, data: d }));
    }).on('error', reject);
  });
}

async function main() {
  // Login
  const loginRes = await post('/api/auth/login', { username: 'admin', password: 'admin123' });
  console.log('Login Status:', loginRes.status);
  const loginData = JSON.parse(loginRes.data);
  const token = loginData.token;
  console.log('Token obtained');

  // Test departments
  let r = await get('/api/departments', token);
  console.log('\n/api/departments Status:', r.status);
  console.log('Data:', r.data.substring(0, 300));

  // Test team members
  r = await get('/api/team/members', token);
  console.log('\n/api/team/members Status:', r.status);
  console.log('Data:', r.data.substring(0, 500));
}

main().catch(console.error);

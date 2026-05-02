const http = require('http');

function get(url) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 8080,
      path: url,
      headers: { 
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJleHAiOjE5MDAwMDAwMDB9.8fKYcWJwZ2K_y9hJ6v1vGYk9qFzGFWd3F7aJZ9k_JY'
      }
    };
    http.get(options, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve({ status: res.statusCode, data }));
    }).on('error', reject);
  });
}

async function main() {
  console.log('=== Test /api/departments ===');
  let r = await get('/api/departments');
  console.log('Status:', r.status);
  console.log('Data:', r.data.substring(0, 200));

  console.log('\n=== Test /api/team/members ===');
  r = await get('/api/team/members');
  console.log('Status:', r.status);
  console.log('Data:', r.data.substring(0, 300));
}

main().catch(console.error);

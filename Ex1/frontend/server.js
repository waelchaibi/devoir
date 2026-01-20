const http = require('http');
const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

const PORT = 3000;

const server = http.createServer(async (req, res) => {
    if (req.url === '/') {
        let html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
        
        try {
            const response = await fetch('http://backend:5000/api/hello');
            const message = await response.text();
            html = html.replace('<!--MESSAGE-->', message);
        } catch (err) {
            html = html.replace('<!--MESSAGE-->', 'Error loading message');
        }
        
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(html);
        return;
    }
    
    let filePath = path.join(__dirname, req.url);
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end('<h1>404 - File Not Found</h1>');
            return;
        }
        
        const ext = path.extname(filePath);
        let contentType = 'text/html';
        if (ext === '.css') contentType = 'text/css';
        if (ext === '.js') contentType = 'application/javascript';
        
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
    });
});

server.listen(PORT);

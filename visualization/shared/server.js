#!/usr/bin/env node
/**
 * 可视化技能通用开发服务器
 * 用法：node server.js [port] [directory]
 * 示例：node server.js 3000 /Users/xx/project/my-visualization
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

let startPort = parseInt(process.argv[2]) || 3000;
const serveDir = process.argv[3] ? path.resolve(process.argv[3]) : process.cwd();
const MAX_PORT_TRIES = 10; // 最多尝试 10 个端口

// MIME 类型映射
const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.ttf':  'font/ttf',
};

const server = http.createServer((req, res) => {
  // 处理 URL，防止路径穿越
  let urlPath = decodeURIComponent(req.url.split('?')[0]);
  if (urlPath === '/') urlPath = '/index.html';

  const filePath = path.join(serveDir, urlPath);

  // 安全检查：确保请求路径在服务目录内
  if (!filePath.startsWith(serveDir)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end(`文件未找到: ${urlPath}`);
      } else {
        res.writeHead(500);
        res.end('服务器内部错误');
      }
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = mimeTypes[ext] || 'application/octet-stream';
    res.writeHead(200, {
      'Content-Type': contentType,
      'Cache-Control': 'no-cache', // 开发模式不缓存
    });
    res.end(content);
  });
});

// 尝试启动服务器，端口被占用时自动尝试下一个
function tryListen(port, attempt = 1) {
  server.listen(port, '127.0.0.1', () => {
    const url = `http://localhost:${port}`;
    console.log(`\n✅ 可视化服务器已启动`);
    if (port !== startPort) {
      console.log(`   （端口 ${startPort} 被占用，已自动切换到 ${port}）`);
    }
    console.log(`   地址: ${url}`);
    console.log(`   目录: ${serveDir}`);
    console.log(`\n   按 Ctrl+C 停止服务器\n`);

    // 自动打开浏览器
    const platform = process.platform;
    let openCmd;
    if (platform === 'darwin') {
      openCmd = `open "${url}"`;
    } else if (platform === 'win32') {
      openCmd = `start "${url}"`;
    } else {
      openCmd = `xdg-open "${url}"`;
    }

    exec(openCmd, (err) => {
      if (err) {
        console.log(`   提示：请手动打开浏览器访问 ${url}`);
      }
    });
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      if (attempt < MAX_PORT_TRIES) {
        // 端口被占用，尝试下一个
        server.removeAllListeners('error');
        tryListen(port + 1, attempt + 1);
      } else {
        console.error(`\n❌ 端口 ${startPort}-${port} 均被占用，请稍后重试或手动指定端口：`);
        console.error(`   node server.js ${port + 1} "${serveDir}"\n`);
        process.exit(1);
      }
    } else {
      console.error('服务器启动失败:', err.message);
      process.exit(1);
    }
  });
}

tryListen(startPort);

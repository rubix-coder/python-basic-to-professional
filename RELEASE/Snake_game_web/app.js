// Retro Snake - single-file vanilla Node.js web app
// Mobile-first (Samsung S24+, OnePlus 13, etc.). Railway-friendly: no native modules.
// Data persists to RAILWAY_VOLUME_MOUNT_PATH/players.json (or ./data/players.json locally).

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = parseInt(process.env.PORT, 10) || 3000;
const DATA_DIR = process.env.RAILWAY_VOLUME_MOUNT_PATH || path.join(__dirname, 'data');
const DATA_FILE = path.join(DATA_DIR, 'players.json');
const SESSION_TTL_MS = 24 * 60 * 60 * 1000;
const GAME_TYPES = ['easy', 'medium', 'hard'];

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(DATA_FILE)) fs.writeFileSync(DATA_FILE, JSON.stringify({ players: [] }, null, 2));

const sessions = new Map();

function loadDb() {
  try { return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')); }
  catch { return { players: [] }; }
}
function saveDb(db) {
  const tmp = DATA_FILE + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(db, null, 2));
  fs.renameSync(tmp, DATA_FILE);
}
function makeToken() { return crypto.randomBytes(24).toString('hex'); }
function getSession(req) {
  const auth = req.headers['authorization'] || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : '';
  if (!token) return null;
  const s = sessions.get(token);
  if (!s) return null;
  if (s.expires < Date.now()) { sessions.delete(token); return null; }
  return s;
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let total = 0;
    req.on('data', c => {
      total += c.length;
      if (total > 8192) { req.destroy(); reject(new Error('payload too large')); return; }
      chunks.push(c);
    });
    req.on('end', () => {
      if (!chunks.length) return resolve({});
      try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); }
      catch (e) { reject(new Error('invalid json')); }
    });
    req.on('error', reject);
  });
}
function send(res, status, body, contentType) {
  const ct = contentType || 'application/json; charset=utf-8';
  res.writeHead(status, { 'Content-Type': ct, 'Cache-Control': 'no-store' });
  res.end(ct.startsWith('application/json') ? JSON.stringify(body) : body);
}

const HTML = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="theme-color" content="#0a0a0a">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Retro Snake</title>
<style>
:root{
  --bg:#0a0a0a; --fg:#cfffd2; --accent:#4cff7a; --warn:#ffd14c;
  --danger:#ff4c5e; --grid:#0f1a12; --line:#1c2e21;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html,body{width:100%;height:100%;overflow:hidden;background:var(--bg)}
body{
  color:var(--fg);font-family:'Courier New',Menlo,monospace;
  display:flex;justify-content:center;
  padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
  touch-action:none;user-select:none;-webkit-user-select:none;
}
.app{width:100%;max-width:480px;height:100%;position:relative}
.screen{position:absolute;inset:0;padding:16px;display:none;flex-direction:column;gap:14px}
.screen.active{display:flex}
h1{color:var(--accent);font-size:30px;letter-spacing:3px;text-align:center;text-shadow:0 0 8px rgba(76,255,122,.4)}
h2{color:var(--accent);font-size:16px;letter-spacing:2px;text-align:center;opacity:.85}
.dim{color:#6f8a72;font-size:12px;text-align:center;letter-spacing:1px}
.spacer{flex:1}
.btn{
  background:transparent;color:var(--accent);border:2px solid var(--accent);
  padding:14px;font-size:18px;font-family:inherit;letter-spacing:2px;
  cursor:pointer;width:100%;text-transform:uppercase;
  transition:background .06s,color .06s;
}
.btn:active{background:var(--accent);color:var(--bg)}
.btn.secondary{color:var(--warn);border-color:var(--warn)}
.btn.secondary:active{background:var(--warn);color:var(--bg)}
.btn.danger{color:var(--danger);border-color:var(--danger)}
.btn.danger:active{background:var(--danger);color:var(--bg)}
.btn.active{background:var(--accent);color:var(--bg)}
.btn.secondary.active{background:var(--warn);color:var(--bg)}
input[type=text]{
  background:transparent;color:var(--fg);border:2px solid var(--fg);
  padding:14px;font-size:18px;font-family:inherit;width:100%;
  text-align:center;letter-spacing:3px;text-transform:uppercase;
}
input[type=text]:focus{outline:none;border-color:var(--accent);color:var(--accent)}
.row{display:flex;gap:8px}
.row .btn{flex:1;padding:12px 4px;font-size:13px;letter-spacing:1px}
.bar{display:flex;justify-content:space-between;align-items:center;padding:0 4px;font-size:13px;letter-spacing:1px}
.bar span{color:var(--accent)}
#board{
  width:100%;aspect-ratio:1/1;background:var(--grid);
  border:2px solid var(--accent);display:block;
  image-rendering:pixelated;touch-action:none;
}
.pad{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:auto}
.pad .btn{padding:18px 0;font-size:22px;letter-spacing:0}
.pad .blank{visibility:hidden}
.scores{flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:6px}
.score-row{display:flex;justify-content:space-between;padding:10px 12px;border:1px solid var(--line);font-size:14px;letter-spacing:1px}
.score-row.gold{border-color:var(--warn);color:var(--warn)}
.score-row.me{border-color:var(--accent);color:var(--accent)}
.toast{
  position:fixed;left:50%;bottom:24px;transform:translateX(-50%);
  background:var(--grid);color:var(--fg);padding:10px 18px;border:1px solid var(--accent);
  opacity:0;transition:opacity .15s;z-index:50;font-size:13px;letter-spacing:1px;
  pointer-events:none;
}
.toast.show{opacity:1}
@media (max-height:680px){
  h1{font-size:22px}
  .btn{padding:11px;font-size:16px}
  .pad .btn{padding:14px 0;font-size:20px}
}
</style>
</head>
<body>
<div class="app">

<div id="screen-login" class="screen active">
  <div class="spacer"></div>
  <h1>RETRO SNAKE</h1>
  <p class="dim">pick a name to begin</p>
  <input id="login-name" type="text" placeholder="PLAYER_1" maxlength="16" autocomplete="off" inputmode="text" spellcheck="false">
  <button class="btn" id="login-btn">ENTER</button>
  <p class="dim">letters, digits, underscore (2-16)</p>
  <div class="spacer"></div>
</div>

<div id="screen-home" class="screen">
  <h1>RETRO SNAKE</h1>
  <p class="dim" id="home-greeting"></p>
  <h2>GAME MODE</h2>
  <div class="row" id="mode-row">
    <button class="btn mode-btn" data-mode="easy">EASY</button>
    <button class="btn mode-btn" data-mode="medium">MEDIUM</button>
    <button class="btn mode-btn" data-mode="hard">HARD</button>
  </div>
  <button class="btn" id="new-game-btn">NEW GAME</button>
  <button class="btn secondary" id="scores-btn">HIGH SCORES</button>
  <div class="spacer"></div>
  <button class="btn danger" id="logout-btn">LOGOUT</button>
</div>

<div id="screen-game" class="screen">
  <div class="bar">
    <div>MODE: <span id="lbl-mode">EASY</span></div>
    <div>SCORE: <span id="lbl-score">0</span></div>
    <div>BEST: <span id="lbl-best">0</span></div>
  </div>
  <canvas id="board"></canvas>
  <div class="row">
    <button class="btn secondary" id="pause-btn">PAUSE</button>
    <button class="btn danger" id="quit-btn">HOME</button>
  </div>
  <div class="pad">
    <div class="blank"></div>
    <button class="btn dir-btn" data-dir="up">^</button>
    <div class="blank"></div>
    <button class="btn dir-btn" data-dir="left">&lt;</button>
    <button class="btn dir-btn" data-dir="down">v</button>
    <button class="btn dir-btn" data-dir="right">&gt;</button>
  </div>
</div>

<div id="screen-scores" class="screen">
  <h1>HIGH SCORES</h1>
  <div class="row" id="scores-mode-row">
    <button class="btn smode-btn active" data-mode="easy">EASY</button>
    <button class="btn smode-btn" data-mode="medium">MEDIUM</button>
    <button class="btn smode-btn" data-mode="hard">HARD</button>
  </div>
  <div class="scores" id="scores-list"></div>
  <button class="btn" id="scores-back">BACK</button>
</div>

<div id="toast" class="toast"></div>
</div>

<script>
(function(){
  const $ = s => document.querySelector(s);
  const $$ = s => Array.from(document.querySelectorAll(s));
  const SPEEDS = { easy: 200, medium: 130, hard: 80 };
  const GRID = 20;

  const state = {
    token: localStorage.getItem('snake_token') || null,
    player: localStorage.getItem('snake_player') || null,
    mode: localStorage.getItem('snake_mode') || 'easy',
    best: { easy: 0, medium: 0, hard: 0 },
  };

  function show(id){ $$('.screen').forEach(s => s.classList.remove('active')); $('#screen-'+id).classList.add('active'); }
  function toast(msg, ms){
    const t = $('#toast'); t.textContent = msg; t.classList.add('show');
    clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), ms || 1800);
  }
  function cssVar(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }

  async function api(p, opts){
    opts = opts || {};
    const headers = { 'Content-Type': 'application/json' };
    if (state.token) headers['Authorization'] = 'Bearer ' + state.token;
    const res = await fetch(p, { method: opts.method || 'GET', headers, body: opts.body ? JSON.stringify(opts.body) : undefined });
    let data = {};
    try { data = await res.json(); } catch(_) {}
    if (res.status === 401) { logout(); throw new Error('session expired'); }
    if (!res.ok) throw new Error(data.error || ('http ' + res.status));
    return data;
  }

  function logout(){
    localStorage.removeItem('snake_token');
    localStorage.removeItem('snake_player');
    state.token = null; state.player = null;
    state.best = { easy: 0, medium: 0, hard: 0 };
    show('login');
  }

  async function loadBest(){
    try { const r = await api('/api/me'); state.best = r.best_by_mode || state.best; } catch(_) {}
  }

  function updateModeButtons(){
    $$('#screen-home .mode-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === state.mode));
  }

  function enterHome(){
    $('#home-greeting').textContent = 'player: ' + state.player;
    updateModeButtons();
    show('home');
  }

  $('#login-btn').addEventListener('click', async () => {
    const name = $('#login-name').value.trim();
    if (!/^[A-Za-z0-9_]{2,16}$/.test(name)) { toast('invalid name'); return; }
    try {
      const r = await api('/api/login', { method: 'POST', body: { player_name: name } });
      state.token = r.token; state.player = r.player_name;
      localStorage.setItem('snake_token', r.token);
      localStorage.setItem('snake_player', r.player_name);
      await loadBest();
      enterHome();
    } catch(e){ toast(e.message); }
  });
  $('#login-name').addEventListener('keydown', e => { if (e.key === 'Enter') $('#login-btn').click(); });

  $$('#screen-home .mode-btn').forEach(b => b.addEventListener('click', () => {
    state.mode = b.dataset.mode;
    localStorage.setItem('snake_mode', state.mode);
    updateModeButtons();
  }));

  $('#new-game-btn').addEventListener('click', () => startGame());
  $('#scores-btn').addEventListener('click', () => openScores(state.mode));
  $('#logout-btn').addEventListener('click', logout);
  $('#scores-back').addEventListener('click', enterHome);
  $('#quit-btn').addEventListener('click', () => { stopGame(); enterHome(); });
  $('#pause-btn').addEventListener('click', togglePause);

  $$('.smode-btn').forEach(b => b.addEventListener('click', () => openScores(b.dataset.mode)));

  async function openScores(mode){
    $$('.smode-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
    show('scores');
    const list = $('#scores-list');
    list.innerHTML = '<div class="dim">loading...</div>';
    try {
      const r = await api('/api/scores?mode=' + encodeURIComponent(mode));
      if (!r.scores.length) { list.innerHTML = '<div class="dim">no scores yet - go play!</div>'; return; }
      list.innerHTML = r.scores.map((s, i) => {
        const cls = ['score-row', i === 0 ? 'gold' : '', s.player_name === state.player ? 'me' : ''].filter(Boolean).join(' ');
        return '<div class="' + cls + '"><span>' + (i+1) + '. ' + escapeHtml(s.player_name) + '</span><span>' + s.high_score + '</span></div>';
      }).join('');
    } catch(e){ list.innerHTML = '<div class="dim">error: ' + escapeHtml(e.message) + '</div>'; }
  }
  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

  // ---- game ----
  const canvas = $('#board');
  const ctx = canvas.getContext('2d');
  let snake, dir, nextDir, food, score, tickMs, loopId = null, paused = false, alive = false, cellPx = 20;

  function resizeCanvas(){
    const dpr = window.devicePixelRatio || 1;
    const cssSize = canvas.clientWidth;
    canvas.width = Math.max(1, Math.floor(cssSize * dpr));
    canvas.height = canvas.width;
    cellPx = canvas.width / GRID;
  }

  function startGame(){
    show('game');
    requestAnimationFrame(() => {
      resizeCanvas();
      snake = [{x:10,y:10},{x:9,y:10},{x:8,y:10}];
      dir = {x:1,y:0}; nextDir = {x:1,y:0};
      score = 0; alive = true; paused = false;
      tickMs = SPEEDS[state.mode];
      placeFood();
      $('#lbl-mode').textContent = state.mode.toUpperCase();
      $('#lbl-score').textContent = '0';
      $('#lbl-best').textContent = state.best[state.mode] || 0;
      $('#pause-btn').textContent = 'PAUSE';
      draw();
      if (loopId) clearInterval(loopId);
      loopId = setInterval(tick, tickMs);
    });
  }
  function stopGame(){ if (loopId) { clearInterval(loopId); loopId = null; } alive = false; }
  function togglePause(){
    if (!alive) return;
    paused = !paused;
    $('#pause-btn').textContent = paused ? 'RESUME' : 'PAUSE';
    if (paused){ if (loopId){ clearInterval(loopId); loopId = null; } drawPaused(); }
    else { loopId = setInterval(tick, tickMs); }
  }
  function placeFood(){
    const taken = new Set(snake.map(s => s.x + ',' + s.y));
    let f, tries = 0;
    do { f = { x: Math.floor(Math.random()*GRID), y: Math.floor(Math.random()*GRID) }; tries++; }
    while (taken.has(f.x+','+f.y) && tries < 500);
    food = f;
  }
  function tick(){
    if (!alive || paused) return;
    dir = nextDir;
    const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
    if (head.x < 0 || head.x >= GRID || head.y < 0 || head.y >= GRID) return gameOver();
    if (snake.some((s, i) => i < snake.length - 1 && s.x === head.x && s.y === head.y)) return gameOver();
    snake.unshift(head);
    if (head.x === food.x && head.y === food.y){
      score += 10;
      $('#lbl-score').textContent = score;
      placeFood();
    } else {
      snake.pop();
    }
    draw();
  }
  function draw(){
    ctx.fillStyle = cssVar('--grid');
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // subtle grid lines
    ctx.strokeStyle = cssVar('--line');
    ctx.lineWidth = 1;
    for (let i = 1; i < GRID; i++){
      ctx.beginPath(); ctx.moveTo(i * cellPx, 0); ctx.lineTo(i * cellPx, canvas.height); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, i * cellPx); ctx.lineTo(canvas.width, i * cellPx); ctx.stroke();
    }
    // food (pulsing goodie)
    const pulse = 1 + Math.sin(Date.now() / 200) * 0.08;
    const fx = food.x * cellPx, fy = food.y * cellPx;
    const pad = cellPx * (1 - 0.7 * pulse) / 2;
    ctx.fillStyle = cssVar('--warn');
    ctx.fillRect(fx + pad, fy + pad, cellPx - pad*2, cellPx - pad*2);
    // snake
    snake.forEach((s, i) => {
      ctx.fillStyle = i === 0 ? cssVar('--fg') : cssVar('--accent');
      ctx.fillRect(s.x * cellPx + 1, s.y * cellPx + 1, cellPx - 2, cellPx - 2);
    });
  }
  function drawPaused(){
    ctx.fillStyle = 'rgba(0,0,0,0.65)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = cssVar('--accent');
    ctx.font = (canvas.width / 11) + 'px monospace';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('PAUSED', canvas.width / 2, canvas.height / 2);
  }
  async function gameOver(){
    alive = false;
    stopGame();
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = cssVar('--danger');
    ctx.font = (canvas.width / 11) + 'px monospace';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - canvas.width / 16);
    ctx.fillStyle = cssVar('--fg');
    ctx.font = (canvas.width / 16) + 'px monospace';
    ctx.fillText('SCORE ' + score, canvas.width / 2, canvas.height / 2 + canvas.width / 16);
    const prev = state.best[state.mode] || 0;
    if (score > prev){
      state.best[state.mode] = score;
      $('#lbl-best').textContent = score;
      try {
        await api('/api/score', { method: 'POST', body: { game_type: state.mode, score: score } });
        toast('NEW HIGH SCORE!');
      } catch(e){ toast('save failed: ' + e.message); }
    }
  }
  const DIRS = { up:{x:0,y:-1}, down:{x:0,y:1}, left:{x:-1,y:0}, right:{x:1,y:0} };
  function setDir(d){
    if (!alive || paused) return;
    if (d.x === -dir.x && d.y === -dir.y) return;
    nextDir = d;
  }
  $$('.dir-btn').forEach(b => {
    const fire = e => { e.preventDefault(); setDir(DIRS[b.dataset.dir]); };
    b.addEventListener('click', fire);
    b.addEventListener('touchstart', fire, { passive: false });
  });

  let touchStart = null;
  canvas.addEventListener('touchstart', e => {
    if (e.touches.length !== 1) return;
    touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
  }, { passive: true });
  canvas.addEventListener('touchend', e => {
    if (!touchStart || !e.changedTouches.length) return;
    const t = e.changedTouches[0];
    const dx = t.clientX - touchStart.x, dy = t.clientY - touchStart.y;
    if (Math.max(Math.abs(dx), Math.abs(dy)) < 20) { touchStart = null; return; }
    if (Math.abs(dx) > Math.abs(dy)) setDir(dx > 0 ? DIRS.right : DIRS.left);
    else setDir(dy > 0 ? DIRS.down : DIRS.up);
    touchStart = null;
  }, { passive: true });

  document.addEventListener('keydown', e => {
    const m = { ArrowUp:'up', ArrowDown:'down', ArrowLeft:'left', ArrowRight:'right',
                w:'up', s:'down', a:'left', d:'right',
                W:'up', S:'down', A:'left', D:'right' };
    if (m[e.key]) { e.preventDefault(); setDir(DIRS[m[e.key]]); }
    if (e.key === ' ') { e.preventDefault(); togglePause(); }
  });

  window.addEventListener('resize', () => {
    if (canvas.clientWidth && document.getElementById('screen-game').classList.contains('active')){
      resizeCanvas(); draw();
    }
  });

  (async function boot(){
    if (state.token){
      try { await loadBest(); enterHome(); }
      catch(_) { logout(); }
    } else {
      show('login');
    }
  })();
})();
</script>
</body>
</html>`;

const routes = {
  'POST /api/login': async (req, res) => {
    const body = await readBody(req);
    const name = String(body.player_name || '').trim();
    if (!/^[A-Za-z0-9_]{2,16}$/.test(name)) return send(res, 400, { error: 'invalid name' });
    const db = loadDb();
    let p = db.players.find(x => x.player_name.toLowerCase() === name.toLowerCase());
    if (!p) {
      p = { player_name: name, scores: { easy: 0, medium: 0, hard: 0 }, created_at: Date.now() };
      db.players.push(p);
      saveDb(db);
    }
    const token = makeToken();
    sessions.set(token, { player_name: p.player_name, expires: Date.now() + SESSION_TTL_MS });
    send(res, 200, { token, player_name: p.player_name, expires_in: Math.floor(SESSION_TTL_MS / 1000) });
  },

  'GET /api/me': async (req, res) => {
    const s = getSession(req); if (!s) return send(res, 401, { error: 'unauthorized' });
    const db = loadDb();
    const p = db.players.find(x => x.player_name === s.player_name);
    const scores = (p && p.scores) || {};
    send(res, 200, {
      player_name: s.player_name,
      best_by_mode: {
        easy: scores.easy || 0,
        medium: scores.medium || 0,
        hard: scores.hard || 0,
      },
    });
  },

  'POST /api/score': async (req, res) => {
    const s = getSession(req); if (!s) return send(res, 401, { error: 'unauthorized' });
    const body = await readBody(req);
    const mode = String(body.game_type || '').toLowerCase();
    const score = parseInt(body.score, 10);
    if (!GAME_TYPES.includes(mode)) return send(res, 400, { error: 'invalid game_type' });
    if (!Number.isInteger(score) || score < 0 || score > 100000) return send(res, 400, { error: 'invalid score' });
    const db = loadDb();
    const p = db.players.find(x => x.player_name === s.player_name);
    if (!p) return send(res, 404, { error: 'player not found' });
    p.scores = p.scores || { easy: 0, medium: 0, hard: 0 };
    const updated = !p.scores[mode] || score > p.scores[mode];
    if (updated) p.scores[mode] = score;
    saveDb(db);
    send(res, 200, { ok: true, new_high: updated, high_score: p.scores[mode] });
  },

  'GET /api/scores': async (req, res, url) => {
    const mode = String(url.searchParams.get('mode') || 'easy').toLowerCase();
    if (!GAME_TYPES.includes(mode)) return send(res, 400, { error: 'invalid mode' });
    const db = loadDb();
    const list = db.players
      .map(p => ({ player_name: p.player_name, high_score: (p.scores && p.scores[mode]) || 0 }))
      .filter(x => x.high_score > 0)
      .sort((a, b) => b.high_score - a.high_score)
      .slice(0, 10);
    send(res, 200, { mode, scores: list });
  },
};

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    if (req.method === 'GET' && url.pathname === '/') {
      return send(res, 200, HTML, 'text/html; charset=utf-8');
    }
    const handler = routes[req.method + ' ' + url.pathname];
    if (handler) return await handler(req, res, url);
    send(res, 404, { error: 'not found' });
  } catch (e) {
    send(res, 500, { error: e.message || 'server error' });
  }
});

setInterval(() => {
  const now = Date.now();
  for (const [t, s] of sessions) if (s.expires < now) sessions.delete(t);
}, 60 * 60 * 1000).unref();

server.listen(PORT, () => {
  console.log('retro-snake listening on :' + PORT + '  data=' + DATA_FILE);
});

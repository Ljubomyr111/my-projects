import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const execAsync = promisify(exec);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH = path.join(__dirname, "config.json");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function loadConfig() {
  return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8"));
}

const cfg = loadConfig();
const TG_API = "https://api.telegram.org/bot" + cfg.token;
const FILES_DIR = path.join(__dirname, cfg.filesDir || "files");
const PYTHON = cfg.python || "python";
const EDGE = cfg.edge;
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36";

const conversations = new Map();

function log(...a) {
  console.log(new Date().toISOString(), ...a);
}

// ---------- Telegram ----------
async function tg(method, params) {
  const r = await fetch(`${TG_API}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return r.json();
}

function chunks(s, n = 4000) {
  const out = [];
  for (let i = 0; i < s.length; i += n) out.push(s.slice(i, i + n));
  return out;
}

async function send(chatId, text) {
  for (const c of chunks(String(text))) {
    await tg("sendMessage", { chat_id: chatId, text: c });
  }
}

function isAdmin(chatId) {
  return cfg.adminChatIds.includes(String(chatId));
}

function trim(s, max) {
  s = String(s ?? "");
  if (s.length <= max) return s;
  return s.slice(0, max) + "\n...[обрізано]";
}

function sanitizeFilename(name) {
  return path.basename(String(name)).replace(/[\\/:*?"<>|]/g, "_");
}

// ---------- web ----------
async function fetchText(url, timeoutMs = 20000) {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), timeoutMs);
  try {
    const r = await fetch(url, { headers: { "User-Agent": UA }, redirect: "follow", signal: ac.signal });
    const html = await r.text();
    return { html, contentType: r.headers.get("content-type") || "" };
  } finally {
    clearTimeout(t);
  }
}

function stripHtml(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<noscript[\s\S]*?<\/noscript>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&mdash;/g, "—")
    .replace(/&ndash;/g, "–")
    .replace(/&laquo;/g, "«")
    .replace(/&raquo;/g, "»")
    .replace(/\s+/g, " ")
    .trim();
}

async function webSearch(query) {
  const url = "https://html.duckduckgo.com/html/?q=" + encodeURIComponent(query);
  let html;
  try {
    ({ html } = await fetchText(url));
  } catch (e) {
    return "ERROR: пошук не вдався: " + e.message;
  }
  const results = [];
  const re = /class="result__a"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>[\s\S]*?class="result__snippet"[^>]*>([\s\S]*?)<\/a>/g;
  let m;
  while ((m = re.exec(html)) !== null && results.length < 8) {
    let realUrl = m[1];
    const uddg = m[1].match(/uddg=([^&]+)/);
    if (uddg) realUrl = decodeURIComponent(uddg[1]);
    const title = stripHtml(m[2]);
    const snippet = stripHtml(m[3]);
    if (title) results.push({ title, url: realUrl, snippet: snippet.slice(0, 300) });
  }
  if (results.length === 0) return "(результатів не знайдено)";
  return results.map((r, i) => `${i + 1}. ${r.title}\n   ${r.url}\n   ${r.snippet}`).join("\n\n");
}

async function webFetch(url) {
  let html, contentType;
  try {
    ({ html, contentType } = await fetchText(url));
  } catch (e) {
    return "ERROR: не вдалося завантажити сторінку: " + e.message;
  }
  if (!/text|html|xml|json/i.test(contentType)) {
    return "(не текстове посилання; content-type: " + contentType + ")";
  }
  return stripHtml(html).slice(0, 9000);
}

// ---------- files ----------
function ensureFilesDir() {
  fs.mkdirSync(FILES_DIR, { recursive: true });
}

async function runFile(helper, inputPath, outPath) {
  try {
    const { stdout, stderr } = await execAsync(
      `"${PYTHON}" "${helper}" "${inputPath}" "${outPath}"`,
      { timeout: 90000, maxBuffer: 4 * 1024 * 1024, windowsHide: true }
    );
    const out = (stdout || "").trim();
    const err = (stderr || "").trim();
    if (fs.existsSync(outPath)) return "OK: " + outPath;
    return "FAIL: " + (err || out || "невідома помилка");
  } catch (e) {
    return "FAIL: " + (e.message || "").slice(0, 500);
  }
}

async function saveFile(filename, content) {
  ensureFilesDir();
  const p = path.join(FILES_DIR, sanitizeFilename(filename));
  fs.writeFileSync(p, String(content), "utf8");
  return "OK: збережено " + p;
}

async function makeDocx(filename, markdown) {
  ensureFilesDir();
  const out = path.join(FILES_DIR, sanitizeFilename(filename).replace(/\.docx$/i, "") + ".docx");
  const tmp = path.join(os.tmpdir(), `md_${Date.now()}.md`);
  fs.writeFileSync(tmp, String(markdown), "utf8");
  try {
    return await runFile(path.join(__dirname, "helpers", "make_docx.py"), tmp, out);
  } finally {
    try { fs.unlinkSync(tmp); } catch {}
  }
}

async function makeXlsx(filename, csvOrJson) {
  ensureFilesDir();
  const out = path.join(FILES_DIR, sanitizeFilename(filename).replace(/\.xlsx$/i, "") + ".xlsx");
  const tmp = path.join(os.tmpdir(), `csv_${Date.now()}.txt`);
  fs.writeFileSync(tmp, String(csvOrJson), "utf8");
  try {
    return await runFile(path.join(__dirname, "helpers", "make_xlsx.py"), tmp, out);
  } finally {
    try { fs.unlinkSync(tmp); } catch {}
  }
}

function mdToHtml(md) {
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const inline = (s) => esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
  const lines = String(md).split("\n");
  const out = [];
  let list = null;
  let inCode = false;
  let codeBuf = [];
  const closeList = () => { if (list) { out.push("</" + list + ">"); list = null; } };
  for (const raw of lines) {
    const line = raw;
    if (line.trim().startsWith("```")) {
      if (inCode) { out.push("<pre><code>" + esc(codeBuf.join("\n")) + "</code></pre>"); codeBuf = []; inCode = false; }
      else inCode = true;
      continue;
    }
    if (inCode) { codeBuf.push(line); continue; }
    const h = line.match(/^(#{1,6})\s+(.*)/);
    if (h) { closeList(); out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`); continue; }
    if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) { closeList(); out.push("<hr/>"); continue; }
    const ul = line.match(/^\s*[-*+]\s+(.*)/);
    if (ul) { if (list !== "ul") { closeList(); out.push("<ul>"); list = "ul"; } out.push("<li>" + inline(ul[1]) + "</li>"); continue; }
    const ol = line.match(/^\s*\d+[.)]\s+(.*)/);
    if (ol) { if (list !== "ol") { closeList(); out.push("<ol>"); list = "ol"; } out.push("<li>" + inline(ol[1]) + "</li>"); continue; }
    if (line.trim() === "") { closeList(); continue; }
    closeList();
    out.push("<p>" + inline(line.trim()) + "</p>");
  }
  closeList();
  if (inCode) out.push("<pre><code>" + esc(codeBuf.join("\n")) + "</code></pre>");
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.55; margin: 2cm 1.8cm; color: #141414; }
    h1 { font-size: 1.7em; border-bottom: 2px solid #2b2b2b; padding-bottom: 6px; }
    h2 { font-size: 1.35em; } h3 { font-size: 1.15em; }
    code { background: #f2f2f2; padding: 1px 5px; border-radius: 3px; font-family: Consolas, monospace; }
    pre { background: #f6f6f6; padding: 12px; border-radius: 6px; overflow-x: auto; }
    pre code { background: none; padding: 0; }
    hr { border: none; border-top: 1px solid #ccc; margin: 1.2em 0; }
    a { color: #1a56db; }
  </style></head><body>${out.join("\n")}</body></html>`;
}

async function makePdf(filename, markdown) {
  ensureFilesDir();
  const out = path.join(FILES_DIR, sanitizeFilename(filename).replace(/\.pdf$/i, "") + ".pdf");
  if (!EDGE || !fs.existsSync(EDGE)) return "FAIL: Edge не знайдено для конвертації в PDF";
  const html = mdToHtml(markdown);
  const tmpHtml = path.join(os.tmpdir(), `pdf_${Date.now()}.html`);
  const profile = path.join(os.tmpdir(), `edge_${Date.now()}`);
  fs.writeFileSync(tmpHtml, html, "utf8");
  try {
    await execAsync(
      `"${EDGE}" --headless --disable-gpu --no-first-run --no-default-browser-check --user-data-dir="${profile}" --print-to-pdf="${out}" "${tmpHtml}"`,
      { timeout: 60000, maxBuffer: 2 * 1024 * 1024, windowsHide: true }
    );
    for (let i = 0; i < 20; i++) {
      if (fs.existsSync(out)) break;
      await sleep(500);
    }
    return fs.existsSync(out) ? "OK: " + out : "FAIL: PDF не створено";
  } catch (e) {
    return "FAIL: " + (e.message || "").slice(0, 500);
  } finally {
    try { fs.unlinkSync(tmpHtml); } catch {}
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
  }
}

function listFiles() {
  ensureFilesDir();
  const entries = fs.readdirSync(FILES_DIR).map((name) => {
    const st = fs.statSync(path.join(FILES_DIR, name));
    return { name, size: st.size, modified: st.mtime.toISOString() };
  }).sort((a, b) => (a.modified < b.modified ? 1 : -1));
  if (entries.length === 0) return "(поки що немає файлів)";
  return entries.map((e) => `${e.name} (${e.size} байт)`).join("\n");
}

async function sendFile(chatId, filePath) {
  const p = path.isAbsolute(filePath) ? filePath : path.join(__dirname, filePath);
  if (!fs.existsSync(p)) return "FAIL: файл не знайдено: " + filePath;
  const data = fs.readFileSync(p);
  const fd = new FormData();
  fd.append("chat_id", String(chatId));
  fd.append("document", new Blob([data]), path.basename(p));
  const r = await fetch(`${TG_API}/sendDocument`, { method: "POST", body: fd });
  const j = await r.json();
  return j.ok ? "OK: файл надіслано — " + path.basename(p) : "FAIL: " + JSON.stringify(j).slice(0, 400);
}

// ---------- tools ----------
const TOOLS = [
  { type: "function", function: { name: "web_search", description: "Шукати в інтернеті. Повертає список результатів (назва, URL, фрагмент).", parameters: { type: "object", properties: { query: { type: "string", description: "Пошуковий запит" } }, required: ["query"] } } },
  { type: "function", function: { name: "web_fetch", description: "Завантажити сторінку за URL і повернути її текстовий вміст (до ~9000 символів).", parameters: { type: "object", properties: { url: { type: "string", description: "Повний URL сторінки" } }, required: ["url"] } } },
  { type: "function", function: { name: "save_file", description: "Зберегти текстовий файл (.md, .txt, .csv, .json, .html тощо) з заданим вмістом.", parameters: { type: "object", properties: { filename: { type: "string", description: "Ім'я файла, напр. report.md" }, content: { type: "string", description: "Повний вміст файла" } }, required: ["filename", "content"] } } },
  { type: "function", function: { name: "make_docx", description: "Створити Word-документ (.docx) з Markdown-розмітки (заголовки #, списки -, **жирний**, таблиці |a|b|).", parameters: { type: "object", properties: { filename: { type: "string", description: "Ім'я файла, напр. report.docx" }, markdown: { type: "string", description: "Вміст у Markdown" } }, required: ["filename", "markdown"] } } },
  { type: "function", function: { name: "make_xlsx", description: "Створити Excel-файл (.xlsx) з CSV або JSON (масив рядків чи об'єктів). Перший рядок буде заголовком.", parameters: { type: "object", properties: { filename: { type: "string", description: "Ім'я файла, напр. data.xlsx" }, csv_or_json: { type: "string", description: "Дані у CSV або JSON" } }, required: ["filename", "csv_or_json"] } } },
  { type: "function", function: { name: "make_pdf", description: "Створити PDF з Markdown-розмітки (через headless Edge).", parameters: { type: "object", properties: { filename: { type: "string", description: "Ім'я файла, напр. report.pdf" }, markdown: { type: "string", description: "Вміст у Markdown" } }, required: ["filename", "markdown"] } } },
  { type: "function", function: { name: "send_file", description: "Надіслати створений файл користувачу в Telegram. Використовуй шлях, який повернув інструмент створення (напр. files/report.docx).", parameters: { type: "object", properties: { path: { type: "string", description: "Шлях до файла" } }, required: ["path"] } } },
  { type: "function", function: { name: "list_files", description: "Показати список створених файлів.", parameters: { type: "object", properties: {} } } },
];

async function executeTool(name, args, chatId) {
  switch (name) {
    case "web_search": return await webSearch(args.query || "");
    case "web_fetch": return await webFetch(args.url || "");
    case "save_file": return await saveFile(args.filename || "file.txt", args.content || "");
    case "make_docx": return await makeDocx(args.filename || "report.docx", args.markdown || "");
    case "make_xlsx": return await makeXlsx(args.filename || "data.xlsx", args.csv_or_json || "");
    case "make_pdf": return await makePdf(args.filename || "report.pdf", args.markdown || "");
    case "send_file": return await sendFile(chatId, args.path || "");
    case "list_files": return listFiles();
    default: return "Невідомий інструмент: " + name;
  }
}

// ---------- DeepSeek ----------
async function deepseek(messages, tools) {
  const body = { model: cfg.model || "deepseek-chat", messages, stream: false };
  if (tools) body.tools = tools;
  const r = await fetch(`${cfg.deepseekBaseUrl}/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${cfg.deepseekKey}` },
    body: JSON.stringify(body),
  });
  const j = await r.json();
  if (!r.ok) throw new Error("API: " + ((j?.error?.message || JSON.stringify(j)).slice(0, 400)));
  return j;
}

function trimHistory(hist) {
  const max = cfg.maxHistory || 80;
  if (hist.length <= max) return hist;
  const system = hist[0];
  let rest = hist.slice(-(max - 1));
  while (rest.length && (rest[0].role === "tool" || (rest[0].role === "assistant" && rest[0].tool_calls))) {
    rest = rest.slice(1);
  }
  return [system, ...rest];
}

async function runAgent(chatId, text) {
  if (!cfg.deepseekKey) return "❌ Не задано DeepSeek API-ключ.";
  let hist = conversations.get(String(chatId));
  if (!hist) {
    hist = [{ role: "system", content: cfg.systemPrompt }];
    conversations.set(String(chatId), hist);
  }
  hist.push({ role: "user", content: text });

  for (let step = 0; step < (cfg.maxSteps || 20); step++) {
    const data = await deepseek(trimHistory(hist), TOOLS);
    const msg = data.choices?.[0]?.message;
    if (!msg) return "(порожня відповідь)";
    hist.push(msg);

    if (!msg.tool_calls || msg.tool_calls.length === 0) {
      return msg.content || "(порожня відповідь)";
    }

    for (const tc of msg.tool_calls) {
      let args = {};
      try { args = JSON.parse(tc.function.arguments || "{}"); } catch {}
      log("tool:", tc.function.name, JSON.stringify(args).slice(0, 160));
      let result;
      try {
        result = await executeTool(tc.function.name, args, chatId);
      } catch (e) {
        result = "ERROR: " + e.message;
      }
      hist.push({ role: "tool", tool_call_id: tc.id, content: trim(result, 6000) });
    }
  }
  return "(перевищено ліміт кроків)";
}

// ---------- message handling ----------
const HELP = `🧠 Дослідницький асистент

Просто напиши, що дослідити чи який файл створити, наприклад:
• «Знайди інформацію про X і зроби звіт у Word»
• «Зроби таблицю в Excel: порівняння …»
• «Підготуй PDF-конспект на тему …»
• «Пошукай останні новини про …»

Я сам: шукаю в інтернеті → збираю дані → створюю файл → надсилаю його сюди.

Команди:
/help — це меню
/files — список створених файлів
/id — твій Telegram ID`;

async function handleMessage(msg) {
  const chatId = msg.chat.id;
  const text = (msg.text || "").trim();
  const isPrivate = msg.chat.type === "private";

  if (cfg.adminChatIds.length === 0) {
    if (isPrivate && text) {
      cfg.adminChatIds.push(String(chatId));
      fs.writeFileSync(CONFIG_PATH, JSON.stringify(cfg, null, 2));
      log("OWNER CLAIMED:", chatId);
      await send(chatId, "✅ Тепер ти власник.\n\n" + HELP);
    }
    return;
  }

  if (!isAdmin(chatId)) {
    await send(chatId, "⛔ Доступ заборонено.");
    return;
  }

  if (text === "/start" || text === "/help") { await send(chatId, HELP); return; }
  if (text === "/id") { await send(chatId, `Твій chat_id: ${chatId}`); return; }
  if (text === "/files") { await send(chatId, listFiles()); return; }
  if (text.startsWith("/")) { await send(chatId, "Невідома команда. /help для списку."); return; }

  await tg("sendChatAction", { chat_id: chatId, action: "typing" });
  try {
    const reply = await runAgent(chatId, text);
    await send(chatId, reply);
  } catch (e) {
    log("err:", e.message);
    await send(chatId, "❌ " + e.message);
  }
}

// ---------- poll ----------
async function poll() {
  let offset = 0;
  log("Research bot started. admin:", cfg.adminChatIds);
  while (true) {
    try {
      const r = await fetch(`${TG_API}/getUpdates`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ offset, timeout: 25, allowed_updates: ["message"] }),
      });
      const j = await r.json();
      if (!j.ok) { log("getUpdates error:", JSON.stringify(j)); await sleep(3000); continue; }
      for (const u of j.result) {
        offset = u.update_id + 1;
        if (u.message) {
          log("msg", u.message.chat.id, "|", (u.message.text || "").slice(0, 80));
          await handleMessage(u.message).catch((e) => log("handle err:", e));
        }
      }
    } catch (e) {
      log("poll error:", e.message);
      await sleep(3000);
    }
  }
}

poll();

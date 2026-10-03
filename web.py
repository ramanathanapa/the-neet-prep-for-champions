"""NEET papers & question banks hub: `py web.py` then open http://localhost:8000.
sources.csv is the catalogue (edit it to add links; `file` = local copy under downloads/); `done` ticks are kept in neet.duckdb."""
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer
import duckdb

DB = duckdb.connect("neet.duckdb")
DB.execute("CREATE TABLE IF NOT EXISTS ticks(url VARCHAR PRIMARY KEY)")
try:  # one-off: carry over ticks from the old sources.done column
    DB.execute("INSERT OR IGNORE INTO ticks SELECT url FROM sources WHERE done")
except duckdb.Error:
    pass
DB.execute("CREATE OR REPLACE TABLE sources AS SELECT * FROM read_csv('sources.csv', all_varchar=true)")  # CSV is the source of truth
ROOT = os.path.realpath("downloads")

HUB = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>NEET Paper Hub</title>
<style>body{font:16px system-ui;max-width:860px;margin:auto;padding:16px}select,input{font:inherit;padding:6px;margin:0 6px 8px 0}
h1{font-size:22px}h2{font-size:16px;margin:22px 0 4px;padding-top:8px;border-top:2px solid #ccd}small{color:#666}
.r{display:flex;gap:10px;align-items:baseline;border-bottom:1px solid #eee;padding:6px 0}.r a.t{flex:1}.b{font-size:12px;background:#eef;border-radius:10px;padding:2px 8px;white-space:nowrap}
.d a.t{text-decoration:line-through;color:#888}.o{font-size:12px}</style>
<h1>NEET papers &amp; question banks</h1>
<small>Papers are paired with their answer keys per exam code. Local copies open from the <b>downloads/</b> folder; "original" goes to the source site.</small><br><br>
<select id=y></select><select id=p></select><select id=k></select><input id=s placeholder="search">
<div id=l></div>
<script>
let S=[];const f=['y','p','k'],key={y:'year',p:'publisher',k:'kind'};
fetch('/api/sources').then(r=>r.json()).then(d=>{S=d;f.forEach(i=>{const e=document.getElementById(i);
 e.innerHTML='<option value="">all '+key[i]+'s</option>'+[...new Set(S.map(x=>x[key[i]]))].map(v=>`<option>${v}</option>`).join('');e.onchange=draw});s.oninput=draw;draw()});
function draw(){const q=s.value.toLowerCase(),L=document.getElementById('l');L.textContent='';let g='';
 S.filter(x=>f.every(i=>!document.getElementById(i).value||x[key[i]]==document.getElementById(i).value)&&x.title.toLowerCase().includes(q)).forEach(x=>{
  const gl=x.code?`NEET ${x.year} · Code ${x.code}`:`${x.year} · More resources`;
  if(gl!=g){g=gl;const h=document.createElement('h2');h.textContent=g;L.append(h)}
  const r=document.createElement('div');r.className='r'+(x.done?' d':'');
  const a=document.createElement('a');a.className='t';a.href=x.local?'/files/'+x.local:x.url;a.target='_blank';a.rel='noopener';a.textContent=x.title+(x.local?'':' ↗');
  const b=document.createElement('span');b.className='b';b.textContent=x.kind+' · '+x.publisher;
  const c=document.createElement('input');c.type='checkbox';c.checked=x.done;c.title='done';
  c.onchange=()=>{x.done=c.checked;r.className='r'+(x.done?' d':'');fetch('/api/done',{method:'POST',body:JSON.stringify({url:x.url,done:x.done})})};
  r.append(a,b);if(x.local){const o=document.createElement('a');o.className='o';o.href=x.url;o.target='_blank';o.rel='noopener';o.textContent='original ↗';r.append(o)}
  r.append(c);L.append(r)})}
</script>"""


class H(BaseHTTPRequestHandler):
    def send(self, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(200); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/sources":
            rows = DB.execute("""SELECT s.url,s.year,s.code,s.publisher,s.kind,s.title,s.file,t.url IS NOT NULL FROM sources s LEFT JOIN ticks t USING(url)
                ORDER BY s.year = 'all years', s.year DESC, s.code = '', s.code, CASE s.kind WHEN 'question paper' THEN 0 WHEN 'paper + solutions' THEN 1
                WHEN 'answer key + solutions' THEN 2 ELSE 3 END, s.title""").fetchall()
            self.send(json.dumps([dict(url=u, year=y, code=c, publisher=p, kind=k, title=t, done=d,
                                       local=f if f and os.path.exists(os.path.join(ROOT, f)) else "") for u, y, c, p, k, t, f, d in rows]))
        elif self.path.startswith("/files/"):
            p = os.path.realpath(os.path.join(ROOT, self.path[7:].replace("%20", " ")))
            if os.path.commonpath([p, ROOT]) == ROOT and os.path.isfile(p):  # stay inside downloads/
                self.send(open(p, "rb").read(), "application/pdf")
            else:
                self.send_error(404)
        else:
            self.send(HUB, "text/html; charset=utf-8")

    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/api/done":
            DB.execute("INSERT OR IGNORE INTO ticks VALUES (?)" if d["done"] else "DELETE FROM ticks WHERE url=?", [d["url"]])
        self.send("{}")


if __name__ == "__main__":
    print("Open http://localhost:8000")
    HTTPServer(("127.0.0.1", 8000), H).serve_forever()  # ponytail: single-user, single-threaded (DuckDB conn is shared)

import base64
import json
import os
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
import yaml

def b64(v):
    return base64.urlsafe_b64encode(str(v).encode()).decode().rstrip("=")

def uri(p):
    typ = str(p.get("type", "")).lower()
    name = quote(str(p.get("name", "Unnamed")), safe="")
    server, port = p.get("server"), p.get("port")
    if not server or not port:
        return None
    host = str(server)
    host = "[" + host + "]" if ":" in host and not host.startswith("[") else host
    if typ == "ss":
        cipher, password = p.get("cipher") or p.get("method"), p.get("password")
        if not cipher or password is None:
            return None
        return "ss://" + b64(cipher + ":" + str(password)) + "@" + host + ":" + str(port) + "#" + name
    if typ == "vmess":
        if not p.get("uuid"):
            return None
        network = p.get("network", "tcp")
        ws, grpc = p.get("ws-opts") or {}, p.get("grpc-opts") or {}
        info = {"v":"2", "ps":p.get("name", ""), "add":str(server), "port":str(port),
                "id":p["uuid"], "aid":str(p.get("alterId", 0)), "scy":p.get("cipher", "auto"),
                "net":network, "type":"none", "host":(ws.get("headers") or {}).get("Host", "") if network == "ws" else "",
                "path":ws.get("path", "/") if network == "ws" else grpc.get("grpc-service-name", "") if network == "grpc" else "",
                "tls":"tls" if p.get("tls") else "", "sni":p.get("servername", "")}
        return "vmess://" + b64(json.dumps(info, ensure_ascii=False, separators=(",", ":")))
    if typ in ("trojan", "vless"):
        key = p.get("password") if typ == "trojan" else p.get("uuid")
        if not key:
            return None
        params = {"security":"tls" if p.get("tls", typ == "trojan") else "none"}
        if p.get("sni") or p.get("servername"):
            params["sni"] = p.get("sni") or p["servername"]
        network = p.get("network")
        if network:
            params["type"] = network
        if network == "ws":
            ws = p.get("ws-opts") or {}
            if ws.get("path"):
                params["path"] = ws["path"]
            if (ws.get("headers") or {}).get("Host"):
                params["host"] = ws["headers"]["Host"]
        if typ == "vless":
            params["encryption"] = "none"
            if p.get("flow"):
                params["flow"] = p["flow"]
        return typ + "://" + quote(str(key), safe="") + "@" + host + ":" + str(port) + "?" + urlencode(params) + "#" + name
    return None

def parse(data):
    # Support both Clash YAML and simple share-link subscriptions.
    try:
        document = yaml.safe_load(data)
    except yaml.YAMLError:
        document = None
    if isinstance(document, dict) and isinstance(document.get("proxies"), list):
        nodes = document["proxies"]
    elif isinstance(document, list):
        nodes = document
    else:
        allowed = ("ss://", "vmess://", "trojan://", "vless://")
        links = [x.strip() for x in data.splitlines() if x.strip().startswith(allowed)]
        if not links:
            try:
                decoded = base64.b64decode("".join(data.split()) + "===").decode()
                links = [x.strip() for x in decoded.splitlines() if x.strip().startswith(allowed)]
            except (ValueError, UnicodeError):
                pass
        if not links and "[Proxy]" in data:
            # Surge-style subscriptions: convert the common SS node syntax.
            section = False
            for raw_line in data.splitlines():
                line = raw_line.strip()
                if line.startswith("[") and line.endswith("]"):
                    section = (line.lower() == "[proxy]")
                    continue
                if not section or not line or line.startswith(("#", ";")) or "=" not in line:
                    continue
                name, settings = line.split("=", 1)
                parts = [x.strip() for x in settings.split(",")]
                if len(parts) < 3 or parts[0].lower() != "ss":
                    continue
                options = dict(x.split("=", 1) for x in parts[3:] if "=" in x)
                entry = {"type":"ss", "name":name.strip(), "server":parts[1], "port":parts[2],
                         "cipher":options.get("encrypt-method"), "password":options.get("password")}
                link = uri(entry)
                if link:
                    links.append(link)
        if not links:
            raise ValueError("No supported share links or Clash/Surge proxies")
        return list(dict.fromkeys(links))
    links = list(dict.fromkeys(x for x in (uri(p) for p in nodes if isinstance(p, dict)) if x))
    if not links:
        raise ValueError("No supported nodes found")
    return links

def main():
    folder = Path("site")
    folder.mkdir(exist_ok=True)
    for key, filename in (("CLASH_SUB_URL", "clash.txt"), ("OTHER_SUB_URL", "other.txt")):
        source = os.getenv(key, "").strip()
        if not source:
            raise ValueError("Missing repository secret: " + key)
        with urlopen(Request(source, headers={"User-Agent":"Clash/1.18.0"}), timeout=45) as response:
            raw = response.read(5000001)
        if len(raw) > 5000000:
            raise ValueError("Subscription too large")
        links = parse(raw.decode("utf-8-sig"))
        content = base64.b64encode(("\n".join(links) + "\n").encode()).decode()
        (folder / filename).write_text(content + "\n", encoding="utf-8")
        print(filename + ": converted " + str(len(links)) + " nodes")
    (folder / "index.html").write_text(
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow"><title>订阅服务</title>'
        '<style>body{font:16px system-ui,sans-serif;max-width:540px;margin:15vh auto;padding:20px}'
        'a{display:block;margin:12px 0;padding:12px;border:1px solid #ddd;border-radius:8px;color:inherit;text-decoration:none}</style>'
        '</head><body><h2>订阅服务</h2><p>v2rayN 节点订阅</p>'
        '<a href="./clash.txt">Clash</a><a href="./other.txt">Other</a></body></html>', encoding="utf-8")
    (folder / ".nojekyll").write_text("", encoding="utf-8")

if __name__ == "__main__":
    main()

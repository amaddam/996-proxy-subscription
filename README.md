# Subscription converter

GitHub Actions fetches two upstream subscriptions every six hours, converts them into static v2rayN share-link subscriptions, and deploys the generated files to Cloudflare Workers Static Assets. No Worker JavaScript runs when clients download the static files.

## One-time setup

### GitHub repository secrets

Open **Settings → Secrets and variables → Actions** and add:

- `CLASH_SUB_URL`: `https://996chat.com/ClashRPzlPmfQIB8s.yaml`
- `OTHER_SUB_URL`: `https://996chat.com/otherROk20sM4l5.yaml`
- `CF_ACCOUNT_ID`: your Cloudflare Account ID.
- `CF_API_TOKEN`: a Cloudflare API token permitted to deploy Workers (Workers Scripts: Edit, plus required account-level Workers permissions).

### Cloudflare

1. In Cloudflare, create a Workers project named `proxy-subscription-996`, or let the first Wrangler deployment create it.
2. Ensure the account has a `workers.dev` subdomain enabled.
3. The repository contains `wrangler.jsonc`, configured for static assets in `./site`.

### Deploy

Run **Actions → Update subscriptions → Run workflow**, or wait for the six-hour schedule. The workflow converts the inputs and deploys `site/` using Wrangler.

The expected URLs are:

- `https://proxy-subscription-996.<your-workers-subdomain>.workers.dev/clash.txt`
- `https://proxy-subscription-996.<your-workers-subdomain>.workers.dev/other.txt`

Add these URLs to v2rayN as ordinary subscriptions; leave v2rayN's subscription conversion target unset.

## Supported inputs

- Clash YAML with a `proxies` list: SS, VMess, Trojan, VLESS.
- Surge-style `[Proxy]` lines for Shadowsocks.
- Plain or Base64-encoded share-link subscriptions.

**Security:** The generated Base64 subscriptions contain recoverable proxy credentials and are publicly accessible. Keeping upstream URLs in GitHub Secrets does not make the published node credentials private. Do not share the output URLs if you do not want others to use the nodes.

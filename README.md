# Subscription converter

GitHub Actions fetches two upstream subscriptions every six hours, converts them into static v2rayN share-link subscriptions, and deploys the generated files to Cloudflare Workers Static Assets. Static asset requests are served without invoking Worker JavaScript.

## One-time setup

### 1. Cloudflare Worker

Create a Worker named `proxy-subscription-996` in your Cloudflare account and make sure your `workers.dev` subdomain is enabled. The repository's `wrangler.jsonc` deploys the `site/` directory as static assets.

### 2. Cloudflare API credentials

Create an API token at https://dash.cloudflare.com/profile/api-tokens. For the first deployment (which creates or updates the Worker), use the **Edit Cloudflare Workers** template, scoped to the account that owns the Worker. If you create the Worker manually first, a narrower Workers Editor token scoped to that Worker can be used.

Find the Account ID in the Cloudflare dashboard.

### 3. GitHub repository secrets

Open **Settings → Secrets and variables → Actions** and add:

- `CLASH_SUB_URL`: `https://996chat.com/ClashRPzlPmfQIB8s.yaml`
- `OTHER_SUB_URL`: `https://996chat.com/otherROk20sM4l5.yaml`
- `CLOUDFLARE_ACCOUNT_ID`: your Cloudflare Account ID.
- `CLOUDFLARE_API_TOKEN`: the Cloudflare API token.

Never put the API token or upstream subscription URLs in committed files.

## Deploy

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

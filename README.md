# Subscription converter

Every six hours, GitHub Actions converts two upstream subscriptions to static v2rayN node subscriptions, then publishes them to GitHub Pages.

## One-time setup

1. Open **Settings → Secrets and variables → Actions** and create these repository secrets:
   - `CLASH_SUB_URL`: original Clash YAML URL.
   - `OTHER_SUB_URL`: second original subscription URL.
2. Open **Settings → Pages → Build and deployment**; choose **GitHub Actions** as Source.
3. Run **Actions → Update subscriptions → Run workflow**.
4. Add the GitHub Pages links ending with `/clash.txt` and `/other.txt` to v2rayN. Leave subscription conversion target **unset**.

The published page itself has no repository link or author name. The default GitHub Pages URL still includes the account name. Use a custom domain to hide that name in the URL.

**Security:** Published node subscriptions contain recoverable credentials. They are publicly readable, despite upstream URLs living in GitHub Secrets. Supports Clash SS, VMess, Trojan and VLESS plus plain share-link subscriptions. Unsupported nodes are skipped; conversion failure prevents replacing the previously published site.

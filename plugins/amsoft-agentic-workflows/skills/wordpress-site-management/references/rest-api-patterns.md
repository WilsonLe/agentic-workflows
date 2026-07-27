# WordPress REST API patterns

## Authentication

Prefer HTTPS and the authentication method already configured by the site. For core Application
Passwords, use an environment or secret-manager reference for the username and Application
Password. Never print authorization headers, enable verbose HTTP traces containing credentials, or
store credentials in URLs, source files, shell history, logs, or artifacts.

If a site uses JWT, OAuth, cookie/nonces, or a plugin/hosting API, inspect its current documented
contract. Do not reinterpret one credential type as another.

## Discovery

1. Read the REST index at `/wp-json/`.
2. Identify content types and taxonomies from the REST index and WordPress type endpoints.
3. Use `OPTIONS` or the route schema to confirm allowed methods, required fields, and capabilities.
4. Use authenticated edit context when raw source or protected metadata is required.
5. Narrow collections with supported filters and pagination; do not download the whole site
   unnecessarily.

Endpoint availability varies by WordPress version, theme, plugins, capabilities, and registration
settings. Custom post types, fields, menus, SEO metadata, multilingual content, templates, plugins,
and themes may be read-only, omitted, or managed by custom namespaces.

## Safe writes

1. Resolve the exact object by stable ID.
2. Fetch its editable representation and record modified time, status, slug, link, and the fields
   being changed.
3. Refetch just before writing. Stop if it changed unexpectedly.
4. Send only the intended fields rather than replaying an entire stale object.
5. Keep new or uncertain content in draft status.
6. Re-fetch and compare the response to the requested change.
7. Verify the preview or public URL in a browser.

For media, confirm file type, size, rights, dimensions, filename, title, caption, and purpose-based
alt text. Verify generated sizes and rendering after upload.

## Failure handling

- Treat `401` as missing or invalid authentication and `403` as an authorization or policy
  boundary; do not repeatedly retry credentials.
- Treat `404` as possibly an unregistered route, permalink/proxy issue, or hidden resource; inspect
  the REST index before assuming absence.
- Respect rate limits and hosting security controls.
- Do not bypass WAF, two-factor authentication, CAPTCHA, or security plugins.
- Sanitize response excerpts before reporting them because plugin endpoints may return private
  configuration or user data.

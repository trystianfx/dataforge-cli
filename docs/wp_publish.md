# Publish (WordPress)

Pushes a rendered HTML file to WordPress as a new post or page via the
REST API. Draft-first by design: nothing here ever auto-publishes or
deletes content.

## Prerequisites

1. In WP Admin, go to **Users > Profile > Application Passwords** and
   generate one for the account you'll publish as.
2. Have a rendered HTML file ready (e.g. `output/repeaters/index.html`
   from `dataforge build`).

## CLI usage

```bash
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

dataforge wp-push output/repeaters/index.html \
  --site https://your-site.example.com \
  --username your-wp-username \
  --title "US & Global Metro Repeater Directory" \
  --status draft
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--site` | required | WordPress base URL (e.g. `https://example.com`) |
| `--username` | required | WordPress username |
| `--app-password` | env var `WP_APP_PASSWORD` | Application Password; pass via env var rather than the command line to avoid it landing in shell history |
| `--title` | required | Title for the new post/page |
| `--status` | `draft` | `draft`, `pending`, or `publish` |
| `--post-type` | `posts` | `posts` or `pages` |

`html_file` is a positional argument (the path to the rendered HTML), not
a flag.

## Python API

```python
from pathlib import Path
from dataforge.wp_publish import WordPressConfig, push_html_as_post, WordPressPublishError

config = WordPressConfig(
    base_url="https://your-site.example.com",
    username="your-wp-username",
    app_password="xxxx xxxx xxxx xxxx xxxx xxxx",
)

html_content = Path("output/repeaters/index.html").read_text(encoding="utf-8")

try:
    result = push_html_as_post(
        config,
        title="US & Global Metro Repeater Directory",
        html_content=html_content,
        status="draft",
        post_type="posts",
    )
    print(result["id"], result["link"])
except WordPressPublishError as e:
    print(f"WordPress rejected the request: {e}")
```

## Static embed alternative (no WordPress credentials needed)

`dataforge build` output is plain static HTML/CSS -- you don't need this
module at all if you'd rather:

- Paste the relevant markup into a WordPress **Custom HTML block**.
- Serve the generated folder from your own web server and `<iframe>` it
  into a page.
- `include()` a rendered fragment directly from a PHP theme file (see the
  "Custom templates" example in [render.md](render.md)).

## Working example: publish then leave it as a draft for review

```python
from dataforge.wp_publish import WordPressConfig, push_html_as_post

config = WordPressConfig(base_url="https://example.com", username="ops", app_password="...")
result = push_html_as_post(
    config,
    title="Weekly Repeater Snapshot",
    html_content=open("output/repeaters/index.html").read(),
    status="draft",   # always review in wp-admin before publishing
)
print(f"Draft created: {result['link']}")
```

## See also

- [WordPress REST API Handbook -- Posts](https://developer.wordpress.org/rest-api/reference/posts/) -- for fields beyond `title`/`content`/`status` (categories, tags, featured media, custom meta) that `push_html_as_post` doesn't currently set. If you need those, call the REST API directly with `requests` using the same `WordPressConfig.api_root` / Application Password auth pattern this module uses.

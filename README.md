# meteo-imgw — IMGW nowcasting videos for Home Assistant

The „Produkty specjalne" section of <https://meteo.imgw.pl/> embeds two
looping nowcasting videos:

- **INCA – temperatura** (`inca_t2m`)
- **MERGE – suma opadów** (`merge`)

The mp4 filenames carry a publication timestamp that changes with every
republish (roughly hourly), so hardcoding them breaks quickly. This repo
extracts the current links straight from the JSON API the Angular site itself
uses — no browser, no scraping of the rendered DOM.

```
GET https://meteo.imgw.pl/api/v1/products/cmm-maps
    ?token=<public apiToken>&products[0]=merge&products[1]=inca_t2m

{ "data": {
    "merge":    { "modifiedTime": 1794514687, "image": "/cmm_img/MERGE_1794514687.mp4" },
    "inca_t2m": { "modifiedTime": 1794511403, "image": "/cmm_img/INCA_T2M_1794511403.mp4" } } }
```

## Files

| Path | Purpose |
|---|---|
| `www/imgw_video.html` | Self-refreshing video page. Copy to `<config>/www/` in Home Assistant, then embed as `/local/imgw_video.html?embed=1`. Works standalone too — open the file in a browser directly. |
| `lovelace/imgw_tab.yaml` | Lovelace view (tab) using the built-in Webpage (`type: iframe`) card. |
| `imgw_video.py` | Stdlib-only CLI: prints/downloads the current mp4 URLs for scripting. |

## Home Assistant setup

1. Copy `www/imgw_video.html` into the `www` folder of the HA config directory
   (served at `/local/imgw_video.html`, no restart required):

   ```sh
   mkdir -p /config/www && cp www/imgw_video.html /config/www/
   ```

2. Add a tab: **Edit dashboard → + Add card → Webpage**, URL:
   `/local/imgw_video.html?embed=1&v=1`
   — or use `lovelace/imgw_tab.yaml` (YAML-managed dashboard). A
   `panel: true` view makes the video fill the whole tab.

The page re-fetches the API every 10 minutes, so new videos appear by
themselves; `?embed=1` (also auto-detected inside iframes) hides its own
header/toolbar and it inherits HA theme colors, since the iframe is
same-origin and the fetch is allowed by IMGW's `access-control-allow-origin: *`.

## CLI

```sh
./imgw_video.py                # both URLs, one per line
./imgw_video.py inca           # only the INCA video
./imgw_video.py --json         # URLs + publication timestamps
./imgw_video.py --download-dir /tmp/vids   # download too
```

## Notes

- The JSON fetch runs in the *browser* showing the dashboard — that device
  needs internet; HA only serves one static file.
- After editing the HTML in `www/`, bump the `v=` parameter in the card URL to
  bypass browser cache.
- If IMGW rotates the public `apiToken` baked into the page, re-extract it:

  ```sh
  curl -s https://meteo.imgw.pl/ | grep -o 'main\.[a-f0-9]*\.js' |
    xargs -I{} curl -s https://meteo.imgw.pl/{} | grep -o 'apiToken:"[^"]*"'
  ```

Data © IMGW-PIB, offered for reuse as public sector information
(<https://danepubliczne.imgw.pl/apiinfo>).

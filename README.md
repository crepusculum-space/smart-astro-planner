# Smart Astro Planner

A single-file progressive web app for astrophotography planning. It answers *"what are my options over
the next few weeks?"* from an amateur's backyard — partial horizon, few clear nights, limited hours per
target — using a local catalog of 19,092 deep-sky objects, real sky images for framing, and (optionally)
the Claude API for descriptions and capture advice.

It is a planning aid, not a replacement for tools like Telescopius or SkySafari: validate a target there
before committing several nights to it.

No build step, no framework. Everything is in `index.html`.

## Run it locally

```
python3 -m http.server 8080
```

Then open http://localhost:8080. Do not open `index.html` through `file://` (the catalog fetch and the
service worker need HTTP).

## License

Copyright (c) 2026 Crepusculum.

- **Code, help, icons and screenshots** — [CC BY-NC-SA 4.0](LICENSE). You may copy, fork, modify and
  publish it, but you must credit Crepusculum, indicate your changes, keep the same license, and not use
  it commercially.
- **`catalog.json`** — [CC BY-SA 4.0](LICENSE-CATALOG), because it is derived from
  [OpenNGC](https://github.com/mattiaverga/OpenNGC).
- **Third-party material** — see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

When you publish a fork, a line such as *"Based on Smart Astro Planner by Crepusculum
(crepusculum.space)"* in your README and in the app's About section satisfies the credit requirement.

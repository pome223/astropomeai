# Astropome AI research library

An English research collection at [astropomeai.com](https://astropomeai.com/), published with GitHub Pages from `main` at the repository root.

The collection covers MissionOS governance, manipulation, stacking, quadruped delivery, urban flight, landing decisions, maritime missions, spacecraft simulation, and computational studies of DNA replication. Articles use paper-style abstracts, methods, results, discussion, limitations, and linked evidence. They are technical research articles, not peer-reviewed publications.

## Edit and build

Edit an article in `content/articles/`. Each JSON source contains its metadata, abstract, section HTML, and references. Biology evidence summaries are reviewed, portable supplements under `content/evidence/`.

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 18773 --bind 127.0.0.1
```

With the server running, verify actual HTTP delivery:

```sh
python3 scripts/check.py --url http://127.0.0.1:18773
```

The generator uses only the Python standard library. Commit the generated `index.html`, `research/*/index.html`, and sitemap alongside their sources. GitHub Pages serves these files directly; there is no client-side content fetch or production build dependency. `.nojekyll` keeps the output unchanged. Preserve `CNAME` and the existing domain configuration.

## Editorial and evidence rules

- Cite public MissionOS reports at a fixed commit. The first edition uses public `main` at `7f0128491ac1e998c05580b50707ee8cab7543c6`.
- Distinguish proposals, human approval, constrained dispatch, execution, and verification.
- State simulator, synthetic, and empirical evidence separately, with denominators and comparator limitations.
- Include negative results; do not turn model invocation or integration into evidence of improved outcomes.
- Biology supplements are curated from saved study records. They are not a claim that the complete original raw artifacts are publicly reproducible.
- Do not add local paths, private repositories, raw logs, credentials, or unreviewed experiment artifacts.
- Verify links, narrow-screen layout, keyboard navigation, search/filter behavior, and deployed pages when publishing.

## Videos and figures

Five articles include 12 inline MP4 recordings and 15 still figures in total. A structured `media` array places recordings and galleries alongside the relevant article sections. All recordings are source-verified H.264 copies with posters, native playback controls, inline mobile playback, and `preload="none"`. There is no autoplay. Selecting a gallery figure opens a keyboard-accessible enlargement; without JavaScript, the link opens the full-size image. The homepage features three recorded experiments.

Media files and their hashes are listed in `assets/media/provenance.json`; source attribution is retained alongside them. Videos have scenario-specific captions that distinguish recorded simulation, generated prediction, playback compression, and separate research cohorts.

The existing Medium and note links remain in the site navigation/footer. Original background image assets are retained in the repository.

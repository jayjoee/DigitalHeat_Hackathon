# Presentation

| Path | Contents |
|---|---|
| [DigitalHeat_Pitch.mp4](DigitalHeat_Pitch.mp4) | Pitch video, 720p, 5:17, English |
| [DigitalHeat_slides.pdf](DigitalHeat_slides.pdf) | The slides used in the video |
| [SCRIPT.md](SCRIPT.md) | Narration script |
| [video/](video/) | Code that renders the video from the 3D dashboard |
| [stage/](stage/) | Code of the local stage presentation |

Nothing in this folder is needed to run the prototype. Use the [main README](../README.md) for that.

The narration is an ElevenLabs AI voice. The code was written during the sprint with Claude Code.

## What is real in the video

- The March docking run plays back the status log of a real AutoDock Vina process that the scheduler paused and resumed (`video/runs/live/states.json`).
- The May handover is a recording of two processes on one laptop. Its docking scores and router decision are replayed, the checkpoint transfer is live.
- Homes, heat, servers, demand and money come from the simulation in this repository.
- The boiler illustration, explanation panels, captions, camera moves and softened LED flicker were added for the film. The beam from the ML forecast to the router is hidden, because the forecast does not steer the router.

## Render film stills

Requires Node.js and Playwright with Chromium.

```sh
cd presentation/video
npm install --no-save --no-package-lock playwright
npx playwright install chromium
node tools/film/render.js stills /tmp/film-stills 23 70 240
```

The stills work from a fresh clone. A complete re-render of the video also needs the screen recordings of the handover and the voice track, which are not committed because of their size. The finished video contains both. `node tools/capture-runs.js runs` records new runs and requires Vina. `tools/film/encode.swift` and `tools/mux.swift` encode and add the audio on macOS.

## Stage presentation

`stage/` is source only: a local slide player (`stage/stage/`) that starts the real docking job during the pitch, and the script that cuts the short stage video (`stage/build/`). It expects the cut videos, slide images and a copy of this repository next to it, which are not committed.

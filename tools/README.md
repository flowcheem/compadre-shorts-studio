# Subject tracking prototype (v0.3)

The first v0.3 component is a local macOS helper based on Apple Vision.

## What it does

- Samples a source video at a configurable interval (default: 0.25 seconds).
- Runs `VNDetectHumanRectanglesRequest` on each sampled frame.
- Chooses an initial candidate using size and centrality.
- Attempts to keep the same candidate by comparing overlap and center distance with the previous detection.
- Writes normalized bounding boxes and confidence values to JSON.
- Records missed detections instead of pretending a person was found.

## Run locally on macOS

From the repository root:

```bash
swift tools/subject_scan.swift "/path/to/gameplay.mp4" "/path/to/subject_scan.json" 0.25
```

No video is uploaded. The helper reads the local video through AVFoundation and uses the system Vision framework.

## Important limitation

Vision detects human-shaped regions; it does not know which GTA V character is the player. Pedestrians, enemies, and other NPCs can be selected. The temporal matching is a first heuristic, not identity recognition. Inspect the JSON and test against representative frames before using its data to crop a finished Short.

## Next integration step

Convert the selected normalized boxes into a smoothed horizontal crop path for FFmpeg. If detections are unreliable, use a safe full-frame vertical layout (fit the complete 16:9 image inside a 9:16 canvas with a blurred background) rather than forcing a tight crop. Preserve the existing viral grade and audio normalization filters.

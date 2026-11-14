import Foundation
import AVFoundation
import Vision
import ImageIO

struct Detection: Codable {
    let time: Double
    let x: Double
    let y: Double
    let width: Double
    let height: Double
    let confidence: Double
    let selected: Bool
}

struct Output: Codable {
    let source: String
    let sampleInterval: Double
    let detections: [Detection]
    let warning: String
}

func intersectionOverUnion(_ a: CGRect, _ b: CGRect) -> Double {
    let intersection = a.intersection(b)
    if intersection.isNull || intersection.isEmpty { return 0 }
    let unionArea = a.width * a.height + b.width * b.height - intersection.width * intersection.height
    return unionArea > 0 ? (intersection.width * intersection.height) / unionArea : 0
}

func rect(_ observation: VNHumanObservation) -> CGRect {
    observation.boundingBox
}

func run() throws {
    let args = CommandLine.arguments
    guard args.count >= 3 else {
        fputs("Usage: subject_scan <video> <output.json> [sample_interval]\n", stderr)
        exit(2)
    }
    let input = URL(fileURLWithPath: args[1])
    let outputURL = URL(fileURLWithPath: args[2])
    let interval = args.count >= 4 ? max(0.10, Double(args[3]) ?? 0.25) : 0.25

    let asset = AVURLAsset(url: input)
    let duration = asset.duration.seconds
    guard duration.isFinite && duration > 0 else {
        throw NSError(domain: "CompadreSubjectScan", code: 1,
                      userInfo: [NSLocalizedDescriptionKey: "Could not read video duration"])
    }

    let generator = AVAssetImageGenerator(asset: asset)
    generator.appliesPreferredTrackTransform = true
    generator.maximumSize = CGSize(width: 960, height: 960)

    var detections: [Detection] = []
    var previousRect: CGRect? = nil
    var previousCenter = CGPoint(x: 0.5, y: 0.5)
    var lostSamples = 0
    let request = VNDetectHumanRectanglesRequest()
    request.upperBodyOnly = false

    var time = 0.0
    while time < duration {
        let cmTime = CMTime(seconds: time, preferredTimescale: 600)
        do {
            let image = try generator.copyCGImage(at: cmTime, actualTime: nil)
            let handler = VNImageRequestHandler(cgImage: image, options: [:])
            try handler.perform([request])
            // VNDetectHumanRectanglesRequest does not expose minimumConfidence
            // or maximumObservations. Filter its observations after performing it.
            let candidates = (request.results ?? []).filter { $0.confidence >= 0.35 }
            var chosen: VNHumanObservation? = nil

            if let previous = previousRect, lostSamples < 5 {
                let ranked = candidates.map { candidate -> (VNHumanObservation, Double) in
                    let box = rect(candidate)
                    let center = CGPoint(x: box.midX, y: box.midY)
                    let distance = hypot(center.x - previousCenter.x, center.y - previousCenter.y)
                    let overlap = intersectionOverUnion(previous, box)
                    let score = overlap * 2.0 - distance * 1.25 + Double(candidate.confidence) * 0.15
                    return (candidate, score)
                }.sorted { $0.1 > $1.1 }
                if let best = ranked.first, best.1 > -0.25 {
                    chosen = best.0
                }
            }

            if chosen == nil && (previousRect == nil || lostSamples >= 5) {
                // Initial selection: prefer a large, reasonably central person.
                chosen = candidates.max { a, b in
                    let ar = rect(a), br = rect(b)
                    let ac = hypot(ar.midX - 0.5, ar.midY - 0.5)
                    let bc = hypot(br.midX - 0.5, br.midY - 0.5)
                    let ascore = ar.width * ar.height * (1.0 - min(0.8, ac))
                    let bscore = br.width * br.height * (1.0 - min(0.8, bc))
                    return ascore < bscore
                }
            }

            if let observation = chosen {
                let box = rect(observation)
                previousRect = box
                previousCenter = CGPoint(x: box.midX, y: box.midY)
                lostSamples = 0
                detections.append(Detection(
                    time: time, x: box.origin.x, y: box.origin.y,
                    width: box.width, height: box.height,
                    confidence: Double(observation.confidence), selected: true
                ))
            } else {
                lostSamples += 1
                detections.append(Detection(
                    time: time, x: 0, y: 0, width: 0, height: 0,
                    confidence: 0, selected: false
                ))
            }
        } catch {
            lostSamples += 1
            detections.append(Detection(
                time: time, x: 0, y: 0, width: 0, height: 0,
                confidence: 0, selected: false
            ))
        }
        time += interval
    }

    let result = Output(
        source: input.path,
        sampleInterval: interval,
        detections: detections,
        warning: "Vision detects people, not GTA's player identity. Review tracking; NPCs may be selected."
    )
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    try encoder.encode(result).write(to: outputURL, options: .atomic)
    print("Saved \(detections.count) samples to \(outputURL.path)")
}

try run()

// cut <in.mp4> <out.mp4> <bitrate> <width> <height> <start> <end> [<start> <end> ...]
// Joins the parts with a short cross-fade of picture and sound.
import AVFoundation

let a = CommandLine.arguments
let input = AVURLAsset(url: URL(fileURLWithPath: a[1]), options: [AVURLAssetPreferPreciseDurationAndTimingKey: true])
let out = URL(fileURLWithPath: a[2])
let rate = Int(a[3])!, width = Int(a[4])!, height = Int(a[5])!
let numbers = a[6...].map { Double($0)! }
let parts = stride(from: 0, to: numbers.count, by: 2).map { (numbers[$0], numbers[$0 + 1]) }
let fade = 0.36
func tm(_ s: Double) -> CMTime { CMTime(value: Int64((s * 48000).rounded()), timescale: 48000) }

let comp = AVMutableComposition()
let srcV = input.tracks(withMediaType: .video)[0], srcA = input.tracks(withMediaType: .audio)[0]
let vs = (0..<2).map { _ in comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)! }
let aus = (0..<2).map { _ in comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)! }
let mix = aus.map { AVMutableAudioMixInputParameters(track: $0) }
var at: [Double] = [], cursor = 0.0
for (i, p) in parts.enumerated() {
  let r = CMTimeRange(start: tm(p.0), end: tm(p.1)), n = i % 2
  // HOLD="<part>:<seconds>": that part opens on the settled picture, so a removed scene does not flash up.
  let hold = ProcessInfo.processInfo.environment["HOLD"]?.split(separator: ":").map { Double($0)! } ?? [-1, 0]
  if Int(hold[0]) == i {
    try vs[n].insertTimeRange(CMTimeRange(start: tm(p.0 + hold[1]), duration: tm(1.0 / 30)), of: srcV, at: tm(cursor))
    vs[n].scaleTimeRange(CMTimeRange(start: tm(cursor), duration: tm(1.0 / 30)), toDuration: tm(hold[1]))
    try vs[n].insertTimeRange(CMTimeRange(start: tm(p.0 + hold[1]), end: tm(p.1)), of: srcV, at: tm(cursor + hold[1]))
  } else {
    try vs[n].insertTimeRange(r, of: srcV, at: tm(cursor))
  }
  // TAIL="<seconds>": the film ends on a still picture while the last word finishes, before the next slide moves in.
  if i == parts.count - 1, let v = ProcessInfo.processInfo.environment["TAIL"], let tail = Double(v) {
    let from = cursor + p.1 - p.0 - tail, frame = 1.0 / 30
    vs[n].removeTimeRange(CMTimeRange(start: tm(from), end: tm(from + tail)))
    try vs[n].insertTimeRange(CMTimeRange(start: tm(p.1 - tail - frame), duration: tm(frame)), of: srcV, at: tm(from))
    vs[n].scaleTimeRange(CMTimeRange(start: tm(from), duration: tm(frame)), toDuration: tm(tail))
  }
  try aus[n].insertTimeRange(r, of: srcA, at: tm(cursor))
  at.append(cursor)
  let end = cursor + p.1 - p.0
  mix[n].setVolumeRamp(fromStartVolume: 0, toEndVolume: 1, timeRange: CMTimeRange(start: tm(cursor), duration: tm(i == 0 ? 0.05 : fade)))
  let out = i == parts.count - 1 ? 0.05 : fade  // no long fade on the last word
  mix[n].setVolumeRamp(fromStartVolume: 1, toEndVolume: 0, timeRange: CMTimeRange(start: tm(end - out), duration: tm(out)))
  cursor = end - fade
}
let total = cursor + fade
let scale = CGAffineTransform(scaleX: CGFloat(width) / srcV.naturalSize.width, y: CGFloat(height) / srcV.naturalSize.height)
var steps: [AVMutableVideoCompositionInstruction] = []
for (i, p) in parts.enumerated() {
  let first = at[i], end = first + p.1 - p.0, n = i % 2
  let steadyFrom = i == 0 ? first : first + fade
  let steadyTo = i == parts.count - 1 ? total : end - fade
  let solo = AVMutableVideoCompositionInstruction()
  // The last instruction must reach the exact end of the composition, else AVFoundation rejects it (-11841).
  solo.timeRange = CMTimeRange(start: tm(steadyFrom), end: i == parts.count - 1 ? comp.duration : tm(steadyTo))
  let layer = AVMutableVideoCompositionLayerInstruction(assetTrack: vs[n])
  layer.setTransform(scale, at: .zero)
  solo.layerInstructions = [layer]
  steps.append(solo)
  if i < parts.count - 1 {
    let both = AVMutableVideoCompositionInstruction()
    both.timeRange = CMTimeRange(start: tm(steadyTo), end: tm(at[i + 1] + fade))
    let old = AVMutableVideoCompositionLayerInstruction(assetTrack: vs[n])
    let new = AVMutableVideoCompositionLayerInstruction(assetTrack: vs[1 - n])
    old.setTransform(scale, at: .zero); new.setTransform(scale, at: .zero)
    old.setOpacityRamp(fromStartOpacity: 1, toEndOpacity: 0, timeRange: both.timeRange)
    both.layerInstructions = [old, new]
    steps.append(both)
  }
}
let picture = AVMutableVideoComposition()
picture.instructions = steps
picture.renderSize = CGSize(width: width, height: height)
picture.frameDuration = CMTime(value: 1, timescale: 30)
let audioMix = AVMutableAudioMix()
audioMix.inputParameters = mix

try? FileManager.default.removeItem(at: out)
let reader = try AVAssetReader(asset: comp)
let vo = AVAssetReaderVideoCompositionOutput(videoTracks: vs, videoSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange])
vo.videoComposition = picture
let ao = AVAssetReaderAudioMixOutput(audioTracks: aus, audioSettings: [AVFormatIDKey: kAudioFormatLinearPCM, AVSampleRateKey: 48000, AVNumberOfChannelsKey: 1])
ao.audioMix = audioMix
reader.add(vo); reader.add(ao)
let writer = try AVAssetWriter(outputURL: out, fileType: .mp4)
let vi = AVAssetWriterInput(mediaType: .video, outputSettings: [AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: width, AVVideoHeightKey: height,
  AVVideoColorPropertiesKey: [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2, AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2, AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2],
  AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: rate, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel]])
let ai = AVAssetWriterInput(mediaType: .audio, outputSettings: [AVFormatIDKey: kAudioFormatMPEG4AAC, AVSampleRateKey: 48000, AVNumberOfChannelsKey: 1, AVEncoderBitRateKey: 128000])
vi.expectsMediaDataInRealTime = false; ai.expectsMediaDataInRealTime = false
writer.add(vi); writer.add(ai); writer.shouldOptimizeForNetworkUse = true
reader.startReading(); writer.startWriting(); writer.startSession(atSourceTime: .zero)
let group = DispatchGroup()
for (i, o, name) in [(vi, vo as AVAssetReaderOutput, "v"), (ai, ao as AVAssetReaderOutput, "a")] {
  group.enter()
  i.requestMediaDataWhenReady(on: DispatchQueue(label: name)) {
    while i.isReadyForMoreMediaData {
      guard let s = o.copyNextSampleBuffer(), i.append(s) else { i.markAsFinished(); group.leave(); return }
    }
  }
}
group.wait()
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
guard writer.status == .completed && reader.status == .completed else {
  print("failed", String(describing: writer.error), String(describing: reader.error)); exit(1)
}
print("ok", total, "joins", at.dropFirst().map { $0 })

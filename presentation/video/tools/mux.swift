// Join picture and sound without re-encoding, or cut a silent clip:
//   mux join <picture.mp4> <sound.m4a> <out.mp4>
//   mux cut  <picture.mp4> <start> <seconds> <out.mp4>
import AVFoundation

let a = CommandLine.arguments
let comp = AVMutableComposition()
let picture = AVURLAsset(url: URL(fileURLWithPath: a[2]))
let join = a[1] == "join"
let start = join ? CMTime.zero : CMTime(seconds: Double(a[3])!, preferredTimescale: 600)
let length = join ? picture.duration : CMTime(seconds: Double(a[4])!, preferredTimescale: 600)

let v = comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)!
try v.insertTimeRange(CMTimeRange(start: start, duration: length), of: picture.tracks(withMediaType: .video)[0], at: .zero)
if join {
  let sound = AVURLAsset(url: URL(fileURLWithPath: a[3]))
  let s = comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)!
  try s.insertTimeRange(CMTimeRange(start: .zero, duration: CMTimeMinimum(length, sound.duration)), of: sound.tracks(withMediaType: .audio)[0], at: .zero)
}
let out = URL(fileURLWithPath: join ? a[4] : a[5])
try? FileManager.default.removeItem(at: out)
let export = AVAssetExportSession(asset: comp, presetName: AVAssetExportPresetPassthrough)!
export.outputURL = out
export.outputFileType = .mp4
export.shouldOptimizeForNetworkUse = true
let done = DispatchSemaphore(value: 0)
export.exportAsynchronously { done.signal() }
done.wait()
guard export.status == .completed else { fatalError(String(describing: export.error)) }

// Numbered JPEG frames to an H.264 picture track:
//   encode <frames-dir> <out.mp4> <count> <fps> <width> <height> <bit/s>
import AVFoundation
import CoreGraphics
import ImageIO

let a = CommandLine.arguments
let dir = URL(fileURLWithPath: a[1]), out = URL(fileURLWithPath: a[2])
let count = Int(a[3])!, fps = Int(a[4])!, w = Int(a[5])!, h = Int(a[6])!, rate = Int(a[7])!
try? FileManager.default.removeItem(at: out)
let writer = try AVAssetWriter(outputURL: out, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
  AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: w, AVVideoHeightKey: h,
  AVVideoColorPropertiesKey: [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
    AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2, AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2],
  AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: rate, AVVideoMaxKeyFrameIntervalKey: fps * (rate > 2_000_000 ? 2 : 8),
    AVVideoExpectedSourceFrameRateKey: fps, AVVideoAllowFrameReorderingKey: true,
    AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel]])
input.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
  kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
  kCVPixelBufferWidthKey as String: w, kCVPixelBufferHeightKey as String: h])
writer.add(input); writer.startWriting(); writer.startSession(atSourceTime: .zero)
let space = CGColorSpace(name: CGColorSpace.sRGB)!
for n in 0..<count {
  autoreleasepool {
    let url = dir.appendingPathComponent(String(format: "%05d.jpg", n))
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil), let image = CGImageSourceCreateImageAtIndex(src, 0, nil)
    else { fatalError("cannot read \(url.path)") }
    while !input.isReadyForMoreMediaData {
      if writer.status == .failed { fatalError(String(describing: writer.error)) }
      Thread.sleep(forTimeInterval: 0.002)
    }
    var buffer: CVPixelBuffer? = nil
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &buffer)
    CVPixelBufferLockBaseAddress(buffer!, [])
    let ctx = CGContext(data: CVPixelBufferGetBaseAddress(buffer!), width: w, height: h, bitsPerComponent: 8,
      bytesPerRow: CVPixelBufferGetBytesPerRow(buffer!), space: space,
      bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue)!
    ctx.interpolationQuality = .high
    ctx.draw(image, in: CGRect(x: 0, y: 0, width: w, height: h))
    CVPixelBufferUnlockBaseAddress(buffer!, [])
    if !adaptor.append(buffer!, withPresentationTime: CMTime(value: CMTimeValue(n), timescale: CMTimeScale(fps))) {
      fatalError("append failed: \(String(describing: writer.error))")
    }
  }
}
input.markAsFinished()
writer.endSession(atSourceTime: CMTime(value: CMTimeValue(count), timescale: CMTimeScale(fps)))
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
guard writer.status == .completed else { fatalError(String(describing: writer.error)) }

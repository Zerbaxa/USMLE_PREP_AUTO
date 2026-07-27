// macOS 내장 Vision OCR. 새 의존성 없음.
//   swiftc -O ocr.swift -o ocr    (한 번만)
//   find … -name '*.png' | ./ocr   → 파일당 "\u{1}<경로>\n<텍스트>" 로 출력
// 경로는 stdin에서 한 줄씩 (파일명 공백·22k개 argv 한계 회피)
import Foundation
import Vision

var paths: [String] = []
while let line = readLine(strippingNewline: true) {
    if !line.isEmpty { paths.append(line) }
}

let lock = NSLock()
// Vision은 스레드 안전. 코어를 다 쓴다.
DispatchQueue.concurrentPerform(iterations: paths.count) { i in
    let path = paths[i]
    guard let img = NSData(contentsOfFile: path) as Data?,
          let src = CGImageSourceCreateWithData(img as CFData, nil),
          let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        FileHandle.standardError.write("skip \(path)\n".data(using: .utf8)!)
        return
    }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false          // 의학용어가 일반어로 교정되는 걸 막는다
    req.recognitionLanguages = ["en-US"]
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    let text = (req.results ?? [])
        .compactMap { $0.topCandidates(1).first?.string }
        .joined(separator: "\n")
    lock.lock()                                 // 출력이 섞이지 않게
    print("\u{1}\(path)")
    print(text)
    lock.unlock()
}

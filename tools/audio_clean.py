"""Cắt tiếng 'rẹt' mà model giọng đọc đôi khi chèn ở cuối file, rồi làm nhỏ dần 40 ms cuối.

Dấu hiệu: sau câu nói có một khoảng lặng >= 100 ms, rồi một đoạn ngắn (<= 300 ms) rất to (> -10 dB)
ở ngay cuối file. Chỉ dùng thư viện chuẩn để chạy được trên GitHub Actions.
"""
import array, math, subprocess, sys

RATE, FR = 24000, 480  # khung 20 ms


def _db(frame):
    if not frame:
        return -120.0
    s = sum(v * v for v in frame) / len(frame)
    return 10 * math.log10(s / (32768.0 ** 2) + 1e-12)


def clean_pcm(raw: bytes) -> tuple[bytes, bool]:
    a = array.array("h"); a.frombytes(raw[: len(raw) // 2 * 2])
    n = len(a) // FR
    if n < 6:
        return raw, False
    db = [_db(a[i * FR:(i + 1) * FR]) for i in range(n)]
    voiced = [i for i, d in enumerate(db) if d > -40]
    if not voiced:
        return raw, False
    last = voiced[-1]; i = last
    while i > 0 and db[i - 1] > -40:
        i -= 1
    j, gap = i - 1, 0
    while j >= 0 and db[j] <= -40:
        gap += 1; j -= 1
    burst, loud = last - i + 1, max(db[i:last + 1])
    cut = False
    if j >= 0 and gap >= 5 and burst <= 15 and loud > -10 and n - 1 - last <= 10:
        a = a[: (i - gap + 4) * FR]  # giữ lại 80 ms lặng sau câu nói
        cut = True
    elif j >= 0 and gap >= 1 and burst <= 16 and loud > -10 and n - 1 - last <= 12:
        # khoảng lặng ngắn (20–80 ms) nhưng đoạn cuối to vọt hẳn so với câu nói ngay trước: cũng là tiếng rẹt
        k = j
        while k > 0 and db[k - 1] > -40:
            k -= 1
        bm = sum(db[i:last + 1]) / burst; pm = sum(db[k:j + 1]) / (j - k + 1)
        if bm > -12 and bm > pm + 5:
            a = a[: (j + 1 + min(gap, 4)) * FR]
            cut = True
    # tiếng "tách" ở đầu: một đoạn rất ngắn (<= 60 ms) rồi lặng >= 100 ms trước khi vào câu
    db2 = [_db(a[k * FR:(k + 1) * FR]) for k in range(len(a) // FR)]
    v2 = [k for k, d in enumerate(db2) if d > -40]
    if v2 and v2[0] <= 1:
        e = v2[0]
        while e + 1 < len(db2) and db2[e + 1] > -40:
            e += 1
        q = e + 1
        while q < len(db2) and db2[q] <= -40:
            q += 1
        if e - v2[0] + 1 <= 3 and q - e - 1 >= 5 and q < len(db2):
            a = a[(q - 3) * FR:]  # bỏ tiếng tách, giữ 60 ms lặng trước câu
            cut = True
    fin = min(len(a), int(RATE * 0.01))
    for k in range(fin):
        a[k] = int(a[k] * k / fin)
    fade = min(len(a), int(RATE * 0.04))
    for k in range(fade):
        idx = len(a) - fade + k
        a[idx] = int(a[idx] * (1 - k / fade))
    return a.tobytes(), cut


def clean_mp3(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(RATE), "-"], capture_output=True, check=True).stdout
    pcm, cut = clean_pcm(raw)
    if cut:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(RATE), "-ac", "1", "-i", "pipe:0",
                        "-af", "apad=pad_dur=0.12", "-codec:a", "libmp3lame", "-q:a", "4", path], input=pcm, check=True)
    return cut


if __name__ == "__main__":
    fixed = [p for p in sys.argv[1:] if clean_mp3(p)]
    print(f"Đã cắt tiếng rẹt ở {len(fixed)}/{len(sys.argv) - 1} file")

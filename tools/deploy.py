"""Dựng, kiểm tra và đẩy trang lên GitHub: python3 tools/deploy.py "nội dung thay đổi" [--test] [--ci] [--dry]

  1. Dựng trang (tools/build2.py, tự chạy check_rules.py; còn lỗi là dừng).
  2. --test: chạy thêm node tools/t20.js (mọi bài, 2 ngôn ngữ, 2 mức); còn lỗi là dừng.
  3. Chỉ đẩy khi kho có địa chỉ github.com/ces-training/… (tài khoản của CES).
     Tài khoản ivythaibinh dành cho Lingo Cub và Rung Chuông Vàng: không bao giờ đẩy trang này lên đó.
  4. Commit mặc định có [skip ci] để GitHub KHÔNG tự tạo tranh hay giọng (tốn phí).
     Chỉ thêm --ci khi chị Duyên đã duyệt danh sách tranh/giọng mới trong tools/image-list.json, tools/audio-list.json.
  --dry: chỉ dựng và kiểm tra, không commit, không đẩy."""
import os, subprocess, sys

R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OWNER = "ces-training"
PATHS = ["tuan-1", "tools", "docs", "index.html", "README.md"]
COST = ["tools/audio-list.json", "tools/image-list.json", "tools/make_audio.py", "tools/make_images.py"]


def sh(*cmd, check=True, **kw):
    r = subprocess.run(cmd, cwd=R, text=True, capture_output=True, **kw)
    if check and r.returncode != 0:
        print(r.stdout, r.stderr); sys.exit(f"DỪNG: {' '.join(cmd)} lỗi.")
    return r


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    msg = args[0] if args else "Cập nhật trang bài tập"
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))

    r = sh(sys.executable, "tools/build2.py", check=False); print(r.stdout.strip())
    if r.returncode != 0: print(r.stderr.strip()); sys.exit("DỪNG: dựng trang lỗi.")
    if "--test" in flags:
        r = sh("node", "tools/t20.js", check=False, env=dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH", "") or sh("npm", "root", "-g").stdout.strip()))
        print(r.stdout.strip()[-3000:])
        if r.returncode != 0: sys.exit("DỪNG: t20.js còn lỗi.")
    if "--dry" in flags: print("Chạy thử xong, chưa đẩy."); return

    url = sh("git", "remote", "get-url", "origin").stdout.strip()
    if f"github.com/{OWNER}/" not in url and f"github.com:{OWNER}/" not in url:
        sys.exit(f"DỪNG: kho đang trỏ tới {url}, không phải tài khoản {OWNER}. Không đẩy. "
                 "Hãy đổi kết nối GitHub sang tài khoản ces-training rồi chạy lại.")
    sh("git", "add", "--", *[p for p in PATHS if os.path.exists(os.path.join(R, p))])
    staged = sh("git", "diff", "--cached", "--name-only").stdout.split()
    if not staged: print("Không có gì thay đổi."); return
    cost = [p for p in staged if p in COST]
    if cost and "--ci" not in flags:
        print(f"Lưu ý: có thay đổi ở {', '.join(cost)}; commit vẫn có [skip ci] nên GitHub chưa tạo tranh/giọng.")
    full = msg if "--ci" in flags else msg + " [skip ci]"
    sh("git", "commit", "-q", "-m", full)
    sh("git", "fetch", "-q", "origin", "main")
    sh("git", "rebase", "-q", "origin/main")
    sh("git", "push", "-q", "origin", "HEAD:main")
    print(f"Đã đẩy lên {OWNER}: {sh('git', 'log', '--oneline', '-1').stdout.strip()}")


if __name__ == "__main__":
    main()

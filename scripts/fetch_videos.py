"""Download the source videos for every clip from Europe PMC and cut the benchmark clips from them.

The benchmark does not redistribute the clips: 18 of the 66 source articles are CC BY-NC-ND, which
does not permit derivative works. This script fetches each article's supplementary files from
Europe PMC, keeps the video files, and re-encodes them as H.264 so that frame extractors read them
(many PMC uploads are mp4v and decode silently to nothing). It then cuts every benchmark clip from its
source file using the excerpt recorded in data/clips.json:

  excerpt.source_file   file name inside the article's supplementary archive
  excerpt.start_s/end_s excerpt bounds in seconds (25 fps grid, located by frame matching)
  excerpt.crop          [x, y, w, h] in source pixels after autorotation, or null for the full frame
  excerpt.rotate        clockwise quarter turns applied after cropping (0 for most clips)

usage: python scripts/fetch_videos.py [PMCID ...]      (default: all 66 articles)
env:   FFMPEG (default ffmpeg), OUT (default videos_raw), CLIPS (default dataset/videos)
"""
import io, json, os, re, subprocess, sys, time, urllib.request, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUT", os.path.join(ROOT, "videos_raw")); FF = os.environ.get("FFMPEG", "ffmpeg")
CLIPS = os.environ.get("CLIPS", os.path.join(ROOT, "dataset", "videos"))
VID = re.compile(r"\.(mp4|mov|avi|wmv|m4v|mpg|mpeg|mkv)$", re.I)
clips = json.load(open(os.path.join(ROOT, "data/clips.json")))
want = set(sys.argv[1:]) or {c["source"]["pmcid"] for c in clips if c["source"].get("pmcid")}
os.makedirs(OUT, exist_ok=True)


def cut(clip, raw):
    """cut one benchmark clip from its downloaded source file"""
    ex = clip["excerpt"]
    vf = []
    if ex.get("crop"):
        x, y, w, h = ex["crop"]; vf.append("crop=%d:%d:%d:%d" % (w, h, x, y))
    vf += ["transpose=1"] * int(ex.get("rotate") or 0)
    out = os.path.join(CLIPS, clip["path"].split("videos/", 1)[-1])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # seek after -i (decode, then discard): exact on every container, including MPEG-TS files named .mp4
    cmd = [FF, "-y", "-v", "error", "-i", raw, "-ss", "%.2f" % ex["start_s"], "-t", "%.2f" % (ex["end_s"] - ex["start_s"])]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    subprocess.run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", out], check=False)
    return out


for pmc in sorted(want):
    d = os.path.join(OUT, pmc); os.makedirs(d, exist_ok=True)
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/supplementaryFiles?includeInlineImage=false" % pmc
    zf = None
    for attempt in range(5):                 # Europe PMC intermittently returns an error page instead of the archive
        try:
            zf = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(url, timeout=600).read()))
            break
        except Exception as e:
            err = e; time.sleep(20 * (attempt + 1))
    if zf is None:
        print("%s: no supplementary archive after 5 attempts (%s); rerun later" % (pmc, err)); continue
    n = 0
    for name in zf.namelist():
        if not VID.search(name): continue
        raw = os.path.join(d, os.path.basename(name)); open(raw, "wb").write(zf.read(name))
        h264 = os.path.splitext(raw)[0] + ".h264.mp4"
        subprocess.run([FF, "-y", "-v", "error", "-i", raw, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", h264], check=False)
        n += 1
    print("%s: %d video file(s) -> %s" % (pmc, n, d))
    for c in clips:
        if c["source"].get("pmcid") != pmc or not c.get("excerpt"):
            continue
        raw = os.path.join(d, c["excerpt"]["source_file"])
        if not os.path.exists(raw):
            print("  %s: source file %s missing" % (c["video"], c["excerpt"]["source_file"])); continue
        print("  %s <- %s [%.2f, %.2f] s -> %s" % (c["video"], c["excerpt"]["source_file"], c["excerpt"]["start_s"],
                                                 c["excerpt"]["end_s"], cut(c, raw)))

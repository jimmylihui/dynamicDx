"""Download the source videos for every clip from Europe PMC and re-encode them.

The benchmark does not redistribute the clips: 18 of the 66 source articles are CC BY-NC-ND, which
does not permit derivative works. This script fetches each article's supplementary files from
Europe PMC, keeps the video files, and re-encodes them as H.264 so that frame extractors read them
(many PMC uploads are mp4v and decode silently to nothing). Each benchmark clip is a <30 s excerpt
of one of these files around the interval in which the sign is expressed; data/clips.json gives the
clip's duration, frame rate and scene cuts, and data/cases.json the sign to look for.

usage: python scripts/fetch_videos.py [PMCID ...]      (default: all 66 articles)
env:   FFMPEG (default ffmpeg), OUT (default videos_raw)
"""
import io, json, os, re, subprocess, sys, urllib.request, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUT", os.path.join(ROOT, "videos_raw")); FF = os.environ.get("FFMPEG", "ffmpeg")
VID = re.compile(r"\.(mp4|mov|avi|wmv|m4v|mpg|mpeg|mkv)$", re.I)
clips = json.load(open(os.path.join(ROOT, "data/clips.json")))
want = set(sys.argv[1:]) or {c["source"]["pmcid"] for c in clips}
os.makedirs(OUT, exist_ok=True)
for pmc in sorted(want):
    d = os.path.join(OUT, pmc); os.makedirs(d, exist_ok=True)
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/supplementaryFiles?includeInlineImage=false" % pmc
    try:
        blob = urllib.request.urlopen(url, timeout=120).read()
        zf = zipfile.ZipFile(io.BytesIO(blob))
    except Exception as e:
        print("%s: no supplementary archive (%s)" % (pmc, e)); continue
    n = 0
    for name in zf.namelist():
        if not VID.search(name): continue
        raw = os.path.join(d, os.path.basename(name)); open(raw, "wb").write(zf.read(name))
        h264 = os.path.splitext(raw)[0] + ".h264.mp4"
        subprocess.run([FF, "-y", "-v", "error", "-i", raw, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", h264], check=False)
        n += 1
    print("%s: %d video file(s) -> %s" % (pmc, n, d))

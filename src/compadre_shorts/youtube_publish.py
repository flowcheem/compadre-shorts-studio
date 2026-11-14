"""Resumable YouTube publishing with per-clip idempotency and safe Drive cleanup."""
from __future__ import annotations
import argparse, json, re, sys, time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from .drive_intake import ApiError, token, request_json, drive_file, patch_props, cleanup_after_publish

UPLOAD_URL="https://www.googleapis.com/upload/youtube/v3/videos"

def safe_title(source_name: str, index: int) -> str:
    stem=Path(source_name).stem
    stem=re.sub(r"[_-]+"," ",stem)
    stem=re.sub(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+"," ",stem)
    stem=" ".join(stem.split())[:55]
    base=f"Compadre Gameplay | {stem} | Momento {index:02d} #Shorts"
    return base[:100]

def verify_video(t, video_id, attempts=45, interval=30):
    for attempt in range(attempts):
        data=request_json(
            "https://www.googleapis.com/youtube/v3/videos?part=status,processingDetails&id="+video_id,t
        )
        items=data.get("items",[])
        if not items:
            raise ApiError(f"YouTube video {video_id} is not visible to the authorized channel.")
        video=items[0]
        processing=(video.get("processingDetails") or {}).get("processingStatus")
        upload=(video.get("status") or {}).get("uploadStatus")
        if processing=="succeeded" and upload=="processed":
            return
        if processing=="failed" or upload=="failed":
            raise ApiError(f"YouTube rejected processing for {video_id}; source retained.")
        if attempt+1<attempts:
            time.sleep(interval)
    raise ApiError(f"YouTube processing timed out for {video_id}; source retained.")

def upload_one(t, path, title, description, tags):
    size=path.stat().st_size
    if size<=0: raise ApiError(f"Empty render: {path.name}")
    metadata={
        "snippet":{
            "title":title,
            "description":description,
            "tags":tags,
            "categoryId":"20",
            "defaultLanguage":"es",
        },
        "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False},
    }
    req=Request(
        UPLOAD_URL+"?uploadType=resumable&part=snippet,status",
        data=json.dumps(metadata,ensure_ascii=False).encode(),
        headers={
            "Authorization":f"Bearer {t}",
            "Content-Type":"application/json; charset=UTF-8",
            "X-Upload-Content-Type":"video/mp4",
            "X-Upload-Content-Length":str(size),
        },
        method="POST",
    )
    try:
        with urlopen(req,timeout=120) as response:
            session_url=response.headers.get("Location")
    except HTTPError as e:
        raise ApiError(f"YouTube upload session failed ({e.code}): {e.read().decode(errors='replace')}") from e
    if not session_url: raise ApiError("YouTube did not return a resumable upload URL.")
    data=path.read_bytes()
    put=Request(session_url,data=data,headers={
        "Authorization":f"Bearer {t}",
        "Content-Type":"video/mp4",
        "Content-Length":str(size),
    },method="PUT")
    try:
        with urlopen(put,timeout=900) as response:
            result=json.loads(response.read().decode())
    except HTTPError as e:
        raise ApiError(f"YouTube video upload failed ({e.code}): {e.read().decode(errors='replace')}") from e
    video_id=result.get("id")
    if not video_id: raise ApiError("YouTube upload response did not contain a video ID.")
    return video_id

def record_published_clip(t, source_id, index, video_id):
    source=drive_file(source_id,t)
    props=source.get("appProperties") or {}
    props[f"compadreClip{index:03d}VideoId"]=video_id
    props["compadreStatus"]="rendered"
    patch_props(source_id,t,props)

def publish_batch(source_id, source_name, clips_dir, max_clips):
    t=token()
    source=drive_file(source_id,t)
    props=source.get("appProperties") or {}
    clips=sorted(clips_dir.glob("*.mp4"))[:max_clips]
    if not clips: raise ApiError("No MP4 clips found to publish.")
    published=[]
    for index,path in enumerate(clips,start=1):
        key=f"compadreClip{index:03d}VideoId"
        existing=(props.get(key) or "").strip()
        if existing:
            verify_video(t,existing)
            video_id=existing
            print(f"Already published and verified; skipping duplicate: {path.name} -> {video_id}")
        else:
            title=safe_title(source_name,index)
            description=(
                "Gameplay original de Compadre Gameplay.\n"
                "Suscríbete para ver más momentos.\n\n"
                "#Shorts #Gaming #CompadreGameplay"
            )
            video_id=upload_one(
                t,path,title,description,
                ["Compadre Gameplay","gaming","gameplay","YouTube Shorts","GTA V"],
            )
            verify_video(t,video_id)
            record_published_clip(t,source_id,index,video_id)
            props[key]=video_id
            print(f"Published and verified: {path.name} -> https://www.youtube.com/shorts/{video_id}")
        published.append({"file":path.name,"video_id":video_id,
            "url":f"https://www.youtube.com/shorts/{video_id}",
            "title":safe_title(source_name,index)})
    manifest=clips_dir/"publication_manifest.json"
    manifest.write_text(json.dumps({
        "source_file_id":source_id,"source_name":source_name,
        "published_count":len(published),"videos":published,
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # This final gate runs only after every clip is verified. If it fails, the
    # Drive source remains available and successful clip IDs make retries safe.
    cleanup_after_publish(t,source_id,published[0]["video_id"])
    print(f"All {len(published)} Shorts verified; Drive source cleanup completed.")

def main():
    p=argparse.ArgumentParser(description="Publish Compadre Shorts to the linked YouTube channel")
    p.add_argument("--source-file-id",required=True)
    p.add_argument("--source-name",required=True)
    p.add_argument("--clips-dir",type=Path,required=True)
    p.add_argument("--max-clips",type=int,default=10)
    a=p.parse_args()
    try:
        if not 1<=a.max_clips<=30: raise ApiError("--max-clips must be between 1 and 30.")
        publish_batch(a.source_file_id,a.source_name,a.clips_dir.expanduser().resolve(),a.max_clips)
        return 0
    except (ApiError,OSError,HTTPError) as e:
        print(f"Compadre YouTube publish error: {e}",file=sys.stderr)
        return 1

if __name__=="__main__": raise SystemExit(main())

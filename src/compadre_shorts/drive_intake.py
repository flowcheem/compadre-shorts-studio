"""Google Drive intake and guarded source cleanup for Compadre Shorts Studio."""
from __future__ import annotations
import argparse, json, os, shutil, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DRIVE="https://www.googleapis.com/drive/v3"
YOUTUBE="https://www.googleapis.com/youtube/v3"

class ApiError(RuntimeError): pass

def env(name):
    value=os.environ.get(name,"").strip()
    if not value: raise ApiError(f"Missing required environment variable: {name}")
    return value

def request_json(url, token, method="GET", payload=None):
    data=json.dumps(payload).encode() if payload is not None else None
    headers={"Authorization":f"Bearer {token}"}
    if data is not None: headers["Content-Type"]="application/json"
    try:
        with urlopen(Request(url,data=data,headers=headers,method=method),timeout=180) as r:
            raw=r.read()
            return json.loads(raw.decode()) if raw else {}
    except HTTPError as e:
        raise ApiError(f"API error {e.code}: {e.read().decode(errors='replace')}") from e

def token():
    body=urlencode({"client_id":env("GOOGLE_CLIENT_ID"),"client_secret":env("GOOGLE_CLIENT_SECRET"),
        "refresh_token":env("GOOGLE_REFRESH_TOKEN"),"grant_type":"refresh_token"}).encode()
    try:
        with urlopen(Request("https://oauth2.googleapis.com/token",data=body,
            headers={"Content-Type":"application/x-www-form-urlencoded"}),timeout=60) as r:
            result=json.loads(r.read().decode())
    except HTTPError as e:
        raise ApiError(f"OAuth refresh failed ({e.code}): {e.read().decode(errors='replace')}") from e
    if not result.get("access_token"): raise ApiError("OAuth response did not include access_token")
    return result["access_token"]

def drive_file(fid,t):
    fields="id,name,mimeType,size,md5Checksum,modifiedTime,appProperties,trashed"
    return request_json(f"{DRIVE}/files/{fid}?{urlencode({'fields':fields})}",t)

def patch_props(fid,t,props):
    request_json(f"{DRIVE}/files/{fid}?fields=id,appProperties",t,"PATCH",{"appProperties":props})

def download_one(t,folder,out,stable_minutes):
    q=f"'{folder}' in parents and trashed=false and mimeType contains 'video/'"
    params=urlencode({"q":q,"pageSize":"100","orderBy":"createdTime",
        "fields":"files(id,name,mimeType,size,md5Checksum,modifiedTime,appProperties,createdTime)"})
    files=request_json(f"{DRIVE}/files?{params}",t).get("files",[])
    ready=[]
    for f in files:
        modified=datetime.fromisoformat(f["modifiedTime"].replace("Z","+00:00")).timestamp()
        props=f.get("appProperties") or {}
        status=props.get("compadreStatus","pending")
        processing_started=props.get("compadreProcessingStarted","")
        stale_processing=True
        if status=="processing" and processing_started:
            try:
                started=datetime.fromisoformat(processing_started.replace("Z","+00:00")).timestamp()
                stale_processing=(time.time()-started) > 8*60*60
            except ValueError:
                stale_processing=True
        if time.time()-modified >= stable_minutes*60 and status not in ("published","deleted") and (status!="processing" or stale_processing):
            ready.append(f)
    if not ready:
        print("No stable pending video in Drive input folder.")
        return None
    f=ready[0]; fid=f["id"]; props=f.get("appProperties") or {}
    props.update({"compadreStatus":"processing","compadrePipeline":"drive-v1",
        "compadreProcessingStarted":datetime.now(timezone.utc).isoformat()})
    patch_props(fid,t,props)
    out.parent.mkdir(parents=True,exist_ok=True)
    try:
        req=Request(f"{DRIVE}/files/{fid}?alt=media",headers={"Authorization":f"Bearer {t}"})
        with urlopen(req,timeout=300) as response, out.open("wb") as stream:
            shutil.copyfileobj(response,stream,8*1024*1024)
        if out.stat().st_size==0: raise ApiError("Downloaded file is empty; original retained.")
    except Exception:
        props["compadreStatus"]="pending"; props.pop("compadreProcessingStarted",None)
        patch_props(fid,t,props); raise
    props.update({"compadreStatus":"downloaded","compadreLocalBytes":str(out.stat().st_size),
        "compadreSourceMd5":f.get("md5Checksum","")})
    props.pop("compadreProcessingStarted",None)
    patch_props(fid,t,props)
    result={"status":"downloaded","source_file_id":fid,"source_name":f["name"],
        "source_size_bytes":int(f.get("size",out.stat().st_size)),
        "source_md5":f.get("md5Checksum",""),"local_path":str(out)}
    print(json.dumps(result,ensure_ascii=False)); return result

def mark_rendered(t,fid):
    f=drive_file(fid,t); p=f.get("appProperties") or {}
    if p.get("compadreStatus")!="downloaded":
        raise ApiError("Only a downloaded source can be marked rendered.")
    p.update({"compadreStatus":"rendered","compadreRenderedAt":datetime.now(timezone.utc).isoformat()})
    patch_props(fid,t,p)

def mark_failed(t,fid,reason):
    f=drive_file(fid,t); p=f.get("appProperties") or {}
    p.update({"compadreStatus":"failed","compadreLastError":reason[:120]})
    patch_props(fid,t,p)

def cleanup_after_publish(t,fid,video_id):
    data=request_json(f"{YOUTUBE}/videos?{urlencode({'part':'status,processingDetails','id':video_id})}",t)
    items=data.get("items",[])
    if not items or items[0].get("id")!=video_id:
        raise ApiError("YouTube video not found; source retained.")
    v=items[0]; processing=(v.get("processingDetails") or {}).get("processingStatus")
    upload=(v.get("status") or {}).get("uploadStatus")
    if processing!="succeeded" or upload!="processed":
        raise ApiError(f"YouTube processing not confirmed (processing={processing}, upload={upload}); source retained.")
    f=drive_file(fid,t); p=f.get("appProperties") or {}
    if p.get("compadreStatus") not in ("downloaded","rendered","published"):
        raise ApiError("Source state is not eligible for cleanup; refusing deletion.")
    # Do not change the source state before deletion: if Drive refuses the
    # delete, the file remains eligible for an idempotent retry.
    req=Request(f"{DRIVE}/files/{fid}",headers={"Authorization":f"Bearer {t}"},method="DELETE")
    try:
        with urlopen(req,timeout=120): pass
    except HTTPError as e:
        raise ApiError(f"YouTube verified, but Drive deletion failed ({e.code}): {e.read().decode(errors='replace')}") from e
    print(f"Deleted source {fid} only after YouTube processing was verified for {video_id}.")

def main():
    p=argparse.ArgumentParser(description="Compadre Drive intake and safe cleanup")
    sub=p.add_subparsers(dest="cmd",required=True)
    d=sub.add_parser("download"); d.add_argument("--output",type=Path,required=True); d.add_argument("--stable-minutes",type=int,default=10)
    r=sub.add_parser("mark-rendered"); r.add_argument("--file-id",required=True)
    f=sub.add_parser("mark-failed"); f.add_argument("--file-id",required=True); f.add_argument("--reason",required=True)
    c=sub.add_parser("cleanup-after-publish"); c.add_argument("--file-id",required=True); c.add_argument("--youtube-video-id",required=True)
    a=p.parse_args()
    try:
        t=token()
        if a.cmd=="download":
            if a.stable_minutes<1: raise ApiError("stable-minutes must be at least 1")
            download_one(t,env("GOOGLE_DRIVE_INPUT_FOLDER_ID"),a.output.expanduser().resolve(),a.stable_minutes)
        elif a.cmd=="mark-rendered": mark_rendered(t,a.file_id)
        elif a.cmd=="mark-failed": mark_failed(t,a.file_id,a.reason)
        else: cleanup_after_publish(t,a.file_id,a.youtube_video_id)
        return 0
    except (ApiError,OSError) as e:
        print(f"Compadre Drive error: {e}",file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())

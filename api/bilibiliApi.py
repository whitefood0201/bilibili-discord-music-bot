import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from logger import setupLogger
logger = setupLogger('Bilibili Api')

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}
VIDEO_INFO_URL = "https://api.bilibili.com/x/web-interface/view"
VIDEO_STREAM_URL = 'https://api.bilibili.com/x/player/playurl'

def getVideoData(bvid: str) -> dict:
    logger.info(f"Getting the cid of {bvid}.")
    """
        Get the cid of video, using bvid.

        return:
            cid or -1 for any exception.
    """
    param = { "bvid": bvid }
    try: 
        resp = requests.get(VIDEO_INFO_URL, params=param, headers=HEADER)

        if (resp.status_code == 200):
            data = resp.json()
            if data["code"] == 0:
                return {
                    "cid": data["data"]["cid"],
                    "title": data["data"]["title"],
                    "bvid": bvid
                }
            
    except RequestsConnectionError as e:
        logger.error(e)
        e.with_traceback()
    return None


def getAudioBaseUrl(bvid: str, cid: str) -> str:
    logger.info(f"Getting the audio url of {bvid}.")
    """
        Get the real url of giving video audio

        return:
            real url or empty str for any exception.
    """
    param = {
        "bvid": bvid,
        "cid": cid,
        "fnval": 4048,
        "fnver": 0,
    }
    try :
        resp = requests.get(VIDEO_STREAM_URL, params=param, headers=HEADER)
        if (resp.status_code == 200):
            data = resp.json()
            if data["code"] == 0:
                
                audios = sorted(resp.json()["data"]["dash"]["audio"], key=lambda jsonObj: jsonObj["id"], reverse=True)
                if len(audios) != 0:
                    return audios[0]["baseUrl"]
                
    except Exception as e:
        logger.error(e)
        e.with_traceback()
    return ""


def getAudio(bvid: str) -> str:
    data = getVideoData(bvid)
    if data.cid != -1:
        return getAudioBaseUrl(bvid, data.cid)
    return ""

# a = getAudio("BV1rp4y1e745")
# print(a)


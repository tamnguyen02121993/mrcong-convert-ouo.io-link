import re
from curl_cffi import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn


# ouo url
# Examples:
# https://ouo.io/HxFVfD - ouo.io links (no account -> only one step)
# https://ouo.press/Zu7Vs5 - ouo.io links (with account -> two steps)
# Can exchange between ouo.press and ouo.io

# url = "https://ouo.press/Zu7Vs5"

# -------------------------------------------

class ConvertLinkRequest(BaseModel):
    url: str

class ConvertLinkResponse():
    # def __init__(self, original_link: str, converted_link: str) -> None:
    #     self.original_link = original_link
    #     self.converted_link = converted_link
    original_link: str
    converted_link: str


if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

app = FastAPI()

origins = [
    "https://mrcong-nest-api.vercel.app",
]

app.add_middleware(CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

def RecaptchaV3():
    import requests
    ANCHOR_URL = 'https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x&co=aHR0cHM6Ly9vdW8ucHJlc3M6NDQz&hl=en&v=pCoGBhjs9s8EhFOHJFe8cqis&size=invisible&cb=ahgyd1gkfkhe'
    url_base = 'https://www.google.com/recaptcha/'
    post_data = "v={}&reason=q&c={}&k={}&co={}"
    client = requests.Session()
    client.headers.update({
        'content-type': 'application/x-www-form-urlencoded'
    })
    matches = re.findall('([api2|enterprise]+)\/anchor\?(.*)', ANCHOR_URL)[0]
    url_base += matches[0]+'/'
    params = matches[1]
    res = client.get(url_base+'anchor', params=params)
    token = re.findall(r'"recaptcha-token" value="(.*?)"', res.text)[0]
    params = dict(pair.split('=') for pair in params.split('&'))
    post_data = post_data.format(params["v"], token, params["k"], params["co"])
    res = client.post(url_base+'reload', params=f'k={params["k"]}', data=post_data)
    answer = re.findall(r'"rresp","(.*?)"', res.text)[0]    
    return answer

# -------------------------------------------

client = requests.Session()
client.headers.update({
    'authority': 'ouo.io',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    'referer': 'http://www.google.com/ig/adde?moduleurl=',
    'upgrade-insecure-requests': '1',
})

# -------------------------------------------
# OUO BYPASS

@app.get('/', status_code=200)
async def home():
    return Response(status_code=200)

@app.post('/api/convert-link')
async def ouo_bypass(convertLinkRequest: ConvertLinkRequest) -> ConvertLinkResponse:
    tempurl = convertLinkRequest.url.replace("ouo.press", "ouo.io")
    p = urlparse(tempurl)
    id = tempurl.split('/')[-1]
    res = client.get(tempurl, impersonate="chrome110")
    next_url = f"{p.scheme}://{p.hostname}/go/{id}"

    for _ in range(2):

        if res.headers.get('Location'): break

        bs4 = BeautifulSoup(res.content, 'lxml')
        inputs = bs4.find_all("input", {"name": re.compile(r"token$")})
        data = { input.get('name'): input.get('value') for input in inputs }
        data['x-token'] = RecaptchaV3()
        
        h = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        
        res = client.post(next_url, data=data, headers=h, 
            allow_redirects=False, impersonate="chrome110")
        next_url = f"{p.scheme}://{p.hostname}/xreallcygo/{id}"

    # return {
    #     'original_link': url,
    #     'bypassed_link': res.headers.get('Location')
    # }
    response =  ConvertLinkResponse(converted_link=res.headers.get('Location'), original_link=convertLinkRequest.url)
    return response.model_dump()

# -------------------------------------------


# out = ouo_bypass(url)
# print(out)


# -------------------------------------------
'''
SAMPLE OUTPUT

{
    'original_link': 'https://ouo.io/go/HxFVfD',
    'bypassed_link': 'https://some-link.com'
}

'''
'''
 _._     _,-'""`-._
(,-.`._,'(       |\`-/|
    `-.-' \ )-`( , o o)
          `-    \`_`"'-
'''
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import json
from curl_cffi import requests
import os
from pow import DeepSeekPOW

load_dotenv()

api_key = os.getenv("token")
url = os.getenv("BASE_URL")
pow_solver = DeepSeekPOW()
isTake= False

def get_headers(pow_response: Optional[str] = None) -> Dict[str, str]:
        headers = {
            'accept': '*/*',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'authorization': f'Bearer {api_key}',
            'content-type': 'application/json',
            'origin': 'https://chat.deepseek.com',
            'referer': 'https://chat.deepseek.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-app-version': '20241129.1',
            'x-client-locale': 'en_US',
            'x-client-platform': 'web',
            'x-client-version': '1.0.0-always',
        }

        if pow_response:
            headers['x-ds-pow-response'] = pow_response

        return headers

def get_pow_challenge() -> Dict[str, Any]:
    try:
        
        response = requests.request(
            method='POST',
            url=f'{url}/chat/create_pow_challenge',
            headers=get_headers(),
            json={'target_path': '/api/v0/chat/completion'},
            cookies={},
            impersonate='chrome120',
            timeout=None
        )
        return response.json()['data']['biz_data']['challenge']
    except KeyError:
        print('Invalid challenge response format from server')

def sendMessage(prompt,message_id = None):
     m = {}
     h = get_headers(pow_solver.solve_challenge(get_pow_challenge()))

     json_data = {
    'chat_session_id': '711b9cfe-d3cb-489b-a217-26493be89fbe',
    'parent_message_id':message_id,
    'prompt':prompt,
    'ref_file_ids': [],
    'thinking_enabled': False,
    'search_enabled': False,
    }
     response = requests.post(
          'https://chat.deepseek.com/api/v0/chat/completion',
            cookies={},
            headers=h,
            json=json_data,
            impersonate='chrome120',
            stream=True,
            timeout=None
    )
     
     for line in response.iter_lines():
        
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("data: "):
                content = decoded_line.removeprefix("data: ").strip()
                
                if content == "[DONE]":
                    break
                d=json.loads(content)
                if "message_id" in d:
                    m['id'] = d["message_id"]
                    

                delta = d["choices"][0].get("delta", {})
                if "content" in delta:
                    m['message'] = delta["content"]
                    yield m
                    # message += delta["content"]
                elif "finish_reason" in d["choices"][0]:
                    break

                

                # print(message, end='', flush=True)




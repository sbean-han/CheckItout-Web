import json

import requests
import yaml


# https://developers.band.us/develop/guide/api
class BandOpenApi:
    def __init__(self, your_token):
        print('init')
        self.access_token=your_token

    def _api_call(self, api_path: str, params: dict = None, method: str = 'get') -> dict:
        if params is None:
            params = {}
        print(f'[api call] api_path : {api_path}, params : {params}')
        params['access_token'] = self.access_token
        if method == 'get':
            api_call_result = requests.get('https://openapi.band.us' + api_path, params)
        elif method == 'post':
            api_call_result = requests.post('https://openapi.band.us' + api_path, params)
        else:
            print(f'not support method. method: {method}')
            return None

        if not api_call_result.ok:
            print(f'api call fail. api call result : {api_call_result}, text : {api_call_result.text}')
            return None

        api_call_result_json = json.loads(api_call_result.text)
        if 'result_code' not in api_call_result_json or 'result_data' not in api_call_result_json:
            print(f'api call result structure malformed. api call result json : {api_call_result_json}')
            return None

        return api_call_result_json['result_data']

    def get_album_photos(self, band_key: str, photo_album_key: str) -> dict:
        return self._api_call('/v2/band/album/photos',
                              params={'band_key': band_key, 'photo_album_key': photo_album_key}, )

    def get_albums(self, band_key: str) -> dict:
        return self._api_call('/v2/band/albums',
                              params={'band_key': band_key}, )

    def delete_post_comments(self, band_key: str, post_key: str, comment_key: str):
        return self._api_call('/v2/band/post/comment/remove',
                              params={'band_key': band_key, 'post_key': post_key, 'body': comment_key},
                              method='post')

    def create_post_comments(self, band_key: str, post_key: str, body: str):
        return self._api_call('/v2/band/post/comment/create',
                              params={'band_key': band_key, 'post_key': post_key, 'body': body},
                              method='post')

    def get_post_comments(self, band_key: str, post_key: str):
        return self._api_call('/v2/band/post/comments',
                              params={'band_key': band_key, 'post_key': post_key}, )

    def delete_post(self, band_key: str, post_key: str):
        return self._api_call('/v2/band/post/remove',
                              params={'band_key': band_key, 'post_key': post_key},
                              method='post')

    def create_post(self, band_key: str, content: str):
        return self._api_call('/v2.2/band/post/create',
                              params={'band_key': band_key, 'content': content},
                              method='post')

    def get_post(self, band_key: str, post_key: str):
        return self._api_call('/v2.1/band/post', params={'band_key': band_key, 'post_key': post_key})

    def get_posts(self, band_key: str, locale: str):
        return self._api_call('/v2/band/posts', params={'band_key': band_key, 'locale': locale})

    def get_bands(self) -> dict:
        return self._api_call('/v2.1/bands')

    def get_profile(self) -> dict:
        return self._api_call('/v2/profile')
    
    def get_nextpage(self, type, next_params):
        return self._api_call(f'/v2.1/band/{type}', params=next_params)
    
    def get_nextpage(self, type, next_params, vers):
        return self._api_call(f'/{vers}/band/{type}', params=next_params)
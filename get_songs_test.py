import requests as r


def main():
    login_data = {
        'username': 'admin',
        'password': 'admin'
    }

    base_url = 'https://musicapp-bck.herokuapp.com/'


    token_res = 'auth/token/'
    songs = 'songs/'
    get_song = lambda song_id: 'songs/download?song_id=' + str(song_id)
    create_song = lambda song_id, start_time, stop_time: 'songs/create_song?song_id=%s&start_time=%s&stop_time=%s' % (song_id, start_time, stop_time)
    token_header = {'Authorization': 'Bearer ' + r.post(base_url + token_res, login_data).json()['token']}

    print(r.get(base_url+songs, headers=token_header).json())
    print(r.get(base_url+get_song(34), headers=token_header).json())
    # print(r.get(base_url+create_song(1, 16.2, 32.4), headers=token_header).json())


if __name__ == '__main__':
    main()
import pytube, os, json, requests
from PIL import Image
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from pathlib import Path

MOZILLA_PROFILE_PATH = 'C:\\Users\\Luis\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\1nz1cfe7.Channel Sports' # Find your mozilla profile path and put here
CHANNEL = 'https://www.youtube.com/channel/UCKZZlda0YgSfEnV8WNWDJCA/videos' # Channel to download videos
AMOUNT_VIDEO = 4 # Video amount to download
TIME_BETWEEN_POSTS = 3600 # The time between the videos will be post | Time in seconds: 3600 = 1 hour

class YoutubePost:
    def __init__(self) -> None:
        pass

    def take_videos_url(self):
        channel = pytube.Channel(CHANNEL)
        for video_url in channel.video_urls[0:AMOUNT_VIDEO]:
            yield video_url

    def get_infos(self, video_url):
        video = pytube.YouTube(video_url)
        video_info = {
            'video':video,
            'video_title':video.title,
            'video_thumb':video.thumbnail_url,
            'video_desc':video.description,
            'video_tags':video.keywords,
            'video_url':video_url
        }
        return video_info

    def download_video(self, video, directory_name):
        video.streams.get_highest_resolution().download(output_path=f'./videos/{directory_name}/', filename=f'{directory_name}.mp4')
        print('Video downloaded!')

    def download_thumb(self, thumb_url, directory_name):
        r = requests.get(thumb_url, stream=True)
        if r.status_code == 200:
            with open(f"./videos/{directory_name}/{directory_name}_thumb.jpg", 'wb') as f:
                f.write(r.content)
                print('Thumb downloaded!')
                f.close()
            self.change_res_thumb(f'./videos/{directory_name}/{directory_name}_thumb.jpg', directory_name)

    def change_res_thumb(self, image_path, filename):
        i = Image.open(image_path)
        i_resized = i.resize(size=(1280,720))
        i_resized.save(f'./videos/{filename}/{filename}.jpg')
        print('Thumb resized to 1280x720')

    def download_and_save(self, infos):
        if 'videos' not in os.listdir():
            os.makedirs('videos')
        directory_name = f'youtube_{infos["video_url"].strip("https://www.youtube.com/watch?v=")}'
        if directory_name not in os.listdir('./videos/'):
            os.makedirs(f'./videos/{directory_name}')
        self.download_video(infos['video'], directory_name)
        self.download_thumb(infos['video_thumb'], directory_name)
        infos.pop('video')
        with open(f'./videos/{directory_name}/infos.json', 'w') as json_file:
            json.dump(infos, json_file)
            print('Infos saved!')
            json_file.close()
        return directory_name
        
    def infos_to_upload(self, directory_name):
        if 'videos' in os.listdir():
            all_files = os.listdir(f'./videos/{directory_name}')
            for file_to_upload in all_files:
                if file_to_upload.endswith('.json'):
                    informations = file_to_upload
                if file_to_upload.endswith('.mp4'):
                    video = file_to_upload
                if file_to_upload.endswith('.jpg'):
                    thumb = file_to_upload
            return {
                'info':f'\\videos\\{directory_name}\\{informations}', 
                'video':f'\\videos\\{directory_name}\\{video}', 
                'thumb':f'\\videos\\{directory_name}\\{thumb}'}

    def open_informations(self, info_path):
        with open(f'{str(Path.cwd())}{info_path}') as f:
            data = json.load(f)
            return data

    def open_firefox(self, infos):
        video_path = f'{str(Path.cwd())}{infos["video"]}'
        thumb_path = f'{str(Path.cwd())}{infos["thumb"]}'
        info = self.open_informations(infos['info'])
        #################
        #Options
        profile = webdriver.FirefoxProfile(MOZILLA_PROFILE_PATH)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        options = Options()
        #Hide/Unhide browser
        #options.add_argument('--headless')
        driver = webdriver.Firefox(firefox_profile=profile, desired_capabilities=DesiredCapabilities.FIREFOX, options=options)
        ############
        print('Firefox open')
        driver.get('https://youtube.com/upload')
        driver.maximize_window()
        print('Getting https://youtube.com/upload')
        sleep(5)
        driver.find_element_by_xpath("//input[@type='file']").send_keys(video_path)
        sleep(5)
        driver.find_element_by_id('textbox').send_keys(info['video_title'])
        print('Title writed')
        sleep(2)
        #Writing video description
        driver.find_elements_by_id('textbox')[1].send_keys(info['video_desc'])
        print('Description writed')
        sleep(2)
        #Adding thumb
        driver.find_element_by_xpath("//input[@id='file-loader']").send_keys(thumb_path)
        sleep(2)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]').click()
        sleep(1)
        driver.find_element_by_xpath('//*[@id="toggle-button"]').click()
        sleep(1)
        tags = info['video_tags']
        input_tag = driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-advanced/div[3]/ytcp-form-input-container/div[1]/div[2]/ytcp-free-text-chip-bar/ytcp-chip-bar/div/input')
        print('Writing tags...')
        for tag in tags:
            input_tag.send_keys(f'{tag}', Keys.ENTER)
            sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[1]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]/div[1]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]').click()
        sleep(2)
        print('Video uploaded!')
        driver.quit()

    def run(self):
        videos_urls = self.take_videos_url()
        for video in videos_urls:
            video_info = self.get_infos(video)
            directory_name = self.download_and_save(video_info)
            self.open_firefox(directory_name)
            print()

    def test(self):
        video_info = self.get_infos('https://www.youtube.com/watch?v=59VbzYwWh40')
        directory_name = self.download_and_save(video_info)
        informations_to_upload = self.infos_to_upload(directory_name)
        self.open_firefox(informations_to_upload)

if __name__ == '__main__':
    yt = YoutubePost()
    yt.test()
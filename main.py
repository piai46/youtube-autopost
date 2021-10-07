import pytube, os, json, requests, datetime
from PIL import Image
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from pathlib import Path

MOZILLA_PROFILE_PATH = 'path\\to\\mozilla\\profile\\folder' # Find your mozilla profile path and put here
CHANNEL = 'https://www.youtube.com/channel/' # Channel to download videos
AMOUNT_VIDEO = 3 # Video amount to download
TIME_BETWEEN_POSTS = 3600 # The time between the videos will be post | Time in seconds: 3600 = 1 hour

class YoutubePost:
    def __init__(self) -> None:
        pass

    def take_videos_url(self):
        channel = pytube.Channel(CHANNEL)
        for video_url in channel.video_urls[0:AMOUNT_VIDEO]:
            yield video_url

    def get_infos(self, video_url, hour_post, date_post):
        video = pytube.YouTube(video_url)
        video_info = {
            'video':video,
            'video_title':video.title,
            'video_thumb':video.thumbnail_url,
            'video_desc':video.description,
            'video_tags':video.keywords,
            'video_url':video_url,
            'hour_post':hour_post,
            'date_post':date_post
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
        i_resized.save(f'./videos/{filename}/{filename}.jpeg')
        i.close()
        os.remove(f'./videos/{filename}/{filename}_thumb.jpg')
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
                if file_to_upload.endswith('.jpeg'):
                    thumb = file_to_upload
            return {
                'info':f'\\videos\\{directory_name}\\{informations}', 
                'video':f'\\videos\\{directory_name}\\{video}', 
                'thumb':f'\\videos\\{directory_name}\\{thumb}'}

    def open_informations(self, info_path):
        with open(f'{str(Path.cwd())}{info_path}') as f:
            data = json.load(f)
            return data

    def get_hour_xpath(self, input_hour):
        hour_xpath = dict()
        xpath_time = 0
        for hour in range(24):
            if hour == 0:
                hour = '00'
            for minute in range(0, 46, 15):
                if minute == 0:
                    minute = '00'
                xpath_time += 1
                hour_xpath.update({f'{hour}:{minute}':f'/html/body/ytcp-time-of-day-picker/tp-yt-paper-dialog/div/div[2]/tp-yt-paper-listbox/tp-yt-paper-item[{xpath_time}]'})
        return hour_xpath[input_hour]

    def open_firefox(self, infos):
        video_path = f'{str(Path.cwd())}{infos["video"]}'
        thumb_path = f'{str(Path.cwd())}{infos["thumb"]}'
        info = self.open_informations(infos['info'])
        date_to_post = info['date_post']
        hour_to_post = info['hour_post']
        hour_xpath = self.get_hour_xpath(hour_to_post)
        #################
        #Options
        profile = webdriver.FirefoxProfile(MOZILLA_PROFILE_PATH)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        options = Options()
        #Hide/Unhide browser
        options.add_argument('--headless')
        driver = webdriver.Firefox(firefox_profile=profile, desired_capabilities=DesiredCapabilities.FIREFOX, options=options)
        ############
        print('Firefox open')
        driver.get('https://youtube.com/upload')
        driver.maximize_window()
        print('Getting https://youtube.com/upload')
        sleep(5)
        driver.find_element_by_xpath("//input[@type='file']").send_keys(video_path)
        sleep(5)
        #Writing video title
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
        #Clicking in schedule video
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[2]/tp-yt-paper-radio-button/div[1]/div[1]').click()
        sleep(1)
        #Writing date
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[2]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/ytcp-text-dropdown-trigger[1]/ytcp-dropdown-trigger/div/div[3]').click()
        sleep(1)
        input_date = driver.find_element_by_xpath('/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input')
        input_date.send_keys(Keys.CONTROL, 'a')
        input_date.send_keys(date_to_post, Keys.ENTER)
        sleep(1)
        #Clicking on hour
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[2]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/ytcp-text-dropdown-trigger[2]/ytcp-dropdown-trigger/div/div[3]/tp-yt-iron-icon').click()
        sleep(1)
        driver.find_element_by_xpath(hour_xpath).click()
        print(f'Programmed to {date_to_post} at {hour_to_post}')
        sleep(1)
        #Clicking on upload
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]').click()
        sleep(2)
        print('Video uploaded!\n\n')
        driver.quit()

    def run(self):
        videos_urls = self.take_videos_url()
        now = datetime.datetime.now()
        video_number = 0
        for video in videos_urls:
            video_number += 1
            print(f'Video {video_number}')
            now += datetime.timedelta(seconds=TIME_BETWEEN_POSTS)
            hour_to_post = now.strftime('%H:%M')
            hour, minutes = hour_to_post.split(':')[0], int(hour_to_post.split(':')[1])
            setting_minutes = minutes//15
            minutes = setting_minutes * 15
            if minutes == 0:
                minutes = '00'
            hour_to_post = f'{hour}:{minutes}'
            date_to_post = now.strftime('%d/%m/%Y')
            video_info = self.get_infos(video, hour_post=hour_to_post, date_post=date_to_post)
            directory_name = self.download_and_save(video_info)
            informations_to_upload = self.infos_to_upload(directory_name)
            self.open_firefox(informations_to_upload)

if __name__ == '__main__':
    yt = YoutubePost()
    yt.run()
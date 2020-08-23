import os
from pathlib import Path
from image_utils import ImageText
import insta3


MAX_TITLE_LEN = 300


def get_title_and_self_text(title):
    """
    Returns text if they fall within the character limits
    :rtype: tuple(str)
    """
    #title= 'You should never view your challenges as a disadvantage. Instead, its important for you to understand that your experience facing and overcoming adversity is actually one of your biggest advantages. ~Michelle Obama'
    #title = 'No matter how good you are, someone is always going to be against you. But never let them be the limit of your success.~Terry Mark'
    if title is None or len(title) >= MAX_TITLE_LEN:
        return None
    
    return title


def get_bg_img():
    #Returns a white background ImageText object
    return ImageText((1500, 1500), background=(255, 255, 255))


def get_format():
    #Format of the text, courtesy Avishek Rakshit (helluva designer)
    return {'subreddit_font': 'Helvetica95Black.ttf',
            'title_font': 'Helvetica65Medium_22443.ttf',
            'subreddit_color': (159, 4, 4),
            'title_color': (33, 32, 32)
            }


def get_img_output_file_paths():
    cur_folder_path = os.getcwd()
    title_path = "".join(
        [cur_folder_path, "/images/tweet_", "img", ".jpg"])
    # creating directory structure if needed
    Path("/".join(title_path.split('/')[:-1])).mkdir(parents=True, exist_ok=True)
    return title_path




def write_on_img(text):

    title = get_title_and_self_text(text)
    title_op = get_img_output_file_paths()

    if title:
        title_img = get_bg_img()
        title_img.write_vertically_centred_text_box(left_padding=150, upper=0, lower=250,
                                                    text="Quote:",
                                                    box_width=1200,
                                                    font_filename=get_format()['subreddit_font'],
                                                    font_size=180,
                                                    color=get_format()['subreddit_color'],
                                                    place='center')
        title_img.write_vertically_centred_text_box(left_padding=150, upper=200, lower=1400,
                                                    text=title,
                                                    box_width=1250,
                                                    font_filename=get_format()['title_font'],
                                                    font_size=90, color=get_format()['title_color'],
                                                    place='left')

        title_img.save(title_op)
        path_of_img=os.getcwd()+"/images/tweet_img.jpg"
        insta3.upload(path_of_img,"Quote Of The Day",2)


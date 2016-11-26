import base64
import time
import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from PIL import Image
from moviepy.editor import *
import glob


GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS.json"
LIKELY = "LIKELY"
VERY_LIKELY = "VERY_LIKELY"

class audience_data:
    def __init__(self, time, results):
        self.time = time
        self.results = results

def set_up_credentials():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = dir_path + '\\' + GOOGLE_APPLICATION_CREDENTIALS

def get_vision_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('vision', 'v1', credentials=credentials)

def detect_face(image, max_results=10):
    """Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.

    Returns:
        An array of dicts with information about the faces in the picture.
    """

    image_content = image.read()
    batch_request = [{
        'image': {
            'content': base64.b64encode(image_content).decode('utf-8')
            },
        'features': [{
            'type': 'FACE_DETECTION',
            'maxResults': max_results,
            }]
        }]

    service = get_vision_service()
    request = service.images().annotate(body={
        'requests': batch_request,
        })

    response = request.execute()
    if not response['responses']:
        return []
    elif not response['responses'][0]:
        return []
    elif not response['responses'][0]['faceAnnotations']:
        return []
    return response['responses'][0]['faceAnnotations']

def audience_response(faces):
    num_emotions = {'joy': 0,
                    'sorrow': 0,
                    'anger': 0,
                    'surprise': 0,
                    'neutral': 0}
    if not faces:
        return num_emotions
    total = 0
    for face in faces:
        emotion = False
        if face['joyLikelihood'] == LIKELY or face['joyLikelihood'] == VERY_LIKELY:
            num_emotions['joy'] += 1
            emotion = True
        if face['sorrowLikelihood'] == LIKELY or face['sorrowLikelihood'] == VERY_LIKELY:
            num_emotions['sorrow'] += 1
            emotion = True
        if face['angerLikelihood'] == LIKELY or face['angerLikelihood'] == VERY_LIKELY:
            num_emotions['anger'] += 1
            emotion = True
        if face['surpriseLikelihood'] == LIKELY or face['surpriseLikelihood'] == VERY_LIKELY:
            num_emotions['surprise'] += 1
            emotion = True
        if emotion == False:
            num_emotions['neutral'] += 1
        total += 1

    per_emotions = {}
    for emotion, value in num_emotions.iteritems():
        per_emotions[emotion] = value / total
    return per_emotions

def getVideoClipResults(fileName, framerate):
    clip = VideoFileClip(fileName)
    clip.write_images_sequence('frame%03d.png', framerate)
    samples = make_img_list()
    final_results = []
    for i in range(len(samples)):
        image = open(samples[i], 'rb')
        data = getResultsFromSample(image, i/framerate)
        final_results.append(data)
    return final_results

def getResultsFromSample(sampleImage, timeStamp):
    faces = detect_face(sampleImage)
    results = audience_response(faces)
    data = audience_data(timeStamp, results)
    return data

def make_img_list():
    #Make list of image filenames
    image_list = []
    for filename in glob.glob('*.png'):
        image_list.append(filename)
    return image_list

if __name__ == "__main__":
    fileName = 'video.mp4'
    framerate = 2
    set_up_credentials()
    final = getVideoClipResults(fileName, framerate)

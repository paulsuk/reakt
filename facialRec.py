import base64
import time
import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from PIL import Image
from moviepy.editor import *
import glob
import plotly.plotly as py
import plotly.graph_objs as go


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
    py.sign_in("ConnorLawless", "izqU2noHEyqoJ4mslcKy")

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
    print(results)
    data = audience_data(timeStamp, results)
    return data

def make_img_list():
    #Make list of image filenames
    image_list = []
    for filename in glob.glob('*.png'):
        image_list.append(filename)
    return image_list

def output_linegraph( audience_data = [] ):
    py.sign_in("ConnorLawless", "izqU2noHEyqoJ4mslcKy")
    x = []
    joy = []
    anger = []
    surprise = []
    sorrow = []
    neutral = []
    for datum in audience_data:
        x.append(datum.time)
        joy.append(datum.results["joy"])
        anger.append(datum.results["anger"])
        surprise.append(datum.results["surprise"])
        sorrow.append(datum.results["sorrow"])
        neutral.append(datum.results["neutral"])
    traceJoy = go.Scatter(
        x=x,
        y=joy,
        mode='lines+markers',
        line=dict(
            color="rgb(244, 223, 66)",
            width=4),
        name='Joyful'
    )
    traceAnger = go.Scatter(
        x = x,
        y = anger,
        mode='lines+markers',
        line=dict(
            color="rgb(244, 66, 66)",
            width=4),
        name='Angry'
    )
    traceSurprise = go.Scatter(
        x=x,
        y=surprise,
        mode='lines+markers',
        line=dict(
            color="rgb(167, 48, 232)",
            width=4
        ),
        name='Surprised'
    )
    traceSorrow = go.Scatter(
        x=x,
        y=sorrow,
        mode='lines+markers',
        line=dict(
            color="rgb(66, 128, 244)",
            width=4
        ),
        name='Sad'
    )
    traceNeutral = go.Scatter(
        x=x,
        y=neutral,
        mode='lines+markers',
        line = dict(
            color="rgb(168, 164, 170)",
            width=4),
        name='Neutral'
    )
    data = [traceJoy, traceAnger, traceSurprise, traceSorrow, traceNeutral]
    layout = go.Layout(width=2592, height=640)
    fig = go.Figure(data=data,layout=layout)
    py.image.save_as(fig, filename=('emotionTimeSeries.png'))


def output_piegraph(audience_data):
    res = audience_data.results

    labels = res.keys()
    values = res.values()

    trace = go.Pie(labels=labels, values=values,
                   marker=dict(
                       colors=["rgb(244, 66, 66)", "rgb(244, 223, 66)", "rgb(66, 128, 244)", "rgb(168, 164, 170)",
                               "rgb(167, 48, 232)"]),
                   textinfo="none", sort=False, showlegend = False)
    layout = go.Layout(width=501, height=501)
    fig = {'data': [trace], 'layout': layout}
    print(trace)
    print(str(audience_data.time))
    py.image.save_as(fig, filename=(str(audience_data.time)+'.png'))


if __name__ == "__main__":
    fileName = 'video.mp4'
    framerate = 1
    set_up_credentials()
    final = getVideoClipResults(fileName, framerate)
    for timestep in final:
        print(timestep.time)
        print(timestep.results)
        output_piegraph(timestep)
    output_linegraph(final)

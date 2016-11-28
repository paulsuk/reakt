#from SimpleCV import Camera
import base64
import time
import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from PIL import Image


GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS.json"

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
        return[]
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
                    'neutral': 0,
                    'total': 0.0}
    for face in faces:
        emotion = False
        if face.joyLikelihood == LIKELY or face.joyLikelihood == VERY_LIKELY:
            num_emotions['joy'] += 1
            emotion = True
        if face.sorrowLikelihood == LIKELY or face.sorrowLikelihood == VERY_LIKELY:
            num_emotions['sorrow'] += 1
            emotion = True
        if face.angerLikelihood == LIKELY or face.angerLikelihood == VERY_LIKELY:
            num_emotions['anger'] += 1
            emotion = True
        if face.surpriseLikelihood == LIKELY or face.surpriseLikelihood == VERY_LIKELY:
            num_emotions['surprise'] += 1
            emotion = True
        if !emotion:
            num_emotions['neutral'] += 1
        num_emotions['total'] += 1
                    'neutral': 0}
    total = 0
    
    if not faces:
        return num_emotions
    
    for face in faces:
        emotion = False
        if face['joyLikelihood'] == "LIKELY" or face['joyLikelihood'] == "VERY_LIKELY":
            num_emotions['joy'] += 1
            emotion = True
        if face['sorrowLikelihood'] == "LIKELY" or face['sorrowLikelihood'] == "VERY_LIKELY":
            num_emotions['sorrow'] += 1
            emotion = True
        if face['angerLikelihood'] == "LIKELY" or face['angerLikelihood'] == "VERY_LIKELY":
            num_emotions['anger'] += 1
            emotion = True
        if face['surpriseLikelihood'] == "LIKELY" or face['surpriseLikelihood'] == "VERY_LIKELY":
            num_emotions['surprise'] += 1
            emotion = True
        if not emotion:
            num_emotions['neutral'] += 1
        total += 1

    per_emotions = {}
    for emotion, value in num_emotions.iteritems():
        per_emotions[emotion] = value

    return per_emotions

def getVideoClipResults(fileName, framerate):
    clip = VideoFileClip(fileName)
    clip.write_images_sequence('frame%03d.jpg', framerate)
    pres = VideoFileClip("video.mp4")
    i = 0
    clip= []
    while i/framerate < math.ceil(pres.duration):
        filename_temp = 'frames\\frame%d.jpg' % i
        pres.save_frame(filename_temp, i/framerate)
        i += 1
    samples = make_img_list_jpg()
    final_results = []
    for i in range(len(samples)):
        image = open(samples[i], 'rb')
        data = getResultsFromSample(image, i/framerate)
        data = getResultsFromSample(image, float(i/framerate))
        final_results.append(data)
    return final_results

def getResultsFromSample(sampleImage, timeStamp):
    faces = detect_face(sampleImage)
    results = audience_response(faces)
    print(results)
    data = audience_data(timeStamp, results)
    return data

def make_img_list_jpg():
    #Make list of image filenames
    image_list = []
    for filename in glob.glob('*.jpg'):
    for filename in glob.glob('frames\*.jpg'):
        image_list.append(filename)
    return image_list

def output_linegraph( audience_data = [] ):
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
    py.image.save_as(fig, filename=('emotionTimeSeries.jpeg'))


def output_piegraph(audience_data):
    py.image.save_as(fig, filename=('emotionTimeSeries.png'))


def output_piegraph(audience_data, i):
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
    py.image.save_as(fig, filename=(str(audience_data.time)+'.png'))
    py.image.save_as(fig, filename=('pi\\' + str(i)+'.png'))

def make_img_list():
    #Make list of image filenames
    image_list = []
    for filename in glob.glob('*.png'):
        image_list.append(filename)
    return image_list

def make_int_list():
    #Filename contains time stamp of each frame in half seconds (2 frames / sec)
    len_list = []
    for filename in glob.glob('*.png'):
        length = os.path.basename(filename).split('.')[0]
        len_list.append(int(length))
    for filename in glob.glob('pi/*.png'):
        image_list.append(filename)
    return image_list

def make_int_list(framerate):
    #Filename contains time stamp of each frame in half seconds (2 frames / sec)
    len_list = []
    for filename in glob.glob('pi/*.png'):
        len_list.append(0.5)
    print(len_list)
    return len_list

def make_gif(im, length, FPS):
    #Make video with the appropriate lengths of each picture 
    full = []
    for i in range(len(length)):
        for j in range(length[i]):
            full.append(im[i])
        for j in range(int(length[i]*FPS)):
            full.append(im[i])
    print(len(full))
    ImageSequenceClip(full, fps=FPS).write_videofile('images.mp4', fps=FPS)

def final_vid():
    pres = VideoFileClip("video.mp4")
    pi = VideoFileClip("images.mp4")
    graph = ImageClip("emotionTimeSeries.jpeg", duration=pres.duration)
    pi = pi.resize((225,225))
    pres = pres.resize((1280,1080))
    CompositeVideoClip([pres,graph.set_pos(("center", "bottom")),pi.set_pos((1000,400))], size=(1280,720)).write_videofile('d1.mp4',fps=60,preset='ultrafast')
    graph = ImageClip("emotionTimeSeries.png", duration=pres.duration)
    pi = pi.resize((225,225))
    graph = graph.resize((1280,250))
    pres = pres.resize((1280,1080))
    CompositeVideoClip([pres,graph.set_pos(("center", "bottom")),pi.set_pos((1000,600))], size=(1280,1080)).write_videofile('d1.mp4',fps=60,preset='ultrafast')


if __name__ == "__main__":
    set_up_credentials()

    final = getVideoClipResults(fileName, framerate)
    print('Paul won')

    for timestep in final:
        output_piegraph(timestep)
        print('yo')
    output_linegraph(final)
    print('Connor won')

    make_gif(make_img_list(), make_int_list(), framerate)
    final_vid()
    print('Grace won')
    framerate = 2
    final = getVideoClipResults("video.mp4", framerate)
    print('Paul won')

    for i in range(len(final)):
        output_piegraph(final[i], i)
        print('done')
    output_linegraph(final)
    print('Connor won')

    make_gif(make_img_list(), make_int_list(framerate), framerate) 
    final_vid()
    print('Grace won')

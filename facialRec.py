from SimpleCV import Camera
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import base64


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
    batch_request = [{
        'image': {
            'content': base64.b64encode(image).decode('utf-8')
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

    return response['responses'][0]['faceAnnotations']

def audience_response(faces):
    num_emotions = {'joy': 0,
                    'sorrow': 0,
                    'anger': 0,
                    'surprise': 0,
                    'total': 0.0}
    for face in faces:
        if face.joyLikelihood == LIKELY or face.joyLikelihood == VERY_LIKELY:
            num_emotions['joy'] += 1
        if face.sorrowLikelihood == LIKELY or face.sorrowLikelihood == VERY_LIKELY:
            num_emotions['sorrow'] += 1
        if face.angerLikelihood == LIKELY or face.angerLikelihood == VERY_LIKELY:
            num_emotions['anger'] += 1
        if face.surpriseLikelihood == LIKELY or face.surpriseLikelihood == VERY_LIKELY:
            num_emotions['surprise'] += 1
        num_emotions['total'] += 1

    per_emotions = {}
    for emotion, value in num_emotions.iteritems():
        per_emotions[emotion] = value / num_emotions['total']
    per_emotions['total'] = num_emotions['total']
    return per_emotions

if __name__ == "__main__":
    # Initialize the camera
    cam = Camera()
    # Loop to continuously get images
    while True:
        # Get Image from camera
        img = cam.getImage()
        # Detect faces
        faces = detect_face(img)
        #Calculate results
        results = audience_response(faces)
        print_results = ""
        for emotion, value in results.iteritems():
            print_results += emotion + ': ' + str(value) + '%\n'
        # Draw info text on image
        img.drawText(print_results)
        # Show the image
        img.show()

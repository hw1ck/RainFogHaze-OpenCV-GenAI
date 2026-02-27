from django.shortcuts import render
import cv2
import os
import numpy as np
from django.conf import settings
from .models import Image_c
from genai_guidance import analyze_weather


# -------- HAZE / FOG REMOVAL FUNCTION --------
def remove_haze(image):
    image = image.astype(np.float64) / 255.0

    # Dark Channel
    dark = np.min(image, axis=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    dark = cv2.erode(dark, kernel)

    # Atmospheric Light
    airlight = np.max(dark)

    # Transmission Map
    transmission = 1 - 0.95 * dark / airlight
    transmission = np.clip(transmission, 0.1, 0.9)

    # Recover Image
    result = np.zeros_like(image)
    for i in range(3):
        result[:, :, i] = (image[:, :, i] - airlight) / transmission + airlight

    result = np.clip(result, 0, 1)
    return (result * 255).astype(np.uint8)

    def get_strength(genai_text):
        text = genai_text.lower()
        if "high" in text:
            return 0.95
        elif "medium" in text:
            return 0.85
        else:
            return 0.75

def remove_haze_param(image, strength):
    import numpy as np
    import cv2

    image = image.astype(np.float64) / 255.0

    # Dark channel
    dark = np.min(image, axis=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    dark = cv2.erode(dark, kernel)

    # Atmospheric light
    airlight = np.max(dark)

    # Transmission map
    transmission = 1 - strength * dark / airlight
    transmission = np.clip(transmission, 0.1, 0.9)

    # Recover image
    result = np.zeros_like(image)
    for i in range(3):
        result[:, :, i] = (image[:, :, i] - airlight) / transmission + airlight

    result = np.clip(result * 255, 0, 255)
    return result.astype(np.uint8)

def get_strength(genai_text):
    text = genai_text.lower()

    if "fog: high" in text or "haze: high" in text:
        return 0.95
    elif "fog: medium" in text or "haze: medium" in text:
        return 0.85
    else:
        return 0.75

# -------- MAIN VIEW --------
def image_convert(request):
    baseline_image = None
    guided_image = None
    genai_result = None
    error_msg = None
    output_image = None
    error_msg = None

    if request.method == 'POST':
        file = request.FILES.get('image')

        # Validate file type
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            error_msg = "Please upload JPG or PNG images only"
            return render(request, "index.html", {"error": error_msg})

        # Save uploaded image
        obj = Image_c.objects.create(image=file, status='image')

        img = cv2.imread(obj.image.path)
        genai_result = analyze_weather(obj.image.path)
        if img is None:
            error_msg = "Image could not be processed"
            return render(request, "index.html", {"error": error_msg})

        # -------- PROCESSING --------
        # -------- BASELINE OPENCV (OLD MODEL - FIXED) --------
        baseline = remove_haze_param(img, 0.8)   # fixed strength (old behavior)

        # Optional sharpening for baseline
        kernel = np.array([[0, -1, 0],
                            [-1, 5, -1],
                            [0, -1, 0]])
        baseline = cv2.filter2D(baseline, -1, kernel)

        # Sharpening for better clarity
        strength = get_strength(genai_result)
        final = remove_haze_param(img, strength)
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        final = cv2.filter2D(final, -1, kernel)

        # Save output
        output_dir = os.path.join(settings.MEDIA_ROOT, "output")
        os.makedirs(output_dir, exist_ok=True)

        # Save baseline output
        baseline_path = os.path.join(output_dir, "opencv_baseline.jpg")
        cv2.imwrite(baseline_path, baseline)

        # Save GenAI guided output
        guided_path = os.path.join(output_dir, "genai_guided.jpg")
        cv2.imwrite(guided_path, final)

        baseline_image = "media/output/opencv_baseline.jpg"
        guided_image = "media/output/genai_guided.jpg"
        genai_result = genai_result
    return render(request, "index.html", {
    "baseline": baseline_image,
    "guided": guided_image,
    "genai": genai_result,
    "error": error_msg
    })
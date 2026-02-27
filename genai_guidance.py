import subprocess

def analyze_weather(image_path):
    prompt = f"""
    Analyze the image and answer briefly:
    Fog level: low / medium / high
    Haze level: low / medium / high
    Rain present: yes / no
    """

    result = subprocess.run(
        ["ollama", "run", "llava", prompt],
        capture_output=True,
        text=True
    )

    return result.stdout
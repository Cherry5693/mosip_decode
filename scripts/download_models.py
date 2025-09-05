from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import subprocess

def download():
    for repo in ["microsoft/trocr-small-printed", "microsoft/trocr-small-handwritten"]:
        print(f"Downloading {repo} ...")
        TrOCRProcessor.from_pretrained(repo)
        VisionEncoderDecoderModel.from_pretrained(repo)
    print("Done.")

if __name__ == "__main__":
    download()
    subprocess.run(["bash", "backend/uvicorn_run.sh"])
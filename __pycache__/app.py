import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
import uvicorn

# Initialize OpenAI client
client = OpenAI(api_key="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")

app = FastAPI(title="Image Description API")


# Function to analyze image
def analyze_image_bytes(image_bytes: bytes):
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that describes objects in an image clearly."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the objects and elements in this image clearly."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ]
            }
        ],
        max_tokens=300
    )
    description = response.choices[0].message.content
    objects = [obj.strip().lower() for obj in description.replace("\n", ",").split(",") if obj.strip()]
    return description, objects


# API endpoint
@app.post("/analyze/")
async def analyze_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        description, objects = analyze_image_bytes(image_bytes)
        return JSONResponse(content={
            "description": description,
            "objects_detected": objects,
            "total_objects": len(objects)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    print("\n🚀 API is running!")
    print("➡️  URL: http://127.0.0.1:8000/analyze/\n")


# Run with uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
.
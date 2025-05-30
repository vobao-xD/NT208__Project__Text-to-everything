import asyncio
import io
import os
from urllib import request
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import openai
from runwayml import AsyncRunwayML
import runwayml
from openai_client_instance import openai_client_instance

from db.schemas import ChatbotContentRequest, EnhanceTextRequest, GenerateAnswerRequest, RunwayTextToVideoRequest, TextToAudioRequest, TextToCodeRequest, TextToImageRequest, TextToVideoRequest

router = APIRouter()

async def get_openai_client(request: Request):
    client = request.app.state.openai_client_instance
    if client is None:
        raise RuntimeError("OpenAI client is not initialized.")
    return client

@router.post("/advanced/text-to-code")
async def text_to_code(payload: TextToCodeRequest,client=Depends(get_openai_client)):
    system_prompt = (
        f"You are an expert coding assistant. "
        f"Generate a complete and functional code snippet in the {payload.language} programming language "
        f"based on the user's request. Only output the raw code, without any surrounding text, "
        f"explanations, or markdown formatting like ```{payload.language}... ```."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": payload.prompt}
    ]
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            temperature=0.2,
            max_tokens=payload.max_tokens
        )
        generated_code = completion.choices[0].message.content
        return {"language": payload.language, "code": generated_code.strip()}
    except openai.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"OpenAI API rate limit exceeded: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"OpenAI API authentication error: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"OpenAI API bad request: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIStatusError as e:
        raise HTTPException(status_code=e.status_code, detail=f"OpenAI API error: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to OpenAI API: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred in /text-to-code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
        
@router.post("/advanced/text-to-image")
async def text_to_image(payload: TextToImageRequest,client=Depends(get_openai_client)):
    if payload.model == "dall-e-3" and payload.n > 1:
         raise HTTPException(status_code=400, detail="DALL-E 3 currently supports generating only one image at a time (n=1).")

    try:
        response = await client.images.generate(
            model="dall-e-3", 
            prompt=payload.prompt,
            n=payload.n,
            size=payload.size,
            quality=payload.quality,
            style=payload.style,
            response_format=payload.response_format
        )

        image_data = []
        if payload.response_format == "url":
            for img in response.data:
                image_data.append({"url": img.url, "revised_prompt": img.revised_prompt})
        elif payload.response_format == "b64_json":
            for img in response.data:
                image_data.append({"b64_json": img.b64_json, "revised_prompt": img.revised_prompt})

        return {"images": image_data}
    except openai.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"OpenAI API rate limit exceeded: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"OpenAI API authentication error: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.BadRequestError as e:
        detail_message = f"OpenAI API bad request: {e.message}"
        if e.body and "error" in e.body and "message" in e.body["error"]:
             detail_message = f"OpenAI API bad request: {e.body['error']['message']}"
        raise HTTPException(status_code=400, detail=detail_message + f" (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIStatusError as e:
        raise HTTPException(status_code=e.status_code, detail=f"OpenAI API error: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to OpenAI API: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred in /text-to-image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.post("/advanced/text-to-video")
async def text_to_video(payload: RunwayTextToVideoRequest):
    runway_api_key = os.getenv("RUNWAYML_API_SECRET")
    if not runway_api_key:
        raise HTTPException(status_code=500, detail="RUNWAYML_API_SECRET environment variable not set.")

    runway_client = AsyncRunwayML(api_key=runway_api_key)
    POLLING_INTERVAL_SECONDS = 10 
    MAX_POLLING_ATTEMPTS = 60 

    try:
        print(f"Initiating RunwayML video generation with model: {payload.model}")
        task_submission = await runway_client.image_to_video.create(
            model=payload.model,
            prompt_image=payload.prompt_image_url, # URL to an image
            prompt_text=payload.prompt_text,
            ratio=payload.ratio,
            duration=payload.duration,
            seed=payload.seed if payload.seed is not None else None # Pass seed if provided
        )
        task_id = task_submission.id
        print(f"RunwayML task submitted with ID: {task_id}")

        for attempt in range(MAX_POLLING_ATTEMPTS):
            await asyncio.sleep(POLLING_INTERVAL_SECONDS)
            task_details = await runway_client.tasks.retrieve(task_id)
            print(f"Polling RunwayML task {task_id}, status: {task_details.status}, attempt: {attempt + 1}")

            if task_details.status == "SUCCEEDED":
                if hasattr(task_details, 'output') and task_details.output and hasattr(task_details.output, 'video_url'):
                    video_url = task_details.output.video_url #
                    return {
                        "message": "Video generation successful.",
                        "task_id": task_id,
                        "video_url": video_url,
                        "details": task_details.model_dump() # Return full task details
                    }
                else:
                    raise HTTPException(status_code=500, detail="Video generation succeeded but no video URL found in response.")
            elif task_details.status == "FAILED":
                error_message = "Video generation failed."
                if hasattr(task_details, 'output') and task_details.output and hasattr(task_details.output, 'error'):
                    error_message = f"Video generation failed: {task_details.output.error}"
                raise HTTPException(status_code=500, detail=error_message)
            # Continue polling if status is PENDING, PROCESSING, THROTTLED etc.
        
        raise HTTPException(status_code=408, detail="Video generation timed out after polling.")

    except runwayml.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"RunwayML API rate limit exceeded: {str(e)}")
    except runwayml.AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"RunwayML API authentication error: {str(e)}. Check RUNWAYML_API_SECRET.")
    except runwayml.BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"RunwayML API bad request: {str(e)}")
    except runwayml.APIStatusError as e: # Catch other RunwayML API errors
        raise HTTPException(status_code=e.status_code if hasattr(e, 'status_code') else 500, detail=f"RunwayML API error: {str(e)}")
    except runwayml.APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to RunwayML API: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred in /text-to-video: {str(e)}")
        # It's good practice to close the client if initialized here, though lifespan manager is better
        # await runway_client.close() # Requires client to be defined outside try if used in finally
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
    finally:
        # Ensure client is closed if initialized within the function
        if 'runway_client' in locals() and runway_client:
            await runway_client.close()

@router.post("/advanced/text-to-audio")
async def text_to_audio(payload: TextToAudioRequest,client=Depends(get_openai_client)):
    try:
        api_params = {
            "model": payload.model,
            "input": payload.text,
            "voice": payload.voice,
            "response_format": payload.response_format,
            "speed": payload.speed
        }
        if payload.model == "gpt-4o-mini-tts" and payload.instructions:
            api_params["instructions"] = payload.instructions

        response = await client.audio.speech.create(**api_params)

        audio_bytes = response.read()


        media_type = f"audio/{payload.response_format}"
        if payload.response_format == "pcm":
            media_type = "audio/L16; rate=24000; channels=1"

        return StreamingResponse(io.BytesIO(audio_bytes), media_type=media_type)

    except openai.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"OpenAI API rate limit exceeded: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"OpenAI API authentication error: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"OpenAI API bad request: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIStatusError as e:
        raise HTTPException(status_code=e.status_code, detail=f"OpenAI API error: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to OpenAI API: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred in /text-to-audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.post("/advanced/generate-answer")
async def generate_answer(payload: GenerateAnswerRequest,client=Depends(get_openai_client)):
    system_prompt = (
        "You are a helpful AI assistant designed to answer questions. "
        "If context is provided, base your answer primarily on that context. "
        "If no context is provided, use your general knowledge. "
        "Strive for accuracy and conciseness."
    )

    user_content = payload.question
    if payload.context:
        user_content = f"Context:\n---\n{payload.context}\n---\n\nQuestion: {payload.question}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            temperature=0.3, 
            max_tokens=payload.max_tokens
        )
        answer = completion.choices[0].message.content
        return {"question": payload.question, "answer": answer.strip()}
    except openai.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"OpenAI API rate limit exceeded: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to OpenAI API: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred in /generate-answer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.post("/advanced/chatbot-content")
async def chatbot_content(payload: ChatbotContentRequest,client=Depends(get_openai_client)):
    messages = [{"role": "system", "content": payload.system_prompt}]
    for msg in payload.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": payload.user_input})

    try:
        completion = await client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            temperature=0.7, 
            max_tokens=payload.max_tokens
        )
        response_content = completion.choices[0].message.content

        new_assistant_message = {"role": "assistant", "content": response_content.strip()}

        return {"response": response_content.strip(), "new_history_message": new_assistant_message}
    except openai.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"OpenAI API rate limit exceeded: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to OpenAI API: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred in /chatbot-content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@router.post("/advanced/enhance")
async def enhance(payload: EnhanceTextRequest,client=Depends(get_openai_client)):
    system_prompt = (
        f"You are a text enhancement AI. Rewrite the following text based on this instruction: "
        f"'{payload.instruction}'. Output only the rewritten text, without any additional commentary or explanation."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": payload.text}
    ]
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            temperature=0.5,
            max_tokens=payload.max_tokens
        )
        enhanced_text = completion.choices[0].message.content
        return {"original_text": payload.text, "instruction": payload.instruction, "enhanced_text": enhanced_text.strip()}
    except openai.RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"OpenAI API rate limit exceeded: {e.message} (Request ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'})")
    except openai.APIConnectionError as e: 
        raise HTTPException(status_code=503, detail=f"Failed to connect to OpenAI API: {e.message}")
    except Exception as e: 
        print(f"An unexpected error occurred in /enhance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")




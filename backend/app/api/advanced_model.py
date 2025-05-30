import asyncio
import base64
import io
import json
import mimetypes
import os
import re
from typing import Any, Dict, Optional
from urllib import request
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
import httpx
from openai import AsyncOpenAI
import openai
from runwayml import AsyncRunwayML
import runwayml
from openai_client_instance import openai_client_instance

from db.schemas import AnalyzeRequest, ChatbotContentRequest, EnhanceTextRequest, FileTextToAnswerResponse, GenerateAnswerRequest, RunwayTextToVideoRequest, TextToAudioRequest, TextToCodeRequest, TextToImageRequest, TextToVideoRequest

router = APIRouter()
IMAGE_MIME_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]
DOCUMENT_MIME_TYPES_FOR_ASSISTANT = [
    "application/pdf", "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # .docx
    "application/msword", # .doc
    "text/markdown", "text/csv",
    # Add more from https://platform.openai.com/docs/assistants/tools/file-search/supported-files
]
ASSISTANT_ID_WITH_FILE_SEARCH = os.environ.get("OPENAI_FILE_SEARCH_ASSISTANT_ID")

async def _handle_image_input(
    client: AsyncOpenAI,
    question: str,
    file_content_b64: str,
    mime_type: str,
    vision_model_override: Optional[str] = None, # New parameter
    detail_level: str = "auto",
    max_tokens: int = 300,
) -> Dict[str, Any]:
    messages_payload = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{file_content_b64}",
                        "detail": detail_level,
                    },
                },
            ],
        }
    ]
    model_to_use = vision_model_override or "gpt-4o" # Use override if provided, else default

    completion = await client.chat.completions.create(
        model=model_to_use,
        messages=messages_payload,
        max_tokens=max_tokens,
    )
    answer = completion.choices[0].message.content or "No answer returned."
    return {
        "answer": answer,
        "model_used": completion.model, # Actual model used
        "usage": completion.usage.model_dump() if completion.usage else None,
    }

async def _handle_document_input(
    client: AsyncOpenAI,
    question: str,
    uploaded_file_for_openai: tuple,
    assistant_id: str,
    assistant_model_override: Optional[str] = None, # New parameter
    # max_tokens_assistant: Optional[int] = 1000 # max_tokens is not directly set on run for answer length
) -> Dict[str, Any]:
    if not assistant_id:
        raise HTTPException(status_code=500, detail="File Search Assistant ID is not configured.")

    try:
        file_object = await client.files.create(
            file=uploaded_file_for_openai, purpose="assistants"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to OpenAI: {str(e)}")

    thread_id_to_delete: Optional[str] = None
    try:
        thread = await client.beta.threads.create()
        thread_id_to_delete = thread.id # Mark for deletion

        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
            attachments=[{"file_id": file_object.id, "tools": [{"type": "file_search"}]}]
        )

        run_params = {
            "thread_id": thread.id,
            "assistant_id": assistant_id,
        }
        if assistant_model_override:
            run_params["model"] = assistant_model_override # Add model override if provided

        run = await client.beta.threads.runs.create_and_poll(**run_params)

        answer_content = "No answer generated or run failed."
        model_used_in_run = run.model # Actual model used by the run
        usage_data = run.usage.model_dump() if run.usage else None

        if run.status == 'completed':
            messages_page = await client.beta.threads.messages.list(
                thread_id=thread.id, order="desc", limit=5
            )
            for msg in messages_page.data:
                if msg.role == "assistant":
                    for content_block in msg.content:
                        if content_block.type == "text":
                            answer_content = content_block.text.value
                            # Citation handling (optional, same as before)
                            if content_block.text.annotations:
                                citations = []
                                for index, annotation in enumerate(content_block.text.annotations):
                                    answer_content = answer_content.replace(annotation.text, f' [{index}]')
                                    if (file_citation := getattr(annotation, 'file_citation', None)):
                                        try:
                                            cited_file = await client.files.retrieve(file_citation.file_id)
                                            citations.append(f'[{index}] {file_citation.quote} - (from {cited_file.filename})')
                                        except Exception:
                                            citations.append(f'[{index}] {file_citation.quote} - (citation from uploaded file)')
                                if citations:
                                    answer_content += "\n\nCitations:\n" + "\n".join(citations)
                            break 
                    if answer_content != "No answer generated or run failed.":
                        break
        elif run.status == 'failed':
            answer_content = f"Run failed. Last error: {run.last_error.message if run.last_error else 'Unknown error'}"
        else:
            answer_content = f"Run did not complete as expected. Status: {run.status}"
            if run.required_action: # E.g. if it stopped for tool calls not submitted
                 answer_content += f". Required action: {run.required_action.type}"


    finally:
        # Clean up uploaded file
        try:
            await client.files.delete(file_object.id)
        except Exception:
            pass # Log if necessary
        # Clean up thread
        if thread_id_to_delete:
            try:
                await client.beta.threads.delete(thread_id_to_delete)
            except Exception:
                pass # Log if necessary

    return {
        "answer": answer_content,
        "model_used": model_used_in_run,
        "usage": usage_data,
    }

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
@router.post("/advanced/file-text-to-answer", response_model=FileTextToAnswerResponse)
async def smart_file_text_to_answer(
    request: Request,
    text: str = Form(..., description="The text query or question related to the file."),
    file: UploadFile = File(..., description="The file to analyze (image, PDF, DOCX, TXT, etc.)."),
    vision_model_override: Optional[str] = Form(None, description="Optional: Override vision model (e.g., 'gpt-4o-mini', 'gpt-4-turbo'). Defaults to 'gpt-4o'."),
    detail_vision: Optional[str] = Form("auto", description="Detail level for vision model ('auto', 'low', 'high')."),
    max_tokens_vision: Optional[int] = Form(300, description="Max tokens for vision model answer."),
    assistant_model_override: Optional[str] = Form(None, description="Optional: Override assistant's model for this run (e.g., 'gpt-3.5-turbo', 'gpt-4o'). Ensures compatibility with file_search."),
    client: AsyncOpenAI = Depends(get_openai_client)
):
    filename = file.filename or "uploaded_file"
    content_type = file.content_type
    file_bytes = await file.read()
    await file.seek(0)

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_details = {
        "filename": filename,
        "content_type": content_type,
        "size": len(file_bytes)
    }

    if content_type == "application/octet-stream" and filename:
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type:
            content_type = guessed_type
            file_details["content_type"] = content_type

    result_data: Dict[str, Any] = {}
    processed_by = "unknown"
    error_message: Optional[str] = None

    try:
        if content_type in IMAGE_MIME_TYPES:
            processed_by = "vision_model"
            b64_content = base64.b64encode(file_bytes).decode("utf-8")
            result_data = await _handle_image_input(
                client, text, b64_content, content_type, 
                vision_model_override=vision_model_override, 
                detail_level=detail_vision, 
                max_tokens=max_tokens_vision
            )
        elif content_type in DOCUMENT_MIME_TYPES_FOR_ASSISTANT:
            processed_by = "assistant_file_search"
            current_assistant_id = ASSISTANT_ID_WITH_FILE_SEARCH
            if not current_assistant_id:
                raise HTTPException(status_code=501, detail="Document processing (File Search Assistant ID) is not configured on the server.")
            
            file_for_openai_upload = (filename, file_bytes)
            result_data = await _handle_document_input(
                client, text, file_for_openai_upload, current_assistant_id,
                assistant_model_override=assistant_model_override
                # max_tokens_assistant=max_tokens_assistant # Not directly used in run create for answer length
            )
        else:
            error_message = f"Unsupported file type: {content_type}. Supported image types: {IMAGE_MIME_TYPES}. Supported document types for search: {DOCUMENT_MIME_TYPES_FOR_ASSISTANT}."
            raise HTTPException(status_code=415, detail=error_message)

    except HTTPException as e:
        # Log e here if needed, e.g., print(f"Caught HTTPException: {e.detail}")
        # Return structure that matches FileTextToAnswerResponse for client consistency
        return FileTextToAnswerResponse(
            answer=result_data.get("answer", "Processing failed due to HTTP error."),
            processed_by=processed_by if processed_by != "unknown" else "error_handler",
            file_details=file_details,
            model_used=result_data.get("model_used"),
            usage=result_data.get("usage"),
            error=str(e.detail) # Use the detail from the HTTPException
        )
    except Exception as e:
        print(f"An unexpected error occurred in smart_file_text_to_answer: {str(e)}") # Basic logging
        # logger.error("Error in smart_file_text_to_answer", exc_info=True) # More detailed logging
        error_message = f"An unexpected internal error occurred: {str(e)}"
        return FileTextToAnswerResponse(
            answer="Failed due to an internal server error.",
            processed_by="error_handler",
            file_details=file_details,
            error=error_message
        )

    return FileTextToAnswerResponse(
        answer=result_data.get("answer", "No answer content."),
        processed_by=processed_by,
        file_details=file_details,
        model_used=result_data.get("model_used"),
        usage=result_data.get("usage"),
        error=error_message # Should be None if successful
    )
TASK_LIST_DESCRIPTION = """
Here are the available task types and their keys:
1. Text to Code
   Key: "text-to-code"
   Description: Generate code from a text description.
   Relevant input: User's text prompt describing the code, target language.

2. Text to Image
   Key: "text-to-image"
   Description: Generate an image from a text description.
   Relevant input: User's text prompt describing the image.

3. Text to Audio
   Key: "text-to-audio"
   Description: Convert text to speech.
   Relevant input: User's text to be converted.

4. Text to Answer (Question Answering)
   Key: "generate-answer"
   Description: Answer a question, possibly with context.
   Relevant input: User's question, optional context.

5. Chatbot Conversation Content
   Key: "chatbot-content"
   Description: Continue a chat conversation.
   Relevant input: User's current message, possibly conversation history.

6. Enhanced Text
   Key: "enhance-text"  # Corrected from "enchance"
   Description: Enhance or modify existing text based on an instruction.
   Relevant input: User's text to enhance, instruction for enhancement.

7. File + Text to Answer (File-Based Question Answering)
   Key: "file-text-to-answer"
   Description: Answer a question based on the content of an uploaded file (image or document) and a text query.
   Relevant input: Uploaded file (image or document), user's text query.
   
8. Image URL + Text to Answer (Image URL-Based Question Answering)
    Key: "image-url-to-answer" # Adding a distinct key if image_url is the primary input
    Description: Answer a question based on an image URL and a text query.
    Relevant input: Image URL, user's text query.

If the input does not clearly match any of these tasks, or if essential information for a task seems missing, use the key "unknown_task".
you MUST respond with a single, valid JSON object containing only one key: 'task'. The value for 'task' MUST be one of the provided task keys (e.g., \"text-to-code\", \"file-text-to-answer\", \"unknown_task\"). Do not include any other text, explanations, or markdown formatting like ```json or ``` around the JSON object.
"""

# Programmatically extract valid task keys for validation later (optional but good)
VALID_TASK_KEYS = [
    "text-to-code", "text-to-image", "text-to-audio", "generate-answer",
    "chatbot-content", "enhance-text", "file-text-to-answer",
    "image-url-to-answer", "unknown_task"
]


@router.post("/advanced/analyze")
async def analyze(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    client=Depends(get_openai_client),
):
    prompt_parts = ["Analyze the following user input to determine the most appropriate task type.\n\nUser Input Details:\n"]
    has_input = False

    if text:
        prompt_parts.append(f"- Text provided: \"{text}\"\n")
        has_input = True
    if file:
        prompt_parts.append(f"- File uploaded: name='{file.filename}', content_type='{file.content_type}'\n")
        has_input = True

    if not has_input:
        raise HTTPException(status_code=400, detail="No input provided. Please provide text, an image_url, or upload a file.")

    prompt_parts.append("\nBased on the user input, identify exactly one task key from the list below.\n")
    prompt_parts.append(TASK_LIST_DESCRIPTION)
    prompt_parts.append("\nYou MUST respond with a single, valid JSON object containing only one key: 'task'. The value for 'task' MUST be one of the provided task keys (e.g., \"text-to-code\", \"file-text-to-answer\", \"unknown_task\"). Do not include any other text, explanations, or markdown formatting like ```json or ``` around the JSON object.")
    
    final_prompt = "".join(prompt_parts)

    try:
        completion = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes user inputs to classify them into predefined task types. Your response MUST be a single, valid JSON object formatted exactly as: {\"task\": \"CHOSEN_TASK_KEY\",\"parameters\": {\"text\": \"TEXT_INPUT\", \"file\": \"FILE_INPUT\", \"image_url\": \"IMAGE_URL_INPUT\"}}. Do not add any extra text, explanations, or markdown."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0, 
            response_format={"type": "json_object"} 
        )
        result_text = completion.choices[0].message.content
        

        if not result_text:
            print("OpenAI returned an empty response content.")
            raise HTTPException(status_code=500, detail="AI returned an empty response.")

        try:
            result_json = json.loads(result_text)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError despite response_format=json_object. Raw: '{result_text}'. Error: {e}")
            match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if match:
                try:
                    result_json = json.loads(match.group())
                except json.JSONDecodeError:
                    raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON even after regex. Raw content: {result_text}")
            else:
                raise HTTPException(status_code=500, detail=f"AI response was not valid JSON and no JSON object found. Raw content: {result_text}")

        task = result_json.get("task")

        if not task:
            print(f"Valid JSON returned, but 'task' key is missing or null: {result_json}")
            raise HTTPException(status_code=500, detail="AI response is valid JSON but missing the 'task' key or task is null.")
        
        if task not in VALID_TASK_KEYS:
            print(f"Warning: AI returned a task ('{task}') not in the predefined VALID_TASK_KEYS. Treating as 'unknown_task'. Original JSON: {result_json}")

        return {result_json}

    except httpx.HTTPStatusError as e: # Catch errors from OpenAI client (e.g., auth, rate limits)
        error_detail_msg = str(e)
        if e.response and e.response.content:
            try:
                error_data = e.response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    error_detail_msg = error_data["error"]["message"]
            except Exception:
                pass
        print(f"OpenAI API error: {e.response.status_code if e.response else 'Unknown status'} - {error_detail_msg}")
        raise HTTPException(status_code=e.response.status_code if e.response else 500, detail=f"OpenAI API error: {error_detail_msg}")
    except Exception as e:
        print(f"An unexpected error occurred in /analyze: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

    
    




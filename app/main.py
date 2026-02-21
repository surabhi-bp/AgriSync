from fastapi import FastAPI, Form, Response # <-- Added Response here
from twilio.twiml.messaging_response import MessagingResponse
import uvicorn

app = FastAPI()

@app.post("/message")
async def whatsapp_webhook(
    Body: str = Form(...), 
    From: str = Form(...)
):
    print(f"--- NEW MESSAGE ---")
    print(f"Sender: {From}")
    print(f"Message: {Body}")
    print(f"-------------------")
    
    # Formulate the response
    response = MessagingResponse()
    reply_text = f"AgriSync received: '{Body}'. Our AI is processing your request."
    response.message(reply_text)
    
    # CRITICAL FIX: Tell FastAPI to send this back strictly as XML!
    return Response(content=str(response), media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
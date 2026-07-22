import asyncio
import httpx
import sys

async def main():
    base_url = "http://127.0.0.1:8001/api/v1"
    
    # 1. Login
    print("Logging in...")
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(f"{base_url}/auth/login", json={
            "email": "test2@test.com",
            "password": "password123"
        })
        if r.status_code != 200:
            print("Login failed:", r.text)
            return
        token = r.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful")

        # 2. Upload Document
        print("Uploading document...")
        files = {'file': ('dummy.pdf', b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\n', 'application/pdf')}
        r = await client.post(f"{base_url}/documents", headers=headers, files=files)
        if r.status_code != 200:
            print("Upload failed:", r.text)
            return
        doc_id = r.json()["data"]["id"]
        print(f"Document uploaded: {doc_id}")
        
        # 3. Create Conversation
        print("Creating conversation...")
        r = await client.post(f"{base_url}/conversations?document_id={doc_id}", headers=headers)
        if r.status_code != 200:
            print("Create conversation failed:", r.text)
            return
        conv_id = r.json()["id"]
        print(f"Conversation created: {conv_id}")

        # 4. Start Turn (Message)
        print("Starting turn...")
        r = await client.post(f"{base_url}/conversations/{conv_id}/messages", headers=headers, json={
            "question": "What is this document?"
        })
        if r.status_code != 200:
            print("Start turn failed:", r.text)
            return
        msg_id = r.json()["message_id"]
        print(f"Message created: {msg_id}")

        # 5. Stream
        print("Streaming response...")
        async with client.stream("GET", f"{base_url}/conversations/{conv_id}/messages/{msg_id}/stream", headers=headers) as response:
            if response.status_code != 200:
                print("Stream failed:", await response.aread())
                return
            async for chunk in response.aiter_text():
                print(chunk, end="")
        print("\nEnd of stream")
        print("SUCCESS! End-to-end integration is completely functional.")

if __name__ == "__main__":
    asyncio.run(main())

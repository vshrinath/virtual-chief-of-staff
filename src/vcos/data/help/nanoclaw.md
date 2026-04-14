# Connecting to NanoClaw (WhatsApp/Voice)

NanoClaw is the "Capture Layer" for your Chief of Staff. It allows you to send voice notes or text messages via WhatsApp and have them automatically saved to your VCoS inbox.

## How it works
1. **NanoClaw captures**: You speak a voice note into WhatsApp.
2. **NanoClaw transcribes**: It converts the audio to text (either using a cloud provider or your local VCoS Whisper setup).
3. **NanoClaw archives**: It calls the `vcos archive` command to save the text into your vault.

## Setup
To connect NanoClaw to your VCoS:
- Ensure `vcos` is installed on your system.
- In your NanoClaw configuration, set the archive command to:
  ```bash
  vcos archive --content "{text}" --path "writing/articles/1-inbox/{date}.md"
  ```

Once set up, your WhatsApp messages will appear in your `vcos standup` every morning.

from pyngrok import ngrok

def start_ngrok():
    ngrok.set_auth_token(open('ngrok_token.txt', 'r').read().strip())
    # Start ngrok tunnel on port 8000
    ngrok_process = ngrok.connect(8000)
    print("Tunnel started at ", ngrok_process.public_url)
    print("ngrok tunnel started on port 8000.")
    print("Press Enter to stop the ngrok tunnel.")

    try:
        # Wait for the user to press Enter
        input()
    except KeyboardInterrupt:
        pass
    finally:
        # Terminate the ngrok process
        ngrok_process.terminate()
        print("ngrok tunnel stopped.")


if __name__ == "__main__":
    start_ngrok()
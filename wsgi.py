from app import create_app  # or however you create your app

app = create_app()  # This should be at module level

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

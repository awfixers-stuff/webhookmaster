# Webhook Transformer

This project ingests webhooks, transforms their payloads, and sends them to new destinations.

## Usage

### Backend (Python Flask)

1.  **Install the dependencies:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Run the application locally:**

    ```bash
    source .venv/bin/activate
    python3 app.py
    ```

3.  **Send a POST request to `/webhook` with a JSON payload.**

    You can specify the `source` and `format` of the webhook using query parameters.

    **Examples:**

    *   **Default (no transformation):**

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello, world!"}' http://127.0.0.1:5000/webhook
        ```

    *   **GitHub to Discord:**

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"ref": "refs/heads/main", "repository": {"full_name": "test/repo"}, "pusher": {"name": "testuser"}, "commits": [{}, {}]}' http://127.0.0.1:5000/webhook?source=github&format=discord
        ```

    *   **Stripe to Microsoft Teams:**

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"data": {"object": {"amount": 1000, "currency": "usd", "billing_details": {"email": "test@example.com"}}}}' http://127.0.0.1:5000/webhook?source=stripe&format=msteams
        ```

    *   **Default to Slack:**

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello, world!"}' http://127.0.0.1:5000/webhook?format=slack
        ```

    *   **Default to Email:**

        To send emails, create a `.env` file in the project root with the following environment variables:

        ```
        EMAIL_SENDER=your_email@example.com
        EMAIL_PASSWORD=your_email_password
        EMAIL_RECEIVER=recipient@example.com
        SMTP_HOST=smtp.example.com
        SMTP_PORT=587
        ```

        Then, send a webhook like this:

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"subject": "Test Email", "body": "This is a test email body."}' http://127.0.0.1:5000/webhook?format=email
        ```

    *   **Shopify (orders/create) to Default:**

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"id": 1234567890, "email": "john.doe@example.com", "total_price": "50.00", "currency": "USD", "line_items": []}' http://127.0.0.1:5000/webhook?source=shopify
        ```

    *   **Wix (order-related) to Default:**

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"orderNumber": "10002", "payments": [{"amount": {"value": "0.01", "currency": "EUR"}}]}' http://127.0.0.1:5000/webhook?source=wix
        ```

    *   **Cloudflare (Stream Live Input) to Default:**

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"name": "Test Webhook", "text": "A test event", "ts": 123456789, "data": {"notification_name": "Stream Live Input", "input_id": "eb222fcca08eeb1ae84c981ebe8aeeb6", "event_type": "live_input.disconnected", "updated_at": "2022-01-13T11:43:41.855717910Z"}}' http://127.0.0.1:5000/webhook?source=cloudflare
        ```

    *   **Webflow (form submission) to Default:**

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"formId": "form123", "submissionId": "sub456", "data": {"email": "test@webflow.com", "name": "Webflow User"}, "siteId": "site789", "triggeredBy": "form_submission", "triggeredAt": "2025-07-15T10:00:00.000Z"}' http://127.0.0.1:5000/webhook?source=webflow
        ```

### Frontend (React with shadcn/ui)

1.  **Install the dependencies:**

    ```bash
    cd frontend
    bun install
    ```

2.  **Run the application locally:**

    ```bash
    cd frontend
    bun run dev
    ```

    The frontend application will typically run on `http://localhost:5173` (or another available port).

## Rate Limiting

### Backend Rate Limiting

The Flask backend implements rate limiting using `Flask-Limiter`. The `/webhook` endpoint is limited to **10 requests per minute** per client IP address. There are also default limits of **200 requests per day** and **50 requests per hour**.

### Frontend Rate Limiting

The frontend implements a client-side debounce mechanism to prevent excessive requests. The "Transform Webhook" button is disabled while a transformation request is in progress, and subsequent clicks within a 500ms window will be ignored until the current request completes or the debounce period passes.

## Security Enhancements

Several security enhancements have been implemented:

*   **`debug=True` Removed:** The `debug=True` flag has been removed from the Flask application's `app.run()` call, preventing sensitive information exposure and potential remote code execution in production environments.
*   **Whitelisting for Dynamic Imports:** The `source` and `output_format` parameters are now strictly validated against a whitelist of allowed modules. This prevents malicious users from injecting arbitrary module names and potentially executing unauthorized code.
*   **Non-Root User in Dockerfile:** The Dockerfile now configures the application to run as a non-root user (`appuser`). This significantly reduces the attack surface and limits the potential damage if an attacker gains control of the container.

## Dockerization and Deployment

This application can be containerized using Docker and deployed to platforms that support Docker containers, such as Cloudflare Workers (with Docker support) or Fly.io.

1.  **Build the Docker Image:**

    Navigate to the project root and run:

    ```bash
    docker build -t webhook-transformer .
    ```

2.  **Run the Docker Image Locally (Optional):

    ```bash
    docker run -p 5000:5000 webhook-transformer
    ```

    Then, you can test it using the `curl` commands above, replacing `http://127.0.0.1:5000` with `http://localhost:5000`.

3.  **Deploy to Cloudflare:**

    For deployment to Cloudflare Workers with Docker support, refer to the official Cloudflare documentation on deploying containerized applications. You will typically need to push your Docker image to a registry (e.g., Docker Hub, Cloudflare Container Registry) and then configure your Cloudflare Worker to use that image.

4.  **Deploy to Fly.io:**

    For deployment to Fly.io, ensure you have the `flyctl` CLI installed and configured. Navigate to the project root and run `fly launch` to create a `fly.toml` configuration file, then `fly deploy` to deploy your application. Fly.io will automatically detect your `Dockerfile` and build/deploy the image.
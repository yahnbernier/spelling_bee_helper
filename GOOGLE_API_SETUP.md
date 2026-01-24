# Google Docs API Setup Instructions

To use the "Append" feature that writes words back to your Google Drive document, you need to set up Google API credentials using a **Service Account** (recommended for server deployments).

## Steps:

### 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Docs API** for your project:
   - Go to **APIs & Services** > **Library**
   - Search for "Google Docs API"
   - Click **Enable**

### 2. Create a Service Account
1. In the Google Cloud Console, go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **Service Account**
3. Enter a name (e.g., "Spelling Bee Service Account")
4. Click **Create and Continue**
5. Skip the optional steps and click **Done**

### 3. Create and Download Service Account Key
1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key** > **Create new key**
4. Choose **JSON** format
5. Click **Create** - the key file will download automatically
6. Rename the downloaded file to `service-account-key.json`
7. Place it in your project root directory (same folder as `app.py`)

### 4. Share Your Google Doc with the Service Account
**CRITICAL STEP:** The service account needs access to your Google Doc!

1. Open the JSON key file and copy the `client_email` value (looks like: `your-service@project-id.iam.gserviceaccount.com`)
2. Open your Google Drive document in a browser
3. Click the **Share** button
4. Paste the service account email
5. Grant **Editor** permissions
6. Click **Share**

### 5. Install Required Packages
Run this command to install the Google API libraries:
```bash
pip install -r requirements.txt
```

Or install them individually:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 6. Test the Integration
Click the "Append" button in your application - it should now work without requiring browser authentication!

### 7. Security Notes
- **DO NOT** commit `service-account-key.json` to version control
- Add it to your `.gitignore` file (already included)
- For Kubernetes/cloud deployments, use secrets to store the key file

## For Kubernetes/Cloud Deployments (kuberns.cloud)

### Upload Service Account Key as Secret:

```bash
# Create a Kubernetes secret from your service account key
kubectl create secret generic google-service-account \
  --from-file=service-account-key.json=./service-account-key.json
```

### Mount the Secret in Your Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spelling-bee
spec:
  template:
    spec:
      containers:
      - name: spelling-bee
        image: your-image:tag
        volumeMounts:
        - name: google-credentials
          mountPath: /app/service-account-key.json
          subPath: service-account-key.json
          readOnly: true
      volumes:
      - name: google-credentials
        secret:
          secretName: google-service-account
```

The app will automatically find and use the `service-account-key.json` file.

## How It Works

When you click the "Append" button:
1. The selected words are sent to the Flask backend
2. The backend authenticates with Google Docs API
3. It reads the current document content
4. Adds the new words to the existing words
5. Sorts all words alphabetically
6. Replaces the entire document content with the sorted list
7. Reloads the word list in the app

## Troubleshooting

- **"credentials.json not found"**: Make sure you've downloaded and placed the credentials file in the project root
- **Authentication window doesn't open**: Check your firewall settings
- **Permission errors**: Make sure you're using the same Google account that owns the document

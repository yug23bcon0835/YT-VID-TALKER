# 🚀 Deployment Guide

This guide covers deploying the YTVidTalker application to different environments.

## Table of Contents
- [Overview](#overview)
- [Environment Configuration](#environment-configuration)
- [Local Development](#local-development)
- [Vercel Deployment](#vercel-deployment)
- [Troubleshooting](#troubleshooting)

## Overview

YTVidTalker is a full-stack application consisting of:
- **Frontend**: Next.js 16 (React 19, TypeScript)
- **Backend**: FastAPI (Python)

The application uses intelligent API routing that automatically adapts to the deployment environment.

## Environment Configuration

### API URL Configuration

The application uses the `NEXT_PUBLIC_API_URL` environment variable to determine how to connect to the backend:

- **Development**: Set to your local backend URL (e.g., `http://localhost:8000`)
- **Production/Vercel**: Leave empty or unset (uses relative URLs with Vercel rewrites)

### Environment Variables

#### Frontend (.env.local)

```env
# API Configuration
# For local development with separate backend server:
NEXT_PUBLIC_API_URL=http://localhost:8000

# For Vercel deployment, remove or leave empty:
# NEXT_PUBLIC_API_URL=
```

#### Backend (Python environment)

```env
# AI Services
GROQ_API_KEY=your_groq_api_key
SARVAM_API_KEY=your_sarvam_api_key
PINECONE_API_KEY=your_pinecone_api_key

# Azure Storage
AZURE_STORAGE_ACCOUNT=your_azure_account
AZURE_STORAGE_KEY=your_azure_key
AZURE_FILESYSTEM=your_filesystem_name
```

## Local Development

### Setup

1. **Install dependencies**
   ```bash
   # Frontend
   pnpm install
   
   # Backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   
   Create `.env.local` in the project root:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   GROQ_API_KEY=your_key_here
   SARVAM_API_KEY=your_key_here
   PINECONE_API_KEY=your_key_here
   AZURE_STORAGE_ACCOUNT=your_account
   AZURE_STORAGE_KEY=your_key
   AZURE_FILESYSTEM=your_filesystem
   ```

3. **Start development servers**
   
   Terminal 1 - Frontend:
   ```bash
   pnpm dev
   ```
   
   Terminal 2 - Backend:
   ```bash
   cd api
   uvicorn index:app --reload --port 8000
   ```

4. **Access the application**
   
   Open [http://localhost:3000](http://localhost:3000)

## Vercel Deployment

### Prerequisites

- Vercel account
- GitHub/GitLab/Bitbucket repository
- All required API keys

### Deployment Steps

1. **Connect Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New Project"
   - Import your Git repository

2. **Configure Build Settings**
   
   Vercel automatically detects the Next.js configuration. No changes needed.

3. **Set Environment Variables**
   
   In the Vercel project settings, add the following environment variables:
   
   ```
   GROQ_API_KEY=your_groq_api_key
   SARVAM_API_KEY=your_sarvam_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   AZURE_STORAGE_ACCOUNT=your_azure_account
   AZURE_STORAGE_KEY=your_azure_key
   AZURE_FILESYSTEM=your_filesystem_name
   ```
   
   **Important**: Do NOT set `NEXT_PUBLIC_API_URL` in production. The application automatically uses relative URLs when this variable is not set.

4. **Deploy**
   
   Click "Deploy" and Vercel will:
   - Build the Next.js frontend
   - Deploy the FastAPI backend as serverless functions
   - Configure automatic rewrites from `/api/*` to the Python backend

5. **Verify Deployment**
   
   Once deployed, test the following:
   - Application loads correctly
   - Theme toggle works
   - Video processing endpoint responds
   - Q&A functionality works
   - Blog generation works

### Automatic Deployments

Vercel automatically deploys:
- **Production**: Pushes to the main/master branch
- **Preview**: Pull requests and other branches

### vercel.json Configuration

The project includes a `vercel.json` configuration file that sets up URL rewrites:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/index.py"
    }
  ]
}
```

This configuration:
- Routes all `/api/*` requests to the Python FastAPI backend
- Allows the frontend to use relative URLs in production
- Simplifies deployment without changing API endpoints

## How It Works

### API URL Resolution

The application uses a smart API configuration utility (`lib/api-config.ts`):

```typescript
export const getApiUrl = (): string => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
  return apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
};

export const getApiEndpoint = (endpoint: string): string => {
  const baseUrl = getApiUrl();
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${normalizedEndpoint}`;
};
```

**In Development** (with `NEXT_PUBLIC_API_URL=http://localhost:8000`):
- API call: `getApiEndpoint("/api/process-video")`
- Result: `http://localhost:8000/api/process-video`

**In Production** (without `NEXT_PUBLIC_API_URL`):
- API call: `getApiEndpoint("/api/process-video")`
- Result: `/api/process-video`
- Vercel rewrites to: `api/index.py` (Python serverless function)

## Troubleshooting

### Issue: API calls fail in development

**Solution**: Ensure `NEXT_PUBLIC_API_URL` is set in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Issue: API calls fail in production

**Solution**: 
1. Remove `NEXT_PUBLIC_API_URL` from Vercel environment variables
2. Verify `vercel.json` includes the rewrites configuration
3. Check Vercel function logs for Python errors

### Issue: Environment variables not working

**Solution**:
1. Restart the Next.js development server after changing `.env.local`
2. In Vercel, redeploy after adding/changing environment variables
3. Remember: Only `NEXT_PUBLIC_*` variables are exposed to the browser

### Issue: Python modules not found in Vercel

**Solution**:
1. Ensure all dependencies are in `requirements.txt`
2. Check that `python_helpers` imports use correct paths
3. Verify the `sys.path.append` in `api/index.py`

### Issue: Build fails on Vercel

**Solution**:
1. Check build logs for specific errors
2. Ensure Node.js version compatibility (18+)
3. Verify Python version (3.8+)
4. Check for TypeScript errors (though `ignoreBuildErrors` is set)

## Best Practices

1. **Never commit** `.env.local` or `.env` files
2. **Use separate** API keys for development and production
3. **Test locally** before deploying to Vercel
4. **Monitor** Vercel function logs for errors
5. **Set up** Vercel Analytics for usage insights (already included)
6. **Use preview deployments** to test changes before merging to production

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI on Vercel](https://vercel.com/docs/frameworks/python)
- [Environment Variables in Next.js](https://nextjs.org/docs/basic-features/environment-variables)

---

For more information, see the main [README.md](README.md).

# Quick Reference - Vercel Deployment

## 🚀 Quick Setup

### Local Development
```bash
# 1. Copy environment template
cp .env.local.example .env.local

# 2. Edit .env.local and add your API keys
NEXT_PUBLIC_API_URL=http://localhost:8000
GROQ_API_KEY=your_key
SARVAM_API_KEY=your_key
PINECONE_API_KEY=your_key
# ... other keys

# 3. Start development
pnpm dev              # Terminal 1 - Frontend (port 3000)
uvicorn api.index:app --reload --port 8000  # Terminal 2 - Backend
```

### Vercel Deployment
```bash
# 1. Connect repo to Vercel
# 2. Add environment variables in Vercel dashboard:
GROQ_API_KEY=xxx
SARVAM_API_KEY=xxx
PINECONE_API_KEY=xxx
AZURE_STORAGE_ACCOUNT=xxx
AZURE_STORAGE_KEY=xxx
AZURE_FILESYSTEM=xxx

# ⚠️ DO NOT SET: NEXT_PUBLIC_API_URL (leave empty)

# 3. Deploy (automatic)
git push origin main
```

## 📝 Environment Variables

| Variable | Development | Production | Notes |
|----------|-------------|------------|-------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | *(empty)* | Auto-detects environment |
| `GROQ_API_KEY` | Required | Required | AI inference |
| `SARVAM_API_KEY` | Required | Required | Transcription |
| `PINECONE_API_KEY` | Required | Required | Vector DB |
| `AZURE_STORAGE_*` | Required | Required | File storage |

## 🔧 Key Files

| File | Purpose |
|------|---------|
| `lib/api-config.ts` | API URL configuration utility |
| `.env.local` | Local development config (gitignored) |
| `.env.local.example` | Template for local setup |
| `.env.production.example` | Template for Vercel |
| `vercel.json` | Vercel deployment config |

## 💡 How It Works

```typescript
// In app/page.tsx
import { getApiEndpoint } from "@/lib/api-config";

// Development: → http://localhost:8000/api/process-video
// Production:  → /api/process-video (Vercel rewrites to Python)
const response = await fetch(getApiEndpoint("/api/process-video"), {
  method: "POST",
  // ...
});
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| API calls fail in dev | Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local` |
| API calls fail in prod | Remove `NEXT_PUBLIC_API_URL` from Vercel |
| Build fails | Check environment variables are set |
| Backend not found | Verify `vercel.json` rewrites are configured |

## 📚 Documentation

- Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- All changes: [CHANGES.md](CHANGES.md)
- Quick summary: [SUMMARY.md](SUMMARY.md)
- Validation: [VALIDATION.md](VALIDATION.md)

## ✅ Checklist

**Before Development:**
- [ ] Copy `.env.local.example` to `.env.local`
- [ ] Add all API keys
- [ ] Install dependencies: `pnpm install`
- [ ] Start both frontend and backend

**Before Deployment:**
- [ ] Push code to repository
- [ ] Connect repository to Vercel
- [ ] Add all environment variables (except `NEXT_PUBLIC_API_URL`)
- [ ] Verify build succeeds
- [ ] Test deployed application

**After Deployment:**
- [ ] Test video processing
- [ ] Test Q&A functionality
- [ ] Test blog generation
- [ ] Check Vercel function logs

## 🎯 Remember

1. **Development**: Always set `NEXT_PUBLIC_API_URL` in `.env.local`
2. **Production**: Never set `NEXT_PUBLIC_API_URL` in Vercel
3. **Security**: Never commit `.env.local` (already in `.gitignore`)
4. **Build**: Always test `pnpm build` before deploying

---

For detailed information, see [DEPLOYMENT.md](DEPLOYMENT.md)

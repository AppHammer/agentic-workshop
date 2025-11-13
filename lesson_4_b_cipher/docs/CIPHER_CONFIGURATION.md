# Cipher Memory Agent Configuration Guide

## Overview

Cipher is a memory-enabled AI agent that stores and retrieves knowledge using vector embeddings for semantic search. This guide explains how to configure cipher for proper memory persistence.

## Architecture

Cipher uses **two separate API providers**:

1. **LLM Provider (OpenRouter)**: For reasoning and chat
   - Model: `gpt-4o-mini`
   - Purpose: Generate responses, analyze code, answer questions
   - Cost: Variable by model
   
2. **Embedding Provider (OpenAI)**: For memory storage
   - Model: `text-embedding-3-small`
   - Purpose: Generate vector embeddings for semantic search
   - Cost: ~$0.00002 per 1k tokens (minimal)

### Why Two Providers?

- **OpenRouter** offers cost-effective access to various LLMs but doesn't provide embedding models
- **OpenAI** provides industry-standard embedding models required for vector storage
- Separating concerns allows using the best tool for each purpose

## Configuration Files

### 1. `.env` File

```env
# OpenRouter - Used by cipher for LLM reasoning (gpt-4o-mini)
OPENROUTER_API_KEY="your-openrouter-key-here"

# Vector Store Configuration
VECTOR_STORE_TYPE="in-memory"

# OpenAI - REQUIRED for cipher memory embeddings (text-embedding-3-small)
# Obtain key from: https://platform.openai.com/api-keys
OPENAI_API_KEY="your-openai-key-here"
```

### 2. `memAgent/cipher.yml` File

```yaml
# MCP Servers
mcpServers: 
  filesystem:
    type: stdio
    command: npx
    args:
      - -y
      - '@modelcontextprotocol/server-filesystem'
      - .

# LLM Configuration (OpenRouter)
llm:
  provider: openrouter
  model: gpt-4o-mini
  apiKey: "your-openrouter-key"  # Or use ${OPENROUTER_API_KEY}
  maxIterations: 50

# System Prompt
systemPrompt:
  enabled: true
  content: |
    You are an AI programming assistant focused on coding and reasoning tasks.
```

## Setup Instructions

### Step 1: Obtain API Keys

#### OpenRouter API Key (Already Configured)
- ✅ Already set in `.env` file
- No action needed

#### OpenAI API Key (Required for Memory)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-` or `sk-`)
5. Update `.env` file:
   ```env
   OPENAI_API_KEY="sk-proj-your-actual-key-here"
   ```

### Step 2: Verify Configuration

Test that cipher can access both APIs:

```bash
# Test cipher with memory operations
cipher "store this fact: cipher now has proper OpenAI embeddings configured"
```

Expected output: Success message with memory stored

### Step 3: Test Memory Storage

```bash
# Store a test fact
cipher "remember that the project uses FastAPI for backend and React for frontend"

# Verify retrieval
cipher "what backend framework does this project use?"
```

Expected: Cipher should retrieve the stored fact

## Current Status

### ✅ Configured
- OpenRouter API key for LLM (gpt-4o-mini)
- Cipher MCP server setup
- Vector store type (in-memory)

### ❌ Blocked - Requires OpenAI Key
- Memory persistence (embeddings)
- Semantic knowledge search
- QA findings storage

### Knowledge Extracted but Not Stored
From `docs/v0.0.2/implementation/v0.0.2-qa-summary.md`:
- BUG-v0.0.2-001: Customer profile update failure
- Root cause analysis
- Recommended fixes
- Testing lessons learned
- QA best practices

## Post-Configuration Tasks

Once OpenAI API key is added:

1. **Test Memory Storage**
   ```bash
   cipher "store the BUG-v0.0.2-001 details"
   ```

2. **Store QA Findings**
   - Critical bugs
   - Root cause analyses  
   - Testing recommendations
   - Lessons learned

3. **Verify Retrieval**
   ```bash
   cipher "what critical bugs were found in v0.0.2?"
   ```

## Troubleshooting

### Error: "Invalid API key for provider 'OpenAI'"
**Cause**: OpenAI API key is missing or invalid
**Solution**: Add valid OpenAI API key to `.env` file

### Error: "Embeddings disabled due to failure"
**Cause**: Cipher cannot access OpenAI embedding service
**Solution**: 
1. Verify `OPENAI_API_KEY` in `.env`
2. Ensure key is valid (not expired)
3. Check OpenAI account has available credits

### Memory Operations Return Empty
**Cause**: No embeddings stored yet
**Solution**: Store some knowledge first using cipher

## Cost Considerations

### OpenRouter (LLM)
- gpt-4o-mini: ~$0.15 per 1M input tokens
- Already configured and working

### OpenAI (Embeddings)
- text-embedding-3-small: ~$0.02 per 1M tokens
- Extremely cost-effective for memory storage
- Example: 1000 QA findings ≈ $0.04

### Total Monthly Cost Estimate
For typical usage (100 interactions/day):
- LLM costs: $5-10/month
- Embedding costs: <$1/month
- **Total: ~$6-11/month**

## Security Best Practices

1. **Never commit API keys to git**
   - `.env` is in `.gitignore`
   - Use environment variables in production

2. **Rotate keys periodically**
   - OpenRouter: Every 90 days
   - OpenAI: Every 90 days

3. **Monitor usage**
   - Check OpenAI dashboard for embedding costs
   - Set usage limits to prevent overages

## Next Steps

1. Add OpenAI API key to `.env`
2. Test memory storage with simple fact
3. Store v0.0.2 QA findings in cipher memory
4. Verify retrieval works correctly
5. Document memory storage success

## References

- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Cipher MCP Documentation](https://github.com/your-repo/cipher-docs)
- [QA Summary Document](v0.0.2/implementation/v0.0.2-qa-summary.md)
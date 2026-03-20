# AI Provider Strategy

ChurchClaw should be vendor-flexible by design.

## Base Approach

1. Use native Clawith provider config where possible.
2. Add abstraction only when needed:
   - LiteLLM (self-hosted, OpenAI-compatible)
   - OpenRouter (hosted routing layer)
3. Keep keys in env files, never in tracked code.

## Supported Modes

- Native provider keys (Anthropic/OpenAI/Google)
- LiteLLM gateway for broad model coverage
- OpenRouter for hosted multi-model routing
- Ollama for local/offline models

## Operational Policy

- Set primary + fallback model path
- Use cheaper models for routine tasks
- Use stronger models for complex theology/coding tasks
- Require approvals for sensitive pastoral actions

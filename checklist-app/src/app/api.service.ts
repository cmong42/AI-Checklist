import { Injectable } from '@angular/core';

const API_BASE = 'https://ai-checklist-two.vercel.app';

@Injectable({ providedIn: 'root' })
export class ApiService {
  async getSkill(): Promise<string> {
    const resp = await fetch(`${API_BASE}/api/skill`);
    if (!resp.ok) {
      throw new Error(`Failed to load SKILL.md (HTTP ${resp.status})`);
    }
    return resp.text();
  }

  async runAgent(prompt: string, maxTokens: number): Promise<Record<string, unknown>> {
    const resp = await fetch(`${API_BASE}/api/low-level-coding-agent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, max_tokens: maxTokens }),
    });
    const text = await resp.text();
    try {
      return JSON.parse(text);
    } catch {
      return { error: `Server returned non-JSON (HTTP ${resp.status}): ${text.slice(0, 200)}` };
    }
  }
}

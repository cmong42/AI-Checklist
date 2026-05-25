import { Component, signal, computed, HostListener } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface Item {
  id: number;
  title: string;
  completed: boolean;
  steps?: string[];
}

interface AgentResult {
  agent: string;
  result: string;
  error?: string;
  steps?: string[];
}

@Component({
  selector: 'app-root',
  imports: [FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  items = signal<Item[]>([
    { id: 1, title: 'Example task', completed: false },
  ]);
  newItem = signal('');
  showCompleted = signal(false);
  editingId = signal<number | null>(null);
  editText = signal('');
  menuId = signal<number | null>(null);
  expandedSteps = signal<Set<number>>(new Set());
  private nextId = 2;

  aiResults = signal<AgentResult[]>([]);
  aiLoading = signal(false);
  aiTask = signal('');
  aiItemId = signal<number | null>(null);

  @HostListener('document:click')
  closeMenu() {
    this.menuId.set(null);
  }

  activeItems = computed(() => this.items().filter(i => !i.completed));
  completedItems = computed(() => this.items().filter(i => i.completed));

  addItem() {
    const title = this.newItem().trim();
    if (!title) return;
    this.items.update(items => [
      ...items,
      { id: this.nextId++, title, completed: false },
    ]);
    this.newItem.set('');
  }

  toggleItem(id: number) {
    this.items.update(items =>
      items.map(i => i.id === id ? { ...i, completed: !i.completed } : i)
    );
  }

  startEdit(item: Item) {
    this.editingId.set(item.id);
    this.editText.set(item.title);
  }

  saveEdit() {
    const id = this.editingId();
    const title = this.editText().trim();
    if (id !== null && title) {
      this.items.update(items =>
        items.map(i => i.id === id ? { ...i, title } : i)
      );
    }
    this.editingId.set(null);
  }

  cancelEdit() {
    this.editingId.set(null);
  }

  toggleSteps(id: number) {
    this.expandedSteps.update(s => {
      const next = new Set(s);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  removeItem(id: number) {
    this.items.update(items => items.filter(i => i.id !== id));
  }

  closeAiPanel() {
    this.aiResults.set([]);
    this.aiLoading.set(false);
    this.aiTask.set('');
    this.aiItemId.set(null);
  }

  private parseSteps(result: string): string[] | undefined {
    try {
      const parsed = JSON.parse(result);
      const steps = parsed['steps'];
      if (Array.isArray(steps) && steps.length > 0) {
        return steps.map(s => typeof s === 'string' ? s : JSON.stringify(s));
      }
    } catch {}
    return undefined;
  }

  private async parseJsonSafe(r: Response): Promise<Record<string, unknown>> {
    const text = await r.text();
    try {
      return JSON.parse(text);
    } catch {
      return { error: `Server returned non-JSON (HTTP ${r.status}): ${text.slice(0, 200)}` };
    }
  }

  saveAiSteps() {
    const id = this.aiItemId();
    const steps = this.aiResults()[0]?.steps;
    if (id === null || !steps || steps.length === 0) return;
    this.items.update(items =>
      items.map(i => i.id === id ? { ...i, steps } : i)
    );
    this.closeAiPanel();
  }

  async aiAssistant(item: Item) {
    this.aiTask.set(item.title);
    this.aiItemId.set(item.id);
    this.aiLoading.set(true);
    this.aiResults.set([]);

    try {
      const skillResp = await fetch('/api/skill');
      if (!skillResp.ok) {
        throw new Error(`Failed to load SKILL.md (HTTP ${skillResp.status})`);
      }
      const skillText = await skillResp.text();
      const prompt = skillText.replace('<INSERT_TASK_HERE>', item.title);

      const llResp = await fetch('/api/low-level-coding-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, max_tokens: 512 }),
      });
      const llData = await this.parseJsonSafe(llResp);
      const llResult = (llData['result'] as string) ?? (llData['error'] as string) ?? '';
      const steps = this.parseSteps(llResult);

      this.aiResults.set([
        { agent: 'Low-Level Coding Agent', result: llResult, error: llData['error'] as string | undefined, steps },
      ]);
    } catch (e: unknown) {
      this.aiResults.set([
        { agent: 'Error', result: '', error: e instanceof Error ? e.message : 'Failed to load SKILL.md' },
      ]);
    } finally {
      this.aiLoading.set(false);
    }
  }
}

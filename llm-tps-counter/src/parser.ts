import * as fs from "fs";
import * as path from "path";
import { createInterface } from "readline";

const CLAUDE_DIR = path.join(process.env.HOME!, ".claude");
const PROJECTS_DIR = path.join(CLAUDE_DIR, "projects");

// ---- 类型定义 ----

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

interface JsonlEntry extends AnyRecord {
  type: string;
  subtype?: string;
  timestamp: string;
  uuid: string;
  sessionId: string;
  isMeta?: boolean;
}

export interface SessionInfo {
  sessionId: string;
  filePath: string;
  projectPath: string;
  model: string;
  startTime: string;
  endTime: string;
  messageCount: number;
  totalOutputTokens: number;
  title: string;
  summary: string[];
  toolsUsed: string[];
}

export interface ApiCallTps {
  index: number;
  model: string;
  outputTokens: number;
  generationMs: number;
  tps: number;
  timestamp: string;
  /** true = 前一条是 user 消息，测量准确；false = 前一条是 assistant(含工具执行时间) */
  accurate: boolean;
  stopReason: string;
}

export interface SessionTpsResult {
  sessionId: string;
  projectPath: string;
  title: string;
  calls: ApiCallTps[];
  totalOutputTokens: number;
  // 仅基于准确测量
  avgTps: number;
  maxTps: number;
  minTps: number;
  accurateCount: number;
}

// ---- 解码项目路径 ----

function decodeProjectPath(encoded: string): string {
  return encoded.replace(/^-/, "/").replace(/-/g, "/");
}

// ---- 提取用户消息文本 ----

function extractUserText(entry: JsonlEntry): string {
  const raw = entry.message?.content;
  if (!raw) return "";
  const text =
    typeof raw === "string"
      ? raw
      : Array.isArray(raw)
        ? (raw.find((b: { type: string }) => b.type === "text")?.text ?? "")
        : "";
  return text
    .replace(/<command-message>[\s\S]*?<\/command-message>/g, "")
    .replace(/<system-reminder>[\s\S]*?<\/system-reminder>/g, "")
    .replace(/<local-command-stdout>[\s\S]*?<\/local-command-stdout>/g, "")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

// ---- 扫描所有 session ----

export async function listSessions(): Promise<SessionInfo[]> {
  const sessions: SessionInfo[] = [];

  if (!fs.existsSync(PROJECTS_DIR)) return sessions;

  const projects = await fs.promises.readdir(PROJECTS_DIR);

  for (const project of projects) {
    const projectDir = path.join(PROJECTS_DIR, project);
    const stat = fs.statSync(projectDir);
    if (!stat.isDirectory()) continue;

    const files = await fs.promises.readdir(projectDir);
    const jsonlFiles = files.filter((f) => f.endsWith(".jsonl"));

    for (const file of jsonlFiles) {
      const filePath = path.join(projectDir, file);
      const sessionId = file.replace(".jsonl", "");
      try {
        const info = await parseSessionInfo(filePath, sessionId, project);
        if (info) sessions.push(info);
      } catch {
        // 跳过损坏的文件
      }
    }
  }

  sessions.sort(
    (a, b) =>
      new Date(b.startTime).getTime() - new Date(a.startTime).getTime()
  );

  return sessions;
}

// ---- 解析 session 概要信息 ----

async function parseSessionInfo(
  filePath: string,
  sessionId: string,
  encodedProject: string
): Promise<SessionInfo | null> {
  let startTime = "";
  let endTime = "";
  let model = "";
  let messageCount = 0;
  let totalOutputTokens = 0;
  let title = "";
  const summary: string[] = [];
  const toolsUsed = new Set<string>();

  const rl = createInterface({
    input: fs.createReadStream(filePath, "utf-8"),
    crlfDelay: Infinity,
  });

  const seenUuids = new Set<string>();

  for await (const line of rl) {
    if (!line.trim()) continue;

    let entry: JsonlEntry;
    try {
      entry = JSON.parse(line);
    } catch {
      continue;
    }

    const ts = entry.timestamp;
    if (ts) {
      if (!startTime) startTime = ts;
      endTime = ts;
    }

    if (entry.type === "user" && !entry.isMeta) {
      const cleaned = extractUserText(entry);
      if (!cleaned) continue;
      if (!title) {
        title = cleaned.slice(0, 120);
      } else if (summary.length < 3) {
        summary.push(cleaned.slice(0, 100));
      }
    }

    if (
      entry.type === "assistant" &&
      entry.message &&
      !seenUuids.has(entry.uuid)
    ) {
      seenUuids.add(entry.uuid);
      messageCount++;

      const content = entry.message.content;
      if (Array.isArray(content)) {
        for (const block of content) {
          if (block.type === "tool_use" && block.name) {
            toolsUsed.add(block.name);
          }
        }
      }

      if (entry.message.model) model = entry.message.model;
      if (entry.message.usage) {
        totalOutputTokens += entry.message.usage.output_tokens ?? 0;
      }
    }
  }

  if (!startTime) return null;

  return {
    sessionId,
    filePath,
    projectPath: decodeProjectPath(encodedProject),
    model,
    startTime,
    endTime,
    messageCount,
    totalOutputTokens,
    title: title || "无标题",
    summary,
    toolsUsed: [...toolsUsed],
  };
}

// ---- 解析指定 session 的 TPS 数据 ----

export async function getSessionTps(
  sessionId: string
): Promise<SessionTpsResult | null> {
  const filePath = await findSessionFile(sessionId);
  if (!filePath) return null;

  let projectPath = "";
  let lastModel = "";
  let title = "";

  const match = filePath.match(/projects\/([^/]+)\//);
  if (match) projectPath = decodeProjectPath(match[1]);

  // 按顺序收集所有带时间戳的条目
  interface TimestampedEntry {
    type: string;
    timestamp: string;
    uuid: string;
    isMeta?: boolean;
    outputTokens?: number;
    model?: string;
    stopReason?: string;
    hasToolUse?: boolean;
  }

  const entries: TimestampedEntry[] = [];
  const seenUuids = new Set<string>();

  const rl = createInterface({
    input: fs.createReadStream(filePath, "utf-8"),
    crlfDelay: Infinity,
  });

  for await (const line of rl) {
    if (!line.trim()) continue;

    let entry: JsonlEntry;
    try {
      entry = JSON.parse(line);
    } catch {
      continue;
    }

    if (!entry.timestamp) continue;

    // 提取标题
    if (entry.type === "user" && !entry.isMeta && !title) {
      title = extractUserText(entry).slice(0, 120) || title;
    }

    if (entry.type === "user" && !entry.isMeta) {
      entries.push({
        type: "user",
        timestamp: entry.timestamp,
        uuid: entry.uuid,
      });
      continue;
    }

    if (entry.type === "assistant" && entry.message) {
      if (seenUuids.has(entry.uuid)) continue;
      seenUuids.add(entry.uuid);

      const out = entry.message.usage?.output_tokens ?? 0;
      const content = entry.message.content;
      let hasToolUse = false;
      if (Array.isArray(content)) {
        hasToolUse = content.some(
          (b: { type: string }) => b.type === "tool_use"
        );
      }

      if (entry.message.model) lastModel = entry.message.model;

      entries.push({
        type: "assistant",
        timestamp: entry.timestamp,
        uuid: entry.uuid,
        outputTokens: out,
        model: entry.message.model,
        stopReason: entry.message.stop_reason,
        hasToolUse,
      });
    }
  }

  // 逐条计算 TPS
  const calls: ApiCallTps[] = [];
  let totalOutputTokens = 0;

  for (let i = 0; i < entries.length; i++) {
    const e = entries[i];
    if (e.type !== "assistant" || !e.outputTokens || e.outputTokens <= 0)
      continue;

    // 找前一条有意义的条目
    let prevIndex = i - 1;
    while (prevIndex >= 0 && entries[prevIndex].type !== "user" && entries[prevIndex].type !== "assistant") {
      prevIndex--;
    }
    if (prevIndex < 0) continue;

    const prev = entries[prevIndex];
    const endMs = new Date(e.timestamp).getTime();
    const startMs = new Date(prev.timestamp).getTime();
    const gapMs = endMs - startMs;

    if (gapMs < 500) continue; // 低于 500ms 的测量不可靠，跳过

    // 判断精度：前一条是 user → 准确；前一条是 assistant → 含工具执行时间
    const accurate = prev.type === "user";

    const tps = e.outputTokens / (gapMs / 1000);

    calls.push({
      index: calls.length + 1,
      model: e.model || lastModel,
      outputTokens: e.outputTokens,
      generationMs: gapMs,
      tps: Math.round(tps * 100) / 100,
      timestamp: e.timestamp,
      accurate,
      stopReason: e.stopReason || "",
    });

    totalOutputTokens += e.outputTokens;
  }

  // 统计只基于准确测量
  const accurateTps = calls.filter((c) => c.accurate).map((c) => c.tps);

  return {
    sessionId,
    projectPath,
    title: title || "无标题",
    calls,
    totalOutputTokens,
    avgTps:
      accurateTps.length > 0
        ? Math.round(
            (accurateTps.reduce((a, b) => a + b, 0) / accurateTps.length) * 100
          ) / 100
        : -1,
    maxTps:
      accurateTps.length > 0 ? Math.round(Math.max(...accurateTps) * 100) / 100 : -1,
    minTps:
      accurateTps.length > 0 ? Math.round(Math.min(...accurateTps) * 100) / 100 : -1,
    accurateCount: accurateTps.length,
  };
}

// ---- 查找 session 文件路径 ----

async function findSessionFile(sessionId: string): Promise<string | null> {
  const projects = await fs.promises.readdir(PROJECTS_DIR);

  for (const project of projects) {
    const candidate = path.join(PROJECTS_DIR, project, `${sessionId}.jsonl`);
    try {
      await fs.promises.access(candidate);
      return candidate;
    } catch {
      // 文件不在此目录
    }
  }

  return null;
}

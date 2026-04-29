import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { listSessions, getSessionTps } from "./parser.js";

const server = new McpServer({
  name: "llm-tps-counter",
  version: "0.2.0",
});

// ---- 列出所有 session ----

server.tool(
  "list_sessions",
  "列出所有 Claude Code 会话，返回会话 ID、标题、模型、时间、消息数、token 用量等概要信息",
  {},
  async () => {
    const sessions = await listSessions();

    if (sessions.length === 0) {
      return {
        content: [{ type: "text", text: "未找到任何 Claude Code 会话。" }],
      };
    }

    const lines = sessions.map((s, i) => {
      const start = new Date(s.startTime).toLocaleString("zh-CN");
      const tokens = `${(s.totalOutputTokens / 1000).toFixed(1)}k`;
      const tools =
        s.toolsUsed.length > 0
          ? s.toolsUsed.slice(0, 5).join(", ") +
            (s.toolsUsed.length > 5 ? ` 等${s.toolsUsed.length}个` : "")
          : "";
      const parts = [
        `## ${i + 1}. ${s.title}`,
        `   ID: ${s.sessionId.slice(0, 8)}... | 项目: ${s.projectPath}`,
        `   模型: ${s.model || "未知"} | ${start}`,
        `   消息: ${s.messageCount} | 输出: ${tokens} tokens`,
      ];
      if (tools) parts.push(`   工具: ${tools}`);
      if (s.summary.length > 0) {
        parts.push(`   后续: ${s.summary[0]}`);
      }
      return parts.join("\n");
    });

    return {
      content: [
        {
          type: "text",
          text: `共 ${sessions.length} 个会话\n\n${lines.join("\n\n")}`,
        },
      ],
    };
  }
);

// ---- 查看指定 session 的 TPS 数据 ----

server.tool(
  "session_tps",
  "查看指定 Claude Code 会话中每轮对话的 TPS（tokens per second）数据",
  {
    session_id: z
      .string()
      .describe(
        "会话 ID（可以是完整 UUID 或前几位，从 list_sessions 获取）"
      ),
  },
  async ({ session_id }) => {
    // 支持前缀匹配
    let sid = session_id;
    let sessionTitle = "";
    if (session_id.length < 36) {
      const sessions = await listSessions();
      const matched = sessions.find((s) =>
        s.sessionId.startsWith(session_id)
      );
      if (!matched) {
        return {
          content: [
            {
              type: "text",
              text: `未找到以 "${session_id}" 开头的会话。请先使用 list_sessions 查看所有会话。`,
            },
          ],
        };
      }
      sid = matched.sessionId;
      sessionTitle = matched.title;
    }

    const result = await getSessionTps(sid);

    if (!result) {
      return {
        content: [
          { type: "text", text: `未找到会话 ${sid} 的数据。` },
        ],
      };
    }

    if (result.calls.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `会话 ${sid.slice(0, 8)}... 没有 TPS 数据。`,
          },
        ],
      };
    }

    // 表格输出
    const header =
      "| # | 模型 | 输出 tokens | 生成耗时 | TPS | 精度 |";
    const separator =
      "|---|------|------------|---------|-----|------|";
    const rows = result.calls.map((c) => {
      const duration = (c.generationMs / 1000).toFixed(1) + "s";
      const accuracy = c.accurate ? "准确" : "含工具耗时";
      return `| ${c.index} | ${c.model} | ${c.outputTokens} | ${duration} | ${c.tps.toFixed(2)} | ${accuracy} |`;
    });

    // 统计摘要（仅基于准确测量）
    const accurateCalls = result.calls.filter((c) => c.accurate);
    const estimatedCalls = result.calls.filter((c) => !c.accurate);

    const summaryLines = [
      `\n### TPS 统计`,
      `- 标题: ${result.title}`,
      `- 会话: ${result.sessionId.slice(0, 8)}... (${result.projectPath})`,
      `- 模型: ${result.calls[0]?.model}`,
      `- API 调用: ${result.calls.length} 次（准确 ${accurateCalls.length}，含工具耗时 ${estimatedCalls.length}）`,
      `- 总输出: ${result.totalOutputTokens.toLocaleString()} tokens`,
    ];

    if (result.accurateCount > 0) {
      summaryLines.push(
        ``,
        `**仅准确测量（${result.accurateCount} 次）：**`,
        `- 平均 TPS: ${result.avgTps}`,
        `- 最高 TPS: ${result.maxTps}`,
        `- 最低 TPS: ${result.minTps}`
      );
    }

    if (estimatedCalls.length > 0) {
      const estTps = estimatedCalls.map((c) => c.tps);
      const estAvg =
        Math.round(
          (estTps.reduce((a, b) => a + b, 0) / estTps.length) * 100
        ) / 100;
      summaryLines.push(
        ``,
        `**含工具耗时的测量（${estimatedCalls.length} 次，TPS 偏低）：**`,
        `- 平均 TPS: ${estAvg}（仅供参考，实际 AI 速度更高）`
      );
    }

    return {
      content: [
        {
          type: "text",
          text: `${header}\n${separator}\n${rows.join("\n")}\n${summaryLines.join("\n")}`,
        },
      ],
    };
  }
);

// ---- 启动 ----

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);

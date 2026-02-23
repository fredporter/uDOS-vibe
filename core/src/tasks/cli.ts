#!/usr/bin/env node
import {
  indexTasksWithStats,
  queryTaskCatalog,
  searchTasks,
} from "./indexer.js";
import { resolveTaskCliDefaults } from "../runtime/utils/paths.js";
import { writeJsonReport } from "../runtime/utils/reports.js";
import { jobId, nowIso } from "../runtime/utils/time.js";

function resolveDefaults() {
  return resolveTaskCliDefaults();
}

function parseArgs(args: string[]) {
  const parsed: any = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--vault" && args[i + 1]) {
      parsed.vaultRoot = args[++i];
    } else if (arg === "--db" && args[i + 1]) {
      parsed.dbPath = args[++i];
    } else if (arg === "--mission" && args[i + 1]) {
      parsed.missionId = args[++i];
    } else if (arg === "--runs" && args[i + 1]) {
      parsed.runsRoot = args[++i];
    } else if (arg === "--summary") {
      parsed.summary = true;
    } else if (arg === "--search") {
      parsed.search = true;
    } else if (arg === "--status" && args[i + 1]) {
      parsed.status = args[++i];
    } else if (arg === "--due" && args[i + 1]) {
      parsed.due = args[++i];
    } else if (arg === "--priority" && args[i + 1]) {
      parsed.priority = Number(args[++i]);
    } else if (arg === "--tag" && args[i + 1]) {
      parsed.tag = args[++i];
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  return parsed;
}

function printHelp() {
  console.log(`Index tasks from vault Markdown files into SQLite.

Usage:
  node tasks/cli.js [--vault PATH] [--db PATH] [--mission ID] [--runs PATH] [--summary] [--search]

Search filters:
  --status open|done
  --due YYYY-MM-DD
  --priority -2|0|2
  --tag tagname

Environment:
  VAULT_ROOT      Vault folder (default ../../memory/vault)
  DB_PATH         SQLite database (default ../../memory/vault/.udos/state.db)
  MISSION_ID      Mission id used for run reports (default task-indexer)
  RUNS_ROOT       Run report root (default ../../memory/vault/06_RUNS)
`);
}

async function main() {
  const defaults = resolveDefaults();
  const parsed = parseArgs(process.argv.slice(2));
  const options = { ...defaults, ...parsed };

  console.log(`Indexing tasks from: ${options.vaultRoot}`);
  console.log(`Writing to: ${options.dbPath}`);

  try {
    const startedAt = nowIso();
    const runJobId = jobId("job");
    const missionId = options.missionId ?? "task-indexer";

    const stats = await indexTasksWithStats(options);
    console.log(`✅ Indexed ${stats.total_indexed} tasks`);

    if (options.summary) {
      const summary = queryTaskCatalog(options.dbPath);
      console.log(JSON.stringify({ summary }, null, 2));
    }

    if (options.search) {
      const results = searchTasks(options.dbPath, {
        status: options.status,
        due: options.due,
        priority: Number.isFinite(options.priority)
          ? options.priority
          : undefined,
        tag: options.tag,
      });
      console.log(JSON.stringify({ results }, null, 2));
    }

    const completedAt = nowIso();
    const report = {
      mission_id: missionId,
      job_id: runJobId,
      runner: "task-indexer-cli",
      status: "completed",
      started_at: startedAt,
      completed_at: completedAt,
      vault_root: options.vaultRoot,
      db_path: options.dbPath,
      stats,
    };

    const reportPath = await writeJsonReport(options.runsRoot, missionId, runJobId, report);
    const payload = {
      ...report,
      report_path: reportPath,
    };
    console.log(JSON.stringify(payload));
  } catch (error) {
    const completedAt = nowIso();
    const missionId = options.missionId ?? "task-indexer";
    const runJobId = jobId("job");
    const report = {
      mission_id: missionId,
      job_id: runJobId,
      runner: "task-indexer-cli",
      status: "failed",
      started_at: completedAt,
      completed_at: completedAt,
      vault_root: options.vaultRoot,
      db_path: options.dbPath,
      error: String(error),
    };
    try {
      const reportPath = await writeJsonReport(options.runsRoot, missionId, runJobId, report);
      console.error(`Report written to ${reportPath}`);
    } catch (reportError) {
      console.error("Failed to write mission report:", reportError);
    }
    console.error("Task indexing failed:", error);
    process.exit(1);
  }
}

main();

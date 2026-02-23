import { promises as fs } from "node:fs";
import path from "node:path";

export async function writeJsonReport(
  runsRoot: string,
  missionId: string,
  jobId: string,
  payload: Record<string, unknown>,
): Promise<string> {
  const runDir = path.join(runsRoot, missionId);
  await fs.mkdir(runDir, { recursive: true });
  const reportPath = path.join(runDir, `${jobId}.json`);
  await fs.writeFile(reportPath, JSON.stringify(payload, null, 2), "utf-8");
  return reportPath;
}


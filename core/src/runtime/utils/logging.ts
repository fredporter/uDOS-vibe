export type LogLevel = "INFO" | "WARN" | "ERROR" | "DEBUG";
export type Logger = (level: LogLevel, msg: string) => void;

export function createDefaultLogger(): Logger {
  return (level, msg) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${level}] ${msg}`);
  };
}


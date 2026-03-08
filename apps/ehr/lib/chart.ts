type JsonValue = string | string[] | Record<string, string>;

export function parseJsonValue<T extends JsonValue>(value: string): T {
  return JSON.parse(value) as T;
}

export function formatDateTime(value: Date) {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(value);
}

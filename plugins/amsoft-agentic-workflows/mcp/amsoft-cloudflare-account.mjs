#!/usr/bin/env node

import readline from "node:readline";
import { execFileSync } from "node:child_process";

const SERVER_INFO = {
  name: "amsoft-cloudflare-account",
  version: "0.1.0",
};
const DEFAULT_API_BASE = "https://api.cloudflare.com/client/v4";
const MAX_RESPONSE_BYTES = 1_000_000;
const SECRET_KEYS = new Set([
  "authorization",
  "apikey",
  "apitoken",
  "accesstoken",
  "refreshtoken",
  "token",
  "secret",
  "clientsecret",
  "password",
  "privatekey",
  "secretaccesskey",
]);

const tools = [
  {
    name: "amsoft_cloudflare_verify_token",
    title: "Verify Cloudflare account API token",
    description:
      "Verify the configured Cloudflare account API token for the configured account. Never accepts or returns the token.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true },
  },
  {
    name: "amsoft_cloudflare_get_account",
    title: "Get configured Cloudflare account",
    description:
      "Read the configured Cloudflare account. Uses CLOUDFLARE_ACCOUNT_ID and never accepts an arbitrary account ID.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true },
  },
  {
    name: "amsoft_cloudflare_list_zones",
    title: "List Cloudflare zones",
    description:
      "List zones belonging to the configured Cloudflare account, optionally filtered by name.",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string", description: "Optional zone-name filter." },
        page: { type: "integer", minimum: 1, default: 1 },
        per_page: { type: "integer", minimum: 1, maximum: 50, default: 20 },
      },
      additionalProperties: false,
    },
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true },
  },
  {
    name: "amsoft_cloudflare_api_read",
    title: "Read from the Cloudflare v4 API",
    description:
      "Perform an authenticated GET against a relative Cloudflare v4 API path. Use current Cloudflare docs to choose the path and query.",
    inputSchema: {
      type: "object",
      required: ["path"],
      properties: {
        path: {
          type: "string",
          description:
            "Path relative to /client/v4, beginning with /. Do not include a URL, query string, or fragment.",
        },
        query: {
          type: "object",
          description: "Optional query parameters. Array values become repeated parameters.",
          additionalProperties: {
            anyOf: [
              { type: "string" },
              { type: "number" },
              { type: "boolean" },
              {
                type: "array",
                items: {
                  anyOf: [{ type: "string" }, { type: "number" }, { type: "boolean" }],
                },
              },
            ],
          },
        },
      },
      additionalProperties: false,
    },
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true },
  },
  {
    name: "amsoft_cloudflare_api_write",
    title: "Change Cloudflare through the v4 API",
    description:
      "Perform an authenticated POST, PUT, PATCH, or DELETE against a relative Cloudflare v4 API path. Requires explicit user approval before confirmed may be true.",
    inputSchema: {
      type: "object",
      required: ["method", "path", "confirmed"],
      properties: {
        method: { type: "string", enum: ["POST", "PUT", "PATCH", "DELETE"] },
        path: {
          type: "string",
          description:
            "Path relative to /client/v4, beginning with /. Do not include a URL, query string, or fragment.",
        },
        query: {
          type: "object",
          additionalProperties: {
            anyOf: [
              { type: "string" },
              { type: "number" },
              { type: "boolean" },
              {
                type: "array",
                items: {
                  anyOf: [{ type: "string" }, { type: "number" }, { type: "boolean" }],
                },
              },
            ],
          },
        },
        body: {
          description: "JSON request body. Omit it when the endpoint has no body.",
        },
        confirmed: {
          type: "boolean",
          description:
            "Set true only after the user explicitly approved this exact change in the current conversation.",
        },
      },
      additionalProperties: false,
    },
    annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: false },
  },
];

function textResult(value, isError = false) {
  return {
    content: [
      {
        type: "text",
        text: typeof value === "string" ? value : JSON.stringify(value, null, 2),
      },
    ],
    ...(isError ? { isError: true } : {}),
  };
}

function keychainValue(service, account) {
  if (process.platform !== "darwin") return undefined;
  try {
    return execFileSync(
      "/usr/bin/security",
      ["find-generic-password", "-s", service, "-a", account, "-w"],
      { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }
    ).trim();
  } catch {
    return undefined;
  }
}

function requireConfig() {
  const accountId =
    process.env.CLOUDFLARE_ACCOUNT_ID?.trim() ||
    keychainValue("codex-cloudflare-account-id", "default");
  const token =
    process.env.CLOUDFLARE_API_TOKEN?.trim() ||
    (accountId ? keychainValue("codex-cloudflare-account", accountId) : undefined);
  if (!token) {
    throw new Error(
      "No Cloudflare token is configured. Set CLOUDFLARE_API_TOKEN or use the bundled macOS Keychain setup script; never pass the token as a tool argument."
    );
  }
  if (!accountId) {
    throw new Error(
      "No Cloudflare account ID is configured. Set CLOUDFLARE_ACCOUNT_ID or use the bundled macOS Keychain setup script."
    );
  }
  if (!/^[a-f0-9]{32}$/i.test(accountId)) {
    throw new Error("CLOUDFLARE_ACCOUNT_ID must be a 32-character Cloudflare account identifier.");
  }
  return { token, accountId };
}

function validatePath(path) {
  if (typeof path !== "string" || !path.startsWith("/")) {
    throw new Error("API path must be a string beginning with /.");
  }
  if (
    path.includes("://") ||
    path.includes("?") ||
    path.includes("#") ||
    path.includes("\\") ||
    path.split("/").includes("..") ||
    /[\u0000-\u001f\u007f]/.test(path)
  ) {
    throw new Error(
      "API path must be a clean relative path without a URL, query, fragment, traversal, or control characters."
    );
  }
  return path.replace(/\/{2,}/g, "/");
}

function appendQuery(url, query = {}) {
  if (query === null || Array.isArray(query) || typeof query !== "object") {
    throw new Error("query must be an object.");
  }
  for (const [key, rawValue] of Object.entries(query)) {
    if (!key || /[\u0000-\u001f\u007f]/.test(key)) {
      throw new Error("Invalid query parameter name.");
    }
    const values = Array.isArray(rawValue) ? rawValue : [rawValue];
    for (const value of values) {
      if (!["string", "number", "boolean"].includes(typeof value)) {
        throw new Error(
          `Query parameter ${key} must contain only strings, numbers, or booleans.`
        );
      }
      url.searchParams.append(key, String(value));
    }
  }
}

function redact(value, key = "", redactValueFields = false) {
  const normalizedKey = key.toLowerCase().replace(/[^a-z0-9]/g, "");
  if (SECRET_KEYS.has(normalizedKey) || (redactValueFields && normalizedKey === "value")) {
    return "[REDACTED]";
  }
  if (Array.isArray(value)) {
    return value.map((entry) => redact(entry, "", redactValueFields));
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([childKey, child]) => [
        childKey,
        redact(child, childKey, redactValueFields),
      ])
    );
  }
  return value;
}

async function cloudflareRequest(method, path, query, body) {
  const { token } = requireConfig();
  const cleanPath = validatePath(path);
  const url = new URL(`${DEFAULT_API_BASE}${cleanPath}`);
  appendQuery(url, query);

  const headers = {
    Accept: "application/json",
    Authorization: `Bearer ${token}`,
    "User-Agent": `${SERVER_INFO.name}/${SERVER_INFO.version}`,
  };
  const options = { method, headers, signal: AbortSignal.timeout(110_000) };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);
  const raw = await response.text();
  if (Buffer.byteLength(raw) > MAX_RESPONSE_BYTES) {
    throw new Error(
      `Cloudflare response exceeded ${MAX_RESPONSE_BYTES} bytes. Narrow the query or request fewer results.`
    );
  }

  let payload;
  try {
    payload = raw ? JSON.parse(raw) : null;
  } catch {
    payload = { raw_response: raw };
  }

  const result = {
    request: {
      method,
      path: validatePath(path),
      query: Object.fromEntries(url.searchParams),
    },
    response: {
      status: response.status,
      ok: response.ok,
      cf_ray: response.headers.get("cf-ray"),
      data: redact(
        payload,
        "",
        /\/(?:tokens|secrets|service_tokens)(?:\/|$)/.test(cleanPath)
      ),
    },
  };

  if (!response.ok || (payload && payload.success === false)) {
    const error = new Error(`Cloudflare API request failed with HTTP ${response.status}.`);
    error.details = result;
    throw error;
  }
  return result;
}

async function callTool(name, args = {}) {
  const { accountId } = requireConfig();
  switch (name) {
    case "amsoft_cloudflare_verify_token":
      return cloudflareRequest("GET", `/accounts/${accountId}/tokens/verify`);
    case "amsoft_cloudflare_get_account":
      return cloudflareRequest("GET", `/accounts/${accountId}`);
    case "amsoft_cloudflare_list_zones":
      return cloudflareRequest("GET", "/zones", {
        "account.id": accountId,
        ...(args.name ? { name: args.name } : {}),
        page: args.page ?? 1,
        per_page: args.per_page ?? 20,
      });
    case "amsoft_cloudflare_api_read":
      return cloudflareRequest("GET", args.path, args.query);
    case "amsoft_cloudflare_api_write":
      if (args.confirmed !== true) {
        throw new Error(
          "Write blocked: confirmed must be true only after the user explicitly approves this exact Cloudflare change."
        );
      }
      if (!["POST", "PUT", "PATCH", "DELETE"].includes(args.method)) {
        throw new Error("Write method must be POST, PUT, PATCH, or DELETE.");
      }
      return cloudflareRequest(args.method, args.path, args.query, args.body);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

function send(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

function success(id, result) {
  send({ jsonrpc: "2.0", id, result });
}

function failure(id, code, message, data) {
  send({
    jsonrpc: "2.0",
    id,
    error: { code, message, ...(data === undefined ? {} : { data }) },
  });
}

async function handle(message) {
  if (!message || message.jsonrpc !== "2.0" || typeof message.method !== "string") {
    if (message?.id !== undefined) failure(message.id, -32600, "Invalid Request");
    return;
  }

  if (
    message.method === "notifications/initialized" ||
    message.method === "notifications/cancelled"
  ) {
    return;
  }

  try {
    switch (message.method) {
      case "initialize":
        success(message.id, {
          protocolVersion: "2025-06-18",
          capabilities: { tools: { listChanged: false } },
          serverInfo: SERVER_INFO,
        });
        break;
      case "ping":
        success(message.id, {});
        break;
      case "tools/list":
        success(message.id, { tools });
        break;
      case "tools/call": {
        const name = message.params?.name;
        const args = message.params?.arguments ?? {};
        if (
          typeof name !== "string" ||
          !args ||
          Array.isArray(args) ||
          typeof args !== "object"
        ) {
          failure(message.id, -32602, "Invalid tool call parameters");
          break;
        }
        try {
          success(message.id, textResult(await callTool(name, args)));
        } catch (error) {
          success(message.id, textResult(error.details ?? { error: error.message }, true));
        }
        break;
      }
      default:
        if (message.id !== undefined) failure(message.id, -32601, "Method not found");
    }
  } catch (error) {
    if (message.id !== undefined) {
      failure(message.id, -32603, "Internal error", { message: error.message });
    }
  }
}

const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
input.on("line", (line) => {
  if (!line.trim()) return;
  let message;
  try {
    message = JSON.parse(line);
  } catch {
    failure(null, -32700, "Parse error");
    return;
  }
  void handle(message);
});

process.on("uncaughtException", (error) => {
  console.error(`amsoft-cloudflare-account MCP fatal error: ${error.message}`);
  process.exitCode = 1;
});

process.on("unhandledRejection", (error) => {
  console.error(`amsoft-cloudflare-account MCP unhandled rejection: ${error?.message ?? error}`);
  process.exitCode = 1;
});

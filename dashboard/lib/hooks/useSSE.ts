"use client";

import { useEffect, useRef, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";

interface SSEEvent {
  type: string;
  [key: string]: unknown;
}

const RECONNECT_DELAY = 3000;
const INVALIDATION_MAP: Record<string, string[]> = {
  "account.created": ["accounts", "stats"],
  "account.deleted": ["accounts", "stats"],
  "bot.created": ["bots", "stats"],
  "bot.deleted": ["bots", "stats"],
  "bot.status_change": ["bots", "stats"],
  "license.redeemed": ["licenses", "stats"],
  "license.generated": ["licenses", "stats"],
  "email.received": ["emails"],
};

export function useSSE() {
  const qc = useQueryClient();
  const esRef = useRef<EventSource | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    // Get token from localStorage
    const token = localStorage.getItem("access_token");
    if (!token) return;

    // Close existing connection
    if (esRef.current) {
      esRef.current.close();
    }

    const es = new EventSource(`/api/v1/events?token=${token}`);
    esRef.current = es;

    es.onmessage = (event) => {
      try {
        const data: SSEEvent = JSON.parse(event.data);
        if (data.type === "ping" || data.type === "connected") return;

        // Invalidate relevant query caches
        const queryKeys = INVALIDATION_MAP[data.type];
        if (queryKeys) {
          for (const key of queryKeys) {
            qc.invalidateQueries({ queryKey: [key] });
          }
        }
      } catch {
        // Ignore parse errors
      }
    };

    es.onerror = () => {
      es.close();
      // Reconnect after delay
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY);
    };
  }, [qc]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
      if (esRef.current) {
        esRef.current.close();
      }
    };
  }, [connect]);
}

/**
 * WebSocket Service
 * Handles real-time communication with the backend for simulation updates
 */

import { io, Socket } from 'socket.io-client';
import type { WebSocketMessage } from '@types/models';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

export class SimulationWebSocket {
  private socket: Socket | null = null;
  private simulationId: string;
  private callbacks: {
    onConnected?: () => void;
    onStatus?: (data: any) => void;
    onMetrics?: (data: any) => void;
    onCompleted?: (results: any) => void;
    onError?: (error: string) => void;
  } = {};

  constructor(simulationId: string) {
    this.simulationId = simulationId;
  }

  /**
   * Connect to WebSocket for simulation updates
   */
  connect(): void {
    if (this.socket?.connected) {
      console.warn('WebSocket already connected');
      return;
    }

    // Create socket connection
    this.socket = io(`${WS_URL}/simulations`, {
      path: `/ws/${this.simulationId}`,
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    // Set up event listeners
    this.socket.on('connect', () => {
      console.log(`WebSocket connected for simulation ${this.simulationId}`);
      this.callbacks.onConnected?.();
    });

    this.socket.on('message', (message: WebSocketMessage) => {
      this.handleMessage(message);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.callbacks.onError?.('Connection error: ' + error.message);
    });
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'connected':
        console.log('WebSocket handshake complete');
        this.callbacks.onConnected?.();
        break;

      case 'status':
        this.callbacks.onStatus?.({
          status: message.status,
          progress: message.progress || 0,
          message: message.message || '',
        });
        break;

      case 'metrics':
        this.callbacks.onMetrics?.(message.data);
        break;

      case 'completed':
        this.callbacks.onCompleted?.(message.results);
        this.disconnect();
        break;

      case 'error':
        this.callbacks.onError?.(message.message || 'Unknown error');
        this.disconnect();
        break;

      default:
        console.warn('Unknown message type:', message.type);
    }
  }

  /**
   * Register callback for connection event
   */
  onConnected(callback: () => void): void {
    this.callbacks.onConnected = callback;
  }

  /**
   * Register callback for status updates
   */
  onStatus(callback: (data: any) => void): void {
    this.callbacks.onStatus = callback;
  }

  /**
   * Register callback for metrics updates
   */
  onMetrics(callback: (data: any) => void): void {
    this.callbacks.onMetrics = callback;
  }

  /**
   * Register callback for completion
   */
  onCompleted(callback: (results: any) => void): void {
    this.callbacks.onCompleted = callback;
  }

  /**
   * Register callback for errors
   */
  onError(callback: (error: string) => void): void {
    this.callbacks.onError = callback;
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

/**
 * Create a new WebSocket connection for a simulation
 */
export const createSimulationWebSocket = (simulationId: string): SimulationWebSocket => {
  return new SimulationWebSocket(simulationId);
};

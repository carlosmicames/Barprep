import axios from 'axios';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility function to merge Tailwind classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * API Client configuration
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * API endpoints
 */
export const api = {
  // Users
  users: {
    create: (data: any) => apiClient.post('/users/', data),
    get: (userId: number) => apiClient.get(`/users/${userId}`),
    getByEmail: (email: string) => apiClient.get(`/users/email/${email}`),
  },
  
  // MCQ
  mcq: {
    generate: (data: any) => apiClient.post('/mcq/generate', data),
    getBySubject: (subject: string, limit = 20) => 
      apiClient.get(`/mcq/questions/${subject}`, { params: { limit } }),
    submit: (userId: number, data: any) => 
      apiClient.post(`/mcq/submit/${userId}`, data),
    getStats: (userId: number, subject: string) =>
      apiClient.get(`/mcq/stats/${userId}/${subject}`),
  },
  
  // Essays
  essays: {
    submit: (userId: number, data: any) =>
      apiClient.post(`/essays/submit/${userId}`, data),
    getUserEssays: (userId: number, subject?: string) =>
      apiClient.get(`/essays/user/${userId}`, { params: { subject } }),
    get: (essayId: number) => apiClient.get(`/essays/${essayId}`),
  },
  
  // Study Materials
  materials: {
    upload: (userId: number, formData: FormData) =>
      apiClient.post(`/materials/upload/${userId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    getBySubject: (subject: string) =>
      apiClient.get(`/materials/subject/${subject}`),
    getUserMaterials: (userId: number) =>
      apiClient.get(`/materials/user/${userId}`),
    delete: (materialId: number) =>
      apiClient.delete(`/materials/${materialId}`),
  },
  
  // Progress
  progress: {
    getOverview: (userId: number) =>
      apiClient.get(`/progress/user/${userId}`),
    getSubject: (userId: number, subject: string) =>
      apiClient.get(`/progress/user/${userId}/subject/${subject}`),
  },
  
  // Chat
  chat: {
    getRooms: () => apiClient.get('/chat/rooms'),
    getMessages: (roomId: number, limit = 50) =>
      apiClient.get(`/chat/room/${roomId}/messages`, { params: { limit } }),
    sendMessage: (userId: number, data: any) =>
      apiClient.post(`/chat/message/${userId}`, data),
    getRoomBySubject: (subject: string) =>
      apiClient.get(`/chat/room/subject/${subject}`),
  },
  
  // Subjects
  getSubjects: () => apiClient.get('/subjects'),
};

/**
 * Format date helper
 */
export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Format score helper
 */
export function formatScore(score: number): string {
  return score.toFixed(1);
}

/**
 * Get color for score
 */
export function getScoreColor(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 80) return 'text-blue-600';
  if (score >= 70) return 'text-amber-600';
  return 'text-red-600';
}

/**
 * Subject display names
 */
export const SUBJECT_NAMES: Record<string, string> = {
  familia: 'Derecho de Familia',
  sucesiones: 'Sucesiones',
  reales: 'Derechos Reales',
  hipoteca: 'Hipoteca',
  obligaciones: 'Obligaciones & Contratos',
  etica: 'Ética',
  constitucional: 'Derecho Constitucional',
  administrativo: 'Derecho Administrativo',
  danos: 'Daños y Perjuicios',
  penal: 'Derecho Penal',
  proc_penal: 'Procedimiento Penal',
  evidencia: 'Evidencia',
  proc_civil: 'Procedimiento Civil',
};

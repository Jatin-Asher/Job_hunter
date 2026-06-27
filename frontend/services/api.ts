import apiClient from '@/lib/api'
import { ScrapeJobsRequest, ScrapeJobsResponse, User } from '@/types'

export const authService = {
  register: (email: string, username: string, password: string, fullName: string) =>
    apiClient.post('/auth/register', { email, username, password, full_name: fullName }),

  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),

  refreshToken: (refreshToken: string) =>
    apiClient.post('/auth/refresh-token', { refresh_token: refreshToken }),

  getMe: () => apiClient.get<User>('/auth/me'),

  forgotPassword: (email: string) =>
    apiClient.post('/auth/forgot-password', { email }),

  resetPassword: (token: string, newPassword: string) =>
    apiClient.post('/auth/reset-password', { token, new_password: newPassword }),

  changePassword: (oldPassword: string, newPassword: string) =>
    apiClient.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
}

export const userService = {
  getProfile: () => apiClient.get<User>('/users/profile'),

  updateProfile: (data: any) => apiClient.put('/users/profile', data),

  uploadResume: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/users/upload-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  uploadProfilePhoto: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/users/upload-profile-photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  deleteAccount: () => apiClient.delete('/users/account'),
}

export const filterService = {
  create: (data: any) => apiClient.post('/filters/', data),

  list: (skip = 0, limit = 10) =>
    apiClient.get(`/filters/?skip=${skip}&limit=${limit}`),

  get: (id: number) => apiClient.get(`/filters/${id}`),

  update: (id: number, data: any) => apiClient.put(`/filters/${id}`, data),

  delete: (id: number) => apiClient.delete(`/filters/${id}`),
}

export const jobService = {
  scrapeAllPlatforms: (data: ScrapeJobsRequest) =>
    apiClient.post<ScrapeJobsResponse>('/jobs/scrape', data),

  list: (skip = 0, limit = 10, keyword = '', location = '', source = '') =>
    apiClient.get('/jobs/', {
      params: { skip, limit, keyword, location, source },
    }),

  get: (id: number) => apiClient.get(`/jobs/${id}`),

  save: (id: number) => apiClient.post(`/jobs/${id}/save`),

  unsave: (id: number) => apiClient.delete(`/jobs/${id}/save`),

  listSaved: (skip = 0, limit = 10) =>
    apiClient.get('/jobs/saved/list', { params: { skip, limit } }),
}

export const applicationService = {
  create: (jobId: number) =>
    apiClient.post('/applications/', { job_id: jobId }),

  list: (status = '', skip = 0, limit = 10) =>
    apiClient.get('/applications/', {
      params: { status_filter: status, skip, limit },
    }),

  get: (id: number) => apiClient.get(`/applications/${id}`),

  update: (id: number, data: any) =>
    apiClient.put(`/applications/${id}`, data),

  delete: (id: number) => apiClient.delete(`/applications/${id}`),

  getStats: () => apiClient.get('/applications/stats'),
}

export const dashboardService = {
  getStats: () => apiClient.get('/dashboard/stats'),

  listUsers: (skip = 0, limit = 10) =>
    apiClient.get('/dashboard/admin/users', { params: { skip, limit } }),

  listJobs: (skip = 0, limit = 10) =>
    apiClient.get('/dashboard/admin/jobs', { params: { skip, limit } }),

  listScrapingLogs: (skip = 0, limit = 10) =>
    apiClient.get('/dashboard/admin/scraping-logs', {
      params: { skip, limit },
    }),

  getAnalytics: () => apiClient.get('/dashboard/admin/analytics'),
}

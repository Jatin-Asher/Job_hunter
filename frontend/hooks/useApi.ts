import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authService, userService, jobService, applicationService } from '@/services/api'

export const useLogin = () =>
  useMutation({
    mutationFn: (data: { email: string; password: string }) =>
      authService.login(data.email, data.password),
  })

export const useRegister = () =>
  useMutation({
    mutationFn: (data: {
      email: string
      username: string
      password: string
      fullName: string
    }) =>
      authService.register(data.email, data.username, data.password, data.fullName),
  })

export const useMe = () =>
  useQuery({
    queryKey: ['user', 'me'],
    queryFn: () => authService.getMe(),
  })

export const useProfile = () =>
  useQuery({
    queryKey: ['user', 'profile'],
    queryFn: () => userService.getProfile(),
  })

export const useUpdateProfile = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: any) => userService.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] })
    },
  })
}

export const useJobs = (skip = 0, limit = 10, keyword = '', location = '', source = '') =>
  useQuery({
    queryKey: ['jobs', skip, limit, keyword, location, source],
    queryFn: () => jobService.list(skip, limit, keyword, location, source),
  })

export const useScrapeAllPlatformJobs = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { keywords: string[]; locations: string[] }) =>
      jobService.scrapeAllPlatforms(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export const useScrapeLinkedInJobs = useScrapeAllPlatformJobs

export const useJob = (id: number) =>
  useQuery({
    queryKey: ['job', id],
    queryFn: () => jobService.get(id),
  })

export const useSaveJob = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (jobId: number) => jobService.save(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export const useUnsaveJob = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (jobId: number) => jobService.unsave(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export const useApplications = (status = '', skip = 0, limit = 10) =>
  useQuery({
    queryKey: ['applications', status, skip, limit],
    queryFn: () => applicationService.list(status, skip, limit),
  })

export const useCreateApplication = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (jobId: number) => applicationService.create(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export const useUpdateApplication = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      applicationService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

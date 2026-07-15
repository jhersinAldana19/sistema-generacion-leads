import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { z } from 'zod'

import logoColor from '@/assets/branding/logo-tecport.png'
import loginVideo from '@/assets/login/fondo-video-login.webm'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ApiError } from '@/services/apiClient'
import { useLogin } from '@/features/auth/useAuth'

const loginSchema = z.object({
  email: z.string().email('Ingresa un correo válido'),
  password: z.string().min(1, 'Ingresa tu contraseña'),
  remember_me: z.boolean(),
})

type LoginFormValues = z.infer<typeof loginSchema>

export function LoginForm() {
  const navigate = useNavigate()
  const login = useLogin()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '', remember_me: false },
  })

  const onSubmit = (values: LoginFormValues) => {
    login.mutate(values, {
      onSuccess: () => navigate('/', { replace: true }),
    })
  }

  const errorMessage =
    login.error instanceof ApiError ? login.error.message : login.error ? 'No se pudo iniciar sesión.' : null

  return (
    <div className="flex h-svh overflow-hidden">
      <div className="relative hidden w-1/2 shrink-0 overflow-hidden bg-brand-dark lg:block">
        <video
          className="h-full w-full object-cover"
          src={loginVideo}
          autoPlay
          muted
          loop
          playsInline
        />
        <div className="absolute inset-0 bg-brand-dark/30" />
      </div>

      <div className="flex w-full items-center justify-center overflow-y-auto bg-white px-4 lg:w-1/2">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex flex-col items-center gap-3 text-center">
            <img src={logoColor} alt="Tecport" className="h-20 w-auto" />
            <h1 className="text-lg font-semibold text-gray-900">Lead Intelligence</h1>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Correo</Label>
              <Input id="email" type="email" autoComplete="email" {...register('email')} />
              {errors.email && <p className="text-xs text-status-discarded">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Contraseña</Label>
              <Input id="password" type="password" autoComplete="current-password" {...register('password')} />
              {errors.password && <p className="text-xs text-status-discarded">{errors.password.message}</p>}
            </div>

            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input type="checkbox" className="rounded border-gray-300" {...register('remember_me')} />
              Mantener sesión iniciada
            </label>

            {errorMessage && <p className="text-sm text-status-discarded">{errorMessage}</p>}

            <Button type="submit" className="w-full" disabled={login.isPending}>
              {login.isPending ? 'Ingresando…' : 'Iniciar sesión'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}

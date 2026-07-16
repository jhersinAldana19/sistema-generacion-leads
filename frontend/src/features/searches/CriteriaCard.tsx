import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { Search } from 'lucide-react'
import { useForm } from 'react-hook-form'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { SearchCriteria } from '@/types/api'
import {
  REQUIRED_CONTACT_OPTIONS,
  criteriaFormSchema,
  criteriaToFormValues,
  formValuesToCriteria,
  type CriteriaFormValues,
} from '@/features/searches/criteriaSchema'

const ENTITY_TYPE_LABEL: Record<string, string> = {
  person: 'Persona',
  company: 'Empresa',
  supplier: 'Proveedor',
  institution: 'Institución',
  professional: 'Profesional',
  product: 'Producto',
}

function InfoRow({ label, values }: { label: string; values: string[] }) {
  if (values.length === 0) return null
  return (
    <div className="space-y-1">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-dark-text-muted">{label}</p>
      <div className="flex flex-wrap gap-1.5">
        {values.map((value) => (
          <Badge key={value} variant="neutral">
            {value}
          </Badge>
        ))}
      </div>
    </div>
  )
}

export function CriteriaCard({
  criteria,
  changeSummary,
  onConfirm,
  isConfirming = false,
  readOnly = false,
}: {
  criteria: SearchCriteria
  changeSummary?: string | null
  onConfirm?: (criteria: SearchCriteria) => void
  isConfirming?: boolean
  readOnly?: boolean
}) {
  const [isEditing, setIsEditing] = useState(false)
  const { register, handleSubmit, watch, setValue } = useForm<CriteriaFormValues>({
    resolver: zodResolver(criteriaFormSchema),
    defaultValues: criteriaToFormValues(criteria),
  })

  const requiredContacts = watch('required_contacts')

  const toggleContact = (value: (typeof REQUIRED_CONTACT_OPTIONS)[number]['value']) => {
    if (requiredContacts.includes(value)) {
      setValue(
        'required_contacts',
        requiredContacts.filter((item) => item !== value),
      )
    } else {
      setValue('required_contacts', [...requiredContacts, value])
    }
  }

  const submit = handleSubmit((values) => {
    const updated = formValuesToCriteria(values, criteria)
    setIsEditing(false)
    onConfirm?.(updated)
  })

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand/10 text-brand dark:bg-white/10 dark:text-dark-text">
              <Search className="size-3.5" />
            </span>
            <CardTitle>Entendí tu búsqueda</CardTitle>
          </div>
          <Badge variant="probable">{ENTITY_TYPE_LABEL[criteria.entity_type] ?? criteria.entity_type}</Badge>
        </div>
        <p className="text-sm text-gray-600 dark:text-dark-text-muted">{criteria.summary_es}</p>
        {changeSummary && (
          <p className="text-xs italic text-gray-400 dark:text-dark-text-muted">{changeSummary}</p>
        )}
      </CardHeader>

      {!isEditing ? (
        <CardContent className="grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-3">
          <InfoRow label="Cargo" values={criteria.job_levels} />
          <InfoRow label="Área" values={criteria.areas} />
          <InfoRow label="Sector" values={criteria.industries} />
          <InfoRow label="País" values={criteria.countries} />
          <InfoRow label="Ciudad" values={criteria.cities} />
          <InfoRow label="Productos / servicios" values={criteria.products_or_services} />
          <InfoRow label="Condiciones" values={criteria.conditions} />
          <InfoRow
            label="Datos requeridos"
            values={criteria.required_contacts.map(
              (c) => REQUIRED_CONTACT_OPTIONS.find((o) => o.value === c)?.label ?? c,
            )}
          />
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-dark-text-muted">
              Cantidad máxima
            </p>
            <p className="mt-1 text-sm text-gray-800 dark:text-dark-text">{criteria.max_results}</p>
          </div>
        </CardContent>
      ) : (
        <CardContent className="space-y-3">
          {(
            [
              ['job_levels', 'Cargo'],
              ['areas', 'Área'],
              ['industries', 'Sector'],
              ['countries', 'País'],
              ['cities', 'Ciudad'],
              ['products_or_services', 'Productos / servicios'],
              ['conditions', 'Condiciones'],
            ] as const
          ).map(([field, label]) => (
            <div key={field} className="space-y-1">
              <Label htmlFor={field}>{label}</Label>
              <Input id={field} placeholder="separado por comas" {...register(field)} />
            </div>
          ))}

          <div className="space-y-1">
            <Label htmlFor="max_results">Cantidad máxima de resultados</Label>
            <Input id="max_results" type="number" min={1} max={200} {...register('max_results')} />
          </div>

          <div className="space-y-1">
            <Label>Datos requeridos</Label>
            <div className="flex flex-wrap gap-3">
              {REQUIRED_CONTACT_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-1.5 text-sm text-gray-600 dark:text-dark-text-muted"
                >
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 dark:border-dark-border"
                    checked={requiredContacts.includes(option.value)}
                    onChange={() => toggleContact(option.value)}
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </div>
        </CardContent>
      )}

      {!readOnly && (
        <CardFooter>
          {isEditing ? (
            <>
              <Button variant="outline" size="sm" onClick={() => setIsEditing(false)}>
                Cancelar
              </Button>
              <Button size="sm" onClick={submit}>
                Guardar criterios
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                Editar criterios
              </Button>
              <Button size="sm" onClick={() => onConfirm?.(criteria)} disabled={isConfirming}>
                {isConfirming ? 'Iniciando…' : 'Iniciar búsqueda'}
              </Button>
            </>
          )}
        </CardFooter>
      )}
    </Card>
  )
}

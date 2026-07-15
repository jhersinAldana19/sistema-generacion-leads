import { z } from 'zod'

import type { RequiredContact, SearchCriteria } from '@/types/api'

export const REQUIRED_CONTACT_OPTIONS: { value: RequiredContact; label: string }[] = [
  { value: 'email', label: 'Correo' },
  { value: 'phone', label: 'Teléfono' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'website', label: 'Sitio web' },
]

export const criteriaFormSchema = z.object({
  job_levels: z.string(),
  areas: z.string(),
  industries: z.string(),
  countries: z.string(),
  cities: z.string(),
  products_or_services: z.string(),
  conditions: z.string(),
  max_results: z.string().regex(/^\d+$/, 'Ingresa un número'),
  required_contacts: z.array(z.enum(['email', 'phone', 'linkedin', 'website'])),
})

export type CriteriaFormValues = z.infer<typeof criteriaFormSchema>

function toCsv(values: string[]): string {
  return values.join(', ')
}

function fromCsv(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

export function criteriaToFormValues(criteria: SearchCriteria): CriteriaFormValues {
  return {
    job_levels: toCsv(criteria.job_levels),
    areas: toCsv(criteria.areas),
    industries: toCsv(criteria.industries),
    countries: toCsv(criteria.countries),
    cities: toCsv(criteria.cities),
    products_or_services: toCsv(criteria.products_or_services),
    conditions: toCsv(criteria.conditions),
    max_results: String(criteria.max_results),
    required_contacts: criteria.required_contacts,
  }
}

export function formValuesToCriteria(values: CriteriaFormValues, base: SearchCriteria): SearchCriteria {
  return {
    ...base,
    job_levels: fromCsv(values.job_levels),
    areas: fromCsv(values.areas),
    industries: fromCsv(values.industries),
    countries: fromCsv(values.countries),
    cities: fromCsv(values.cities),
    products_or_services: fromCsv(values.products_or_services),
    conditions: fromCsv(values.conditions),
    max_results: Number.parseInt(values.max_results, 10),
    required_contacts: values.required_contacts,
  }
}

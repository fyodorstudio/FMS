import type {
  FmsEngineStatus,
  FmsPortfolioSummary,
  FmsRegisteredSetupDTO,
  FmsSignalDTO,
} from './contracts/fms-api-types'

const apiBase = '/api/fms'

export class FmsRequestError extends Error {
  readonly status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function fmsRequest<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!response.ok) {
    throw new FmsRequestError(`FMS request failed with HTTP ${response.status}`, response.status)
  }

  return response.json() as Promise<T>
}

export async function fetchFmsHealth(signal?: AbortSignal): Promise<FmsEngineStatus> {
  return fmsRequest<FmsEngineStatus>('/health', signal)
}

export async function fetchFmsSetups(signal?: AbortSignal): Promise<FmsRegisteredSetupDTO[]> {
  const res = await fmsRequest<{ setups: FmsRegisteredSetupDTO[]; count: number }>('/setups', signal)
  return res.setups
}

export async function fetchFmsSummary(signal?: AbortSignal): Promise<FmsPortfolioSummary> {
  return fmsRequest<FmsPortfolioSummary>('/summary', signal)
}

export async function fetchFmsSignals(symbol: string, signal?: AbortSignal): Promise<FmsSignalDTO[]> {
  const res = await fmsRequest<{ symbol: string; signals: FmsSignalDTO[] }>(
    `/signals?symbol=${encodeURIComponent(symbol)}`,
    signal,
  )
  return res.signals
}

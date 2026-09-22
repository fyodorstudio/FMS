export type QuantMethod = 'M-MSD' | 'M-PYS' | 'M-TOT' | 'M-VRC' | 'M-LAR'

export type FmsSetupDirection = 'BUY' | 'SELL'

export type FmsRegisteredSetupDTO = {
  id: string
  quant_method: QuantMethod
  event_name: string
  currency: string
  symbol: string
  direction: FmsSetupDirection
  timeframe: string
  respect_rate: number
  sample_count: number
  median_mfe_pips: number
  mae_85_pips: number
  recommended_sl_pips: number
  recommended_tp_pips: number
  reward_risk_ratio: number
  trigger_state: string
  min_z_score: number
  active: boolean
  created_at: number
}

export type FmsMethodSummaryDTO = {
  method_id: string
  code: QuantMethod
  name: string
  description: string
  setup_count: number
  average_win_rate: number
  average_reward_risk: number
  aggregate_net_r: number
}

export type FmsPortfolioSummary = {
  methods: FmsMethodSummaryDTO[]
  total_setups: number
  total_net_r: number
  active_methods_count: number
  timestamp: number
}

export type FmsSignalDTO = {
  id: string
  time: number
  releaseTime: number
  price: number
  direction: 'long' | 'short'
  method: QuantMethod
  setup_name: string
  event_name: string
  version: 'v1' | 'v2'
  state: 'upcoming' | 'current' | 'recent'
  result: 'tp-reached' | 'sl-reached' | 'open' | 'no-trade'
  result_r: number | null
  recommended_tp_pips?: number
  recommended_sl_pips?: number
}

export type FmsEngineStatus = {
  status: 'operational' | 'offline'
  engine: string
  version: string
  registered_setups: number
  timestamp: number
}

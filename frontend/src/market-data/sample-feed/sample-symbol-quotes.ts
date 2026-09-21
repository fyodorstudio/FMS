import type { SymbolQuote } from '../contracts/SymbolQuote'

export const sampleSymbolQuotes: SymbolQuote[] = [
  { symbol: 'EURUSD', description: 'Euro / US Dollar', bid: 1.17642, ask: 1.17655, dailyChange: 0.18, precision: 5 },
  { symbol: 'GBPUSD', description: 'British Pound / US Dollar', bid: 1.35421, ask: 1.35439, dailyChange: -0.12, precision: 5 },
  { symbol: 'USDJPY', description: 'US Dollar / Japanese Yen', bid: 147.842, ask: 147.864, dailyChange: 0.36, precision: 3 },
  { symbol: 'AUDUSD', description: 'Australian Dollar / US Dollar', bid: 0.66218, ask: 0.66231, dailyChange: 0.08, precision: 5 },
  { symbol: 'NZDUSD', description: 'New Zealand Dollar / US Dollar', bid: 0.58146, ask: 0.58161, dailyChange: -0.27, precision: 5 },
  { symbol: 'USDCAD', description: 'US Dollar / Canadian Dollar', bid: 1.37382, ask: 1.37401, dailyChange: 0.14, precision: 5 },
  { symbol: 'USDCHF', description: 'US Dollar / Swiss Franc', bid: 0.79534, ask: 0.79549, dailyChange: -0.06, precision: 5 },
  { symbol: 'EURJPY', description: 'Euro / Japanese Yen', bid: 173.927, ask: 173.951, dailyChange: 0.51, precision: 3 },
  { symbol: 'EURGBP', description: 'Euro / British Pound', bid: 0.86872, ask: 0.86888, dailyChange: 0.22, precision: 5 },
  { symbol: 'GBPJPY', description: 'British Pound / Japanese Yen', bid: 200.241, ask: 200.278, dailyChange: -0.31, precision: 3 },
]

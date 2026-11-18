import type { BalanceAccount, Currency } from '@/types'
import { request } from '@/services/http'

interface ApiBalanceAccount {
  currency: string
  amount: number
}

interface BalanceResponse {
  company: string
  balances: ApiBalanceAccount[]
}

interface WithdrawResponse {
  withdrawn: number
  currency: string
  balance: number
}

export interface WithdrawResult {
  currency: Currency
  balance: number
}

function toCurrency(value?: string): Currency {
  return value === 'USD' || value === 'GBP' ? value : 'EUR'
}

export async function fetchBalances(): Promise<BalanceAccount[]> {
  const response = await request<BalanceResponse>('/balance')
  return response.balances.map((balance) => ({
    currency: toCurrency(balance.currency),
    amount: balance.amount,
  }))
}

export async function withdraw(currency: Currency, amount: number): Promise<WithdrawResult> {
  const response = await request<WithdrawResponse>('/withdraw', {
    method: 'POST',
    query: { amount: amount.toFixed(2), currency },
  })
  return { currency: toCurrency(response.currency), balance: response.balance }
}

import { Component, type ErrorInfo, type ReactNode } from 'react'

type MarketChartErrorBoundaryProps = {
  children: ReactNode
  symbol: string
  timeframe: string
  onError?: (error: Error) => void
}

type MarketChartErrorBoundaryState = {
  hasError: boolean
  errorMessage: string | null
  prevSymbol: string
  prevTimeframe: string
}

export class MarketChartErrorBoundary extends Component<
  MarketChartErrorBoundaryProps,
  MarketChartErrorBoundaryState
> {
  override state: MarketChartErrorBoundaryState = {
    hasError: false,
    errorMessage: null,
    prevSymbol: this.props.symbol,
    prevTimeframe: this.props.timeframe,
  }

  static getDerivedStateFromError(error: Error): Partial<MarketChartErrorBoundaryState> {
    return {
      hasError: true,
      errorMessage: error.message || 'Unknown chart rendering error',
    }
  }

  static getDerivedStateFromProps(
    props: MarketChartErrorBoundaryProps,
    state: MarketChartErrorBoundaryState,
  ): Partial<MarketChartErrorBoundaryState> | null {
    if (props.symbol !== state.prevSymbol || props.timeframe !== state.prevTimeframe) {
      return {
        hasError: false,
        errorMessage: null,
        prevSymbol: props.symbol,
        prevTimeframe: props.timeframe,
      }
    }
    return null
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.props.onError?.(error)
    console.error('MarketChartErrorBoundary caught an exception:', error, errorInfo)
  }

  private handleReset = (): void => {
    this.setState({ hasError: false, errorMessage: null })
  }

  override render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="chart-error-fallback" role="alert">
          <strong>Chart Rendering Paused</strong>
          <p>
            An unexpected error occurred while rendering the {this.props.symbol} {this.props.timeframe} chart:
            <br />
            <code>{this.state.errorMessage}</code>
          </p>
          <button type="button" onClick={this.handleReset}>
            Retry Chart
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

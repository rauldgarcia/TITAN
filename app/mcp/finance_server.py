import yfinance as yf
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("YahooFinance")

@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """
    Get the current stock price and currency for a given ticker symbol (e.g., AAPL, MSFT).
    """
    try:
        stock = yf.Ticker(ticker)
        price = stock.fast_info.last_price
        currency = stock.fast_info.currency
        return f"The current price of {ticker.upper()} is {price:.2f} {currency}."
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"
    
@mcp.tool()
def get_company_info(ticker: str) -> str:
    """
    Get basic profile information (sector, industry, market cap) for a company.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return (
            f"Profile for {ticker.upper()}:\n"
            f"- Sector: {info.get('sector', 'N/A')}\n"
            f"- Industry: {info.get('industry', 'N/A')}\n"
            f"- Market Cap: ${info.get('marketCap', 0):,}\n"
            f"- Summary: {info.get('longBusinessSummary', 'N/A')[:200]}..."
        )
    except Exception as e:
        return f"Error fetching info for {ticker}: {str(e)}"
    
if __name__ == "__main__":
    mcp.run()
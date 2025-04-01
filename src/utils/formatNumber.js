export const formatNumber = (num) => {
  if (num === undefined || num === null) return "N/A";
  
  // Handle very small numbers (like crypto prices)
  if (num < 0.01) {
    return num.toFixed(8);
  }
  
  // Handle regular numbers with comma formatting
  return num.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

// Format market cap and volume numbers to K, M, B, T
export const formatCompactNumber = (num) => {
  if (num === undefined || num === null) return "N/A";
  
  const trillion = 1e12;
  const billion = 1e9;
  const million = 1e6;
  const thousand = 1e3;

  if (num >= trillion) {
    return `$${(num / trillion).toFixed(2)}T`;
  }
  if (num >= billion) {
    return `$${(num / billion).toFixed(2)}B`;
  }
  if (num >= million) {
    return `$${(num / million).toFixed(2)}M`;
  }
  if (num >= thousand) {
    return `$${(num / thousand).toFixed(2)}K`;
  }
  
  return `$${num.toFixed(2)}`;
}; 
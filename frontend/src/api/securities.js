import apiClient from "./client";

const priceCache = new Map();

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function getPriceFromResponse(data) {
  return Number(
    data?.price ??
      data?.current_price ??
      data?.market_price ??
      data?.quote?.price ??
      data?.close ??
      data?.latest_price ??
      0
  );
}

function hasValidPrice(response) {
  return getPriceFromResponse(response?.data) > 0;
}

async function requestLiveQuote(normalizedTicker) {
  return apiClient.get(`/securities/quote/${normalizedTicker}`);
}

async function requestSavedSecurity(normalizedTicker) {
  return apiClient.get(`/securities/${normalizedTicker}`);
}

export async function getSecurity(ticker) {
  const normalizedTicker = ticker.toUpperCase();

  if (priceCache.has(normalizedTicker)) {
    return priceCache.get(normalizedTicker);
  }

  let firstResponse = null;

  try {
    firstResponse = await requestLiveQuote(normalizedTicker);
  } catch {
    firstResponse = null;
  }

  await delay(2000);

  try {
    const secondResponse = await requestLiveQuote(normalizedTicker);

    if (hasValidPrice(secondResponse)) {
      priceCache.set(normalizedTicker, secondResponse);
      return secondResponse;
    }

    if (firstResponse && hasValidPrice(firstResponse)) {
      priceCache.set(normalizedTicker, firstResponse);
      return firstResponse;
    }

    const savedSecurityResponse = await requestSavedSecurity(normalizedTicker);

    if (hasValidPrice(savedSecurityResponse)) {
      priceCache.set(normalizedTicker, savedSecurityResponse);
      return savedSecurityResponse;
    }

    return secondResponse;
  } catch (secondError) {
    if (firstResponse && hasValidPrice(firstResponse)) {
      priceCache.set(normalizedTicker, firstResponse);
      return firstResponse;
    }

    try {
      const savedSecurityResponse = await requestSavedSecurity(normalizedTicker);

      if (hasValidPrice(savedSecurityResponse)) {
        priceCache.set(normalizedTicker, savedSecurityResponse);
        return savedSecurityResponse;
      }
    } catch {
      // Use the live quote error below if saved security also fails.
    }

    throw secondError;
  }
}

export function clearSecurityPriceCache() {
  priceCache.clear();
}

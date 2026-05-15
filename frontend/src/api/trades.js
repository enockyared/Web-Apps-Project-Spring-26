import apiClient from "./client";

export function buySecurity(tradeData) {
  return apiClient.post("/trades/buy", tradeData);
}

export function sellSecurity(tradeData) {
  return apiClient.post("/trades/sell", tradeData);
}

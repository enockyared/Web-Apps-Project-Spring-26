import apiClient from "./client";

export function getUserPortfolios(username) {
  return apiClient.get(`/portfolios/user/${username}`);
}

export function getPortfolio(portfolioId) {
  return apiClient.get(`/portfolios/${portfolioId}`);
}

export function createPortfolio(portfolioData) {
  return apiClient.post("/portfolios/", portfolioData);
}

export function deletePortfolio(portfolioId) {
  return apiClient.delete(`/portfolios/${portfolioId}`);
}

export function getPortfolioTransactions(portfolioId) {
  return apiClient.get(`/portfolios/${portfolioId}/transactions`);
}

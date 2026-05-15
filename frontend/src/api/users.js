import apiClient from "./client";

export function getUser(username) {
  return apiClient.get(`/users/${username}`);
}

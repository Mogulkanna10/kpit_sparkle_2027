import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface AnalysisRequest {
  artifact_id: string;
  artifact_type: string;
  subsystem: string;
  ecu: string;
  change_type: string;
  after_content: string;
  change_semantics: string;
  force_semantic: boolean;
  filter_subsystem: boolean;
}

export const runAnalysis = async (request: AnalysisRequest) => {
  const response = await axios.post(`${API_URL}/analyze`, request);
  return response.data;
};

export const checkHealth = async () => {
  const response = await axios.get(`${API_URL}/health`);
  return response.data;
};

import apiClient from './client';

// Address interfaces
export interface Address {
  address_id: string;
  street_address_1: string;
  street_address_2?: string;
  city_id?: string;
  state_id?: string;
  zip_code?: string;
  country_id: string;
  latitude?: number;
  longitude?: number;
  address_type?: string;
  is_verified?: boolean;
  verification_date?: string;
  created_at: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  city_name?: string;
  state_name?: string;
  country_name?: string;
}

export interface AddressCreate {
  street_address_1: string;
  street_address_2?: string;
  city_id?: string;
  state_id?: string;
  zip_code?: string;
  country_id: string;
  latitude?: number;
  longitude?: number;
  address_type?: string;
  is_verified?: boolean;
  verification_date?: string;
}

export interface AddressUpdate {
  street_address_1?: string;
  street_address_2?: string;
  city_id?: string;
  state_id?: string;
  zip_code?: string;
  country_id?: string;
  latitude?: number;
  longitude?: number;
  address_type?: string;
  is_verified?: boolean;
  verification_date?: string;
}

// Address History interfaces
export interface AddressHistory {
  address_history_id: string;
  profile_id: string;
  address_id: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  address_type?: string;
  verification_document_id?: string;
  created_at: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  address?: Address;
}

export interface AddressHistoryCreate {
  address_id: string;
  start_date: string;
  end_date?: string;
  is_current?: boolean;
  address_type?: string;
  verification_document_id?: string;
}

export interface AddressHistoryUpdate {
  address_id?: string;
  start_date?: string;
  end_date?: string;
  is_current?: boolean;
  address_type?: string;
  verification_document_id?: string;
}

// Employer interfaces
export interface Employer {
  employer_id: string;
  company_name: string;
  company_ein?: string;
  company_type?: string;
  industry?: string;
  address_id?: string;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
  is_verified?: boolean;
  verification_date?: string;
  created_at: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  address?: Address;
}

export interface EmployerCreate {
  company_name: string;
  company_ein?: string;
  company_type?: string;
  industry?: string;
  address_id?: string;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
  is_verified?: boolean;
  verification_date?: string;
}

export interface EmployerUpdate {
  company_name?: string;
  company_ein?: string;
  company_type?: string;
  industry?: string;
  address_id?: string;
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
  is_verified?: boolean;
  verification_date?: string;
}

// Employment History interfaces
export interface EmploymentHistory {
  employment_id: string;
  profile_id: string;
  employer_id: string;
  job_title: string;
  job_description?: string;
  department?: string;
  employment_type?: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  salary?: number;
  salary_frequency?: string;
  working_hours_per_week?: number;
  work_location_id?: string;
  supervisor_name?: string;
  supervisor_title?: string;
  supervisor_phone?: string;
  supervisor_email?: string;
  termination_reason?: string;
  is_verified?: boolean;
  verification_document_id?: string;
  created_at: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  employer?: Employer;
  work_location?: Address;
}

export interface EmploymentHistoryCreate {
  employer_id: string;
  job_title: string;
  job_description?: string;
  department?: string;
  employment_type?: string;
  start_date: string;
  end_date?: string;
  is_current?: boolean;
  salary?: number;
  salary_frequency?: string;
  working_hours_per_week?: number;
  work_location_id?: string;
  supervisor_name?: string;
  supervisor_title?: string;
  supervisor_phone?: string;
  supervisor_email?: string;
  termination_reason?: string;
  is_verified?: boolean;
  verification_document_id?: string;
}

export interface EmploymentHistoryUpdate {
  employer_id?: string;
  job_title?: string;
  job_description?: string;
  department?: string;
  employment_type?: string;
  start_date?: string;
  end_date?: string;
  is_current?: boolean;
  salary?: number;
  salary_frequency?: string;
  working_hours_per_week?: number;
  work_location_id?: string;
  supervisor_name?: string;
  supervisor_title?: string;
  supervisor_phone?: string;
  supervisor_email?: string;
  termination_reason?: string;
  is_verified?: boolean;
  verification_document_id?: string;
}

// H1-B Validation interface
export interface H1BValidationResult {
  is_valid: boolean;
  issues: string[];
  warnings: string[];
}

class HistoryAPI {
  // Address Methods
  async getAddresses(skip: number = 0, limit: number = 100): Promise<Address[]> {
    const response = await apiClient.get(`/history/addresses?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async createAddress(addressData: AddressCreate): Promise<Address> {
    const response = await apiClient.post('/history/addresses', addressData);
    return response.data;
  }

  async getAddress(addressId: string): Promise<Address> {
    const response = await apiClient.get(`/history/addresses/${addressId}`);
    return response.data;
  }

  async updateAddress(addressId: string, addressData: AddressUpdate): Promise<Address> {
    const response = await apiClient.put(`/history/addresses/${addressId}`, addressData);
    return response.data;
  }

  async deleteAddress(addressId: string): Promise<void> {
    await apiClient.delete(`/history/addresses/${addressId}`);
  }

  // Address History Methods
  async getAddressHistory(skip: number = 0, limit: number = 100): Promise<AddressHistory[]> {
    const response = await apiClient.get(`/history/address-history?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async createAddressHistory(historyData: AddressHistoryCreate): Promise<AddressHistory> {
    const response = await apiClient.post('/history/address-history', historyData);
    return response.data;
  }

  async getAddressHistoryEntry(historyId: string): Promise<AddressHistory> {
    const response = await apiClient.get(`/history/address-history/${historyId}`);
    return response.data;
  }

  async updateAddressHistory(historyId: string, historyData: AddressHistoryUpdate): Promise<AddressHistory> {
    const response = await apiClient.put(`/history/address-history/${historyId}`, historyData);
    return response.data;
  }

  async deleteAddressHistory(historyId: string): Promise<void> {
    await apiClient.delete(`/history/address-history/${historyId}`);
  }

  // Employer Methods
  async getEmployers(skip: number = 0, limit: number = 100): Promise<Employer[]> {
    const response = await apiClient.get(`/history/employers?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async createEmployer(employerData: EmployerCreate): Promise<Employer> {
    const response = await apiClient.post('/history/employers', employerData);
    return response.data;
  }

  async getEmployer(employerId: string): Promise<Employer> {
    const response = await apiClient.get(`/history/employers/${employerId}`);
    return response.data;
  }

  async updateEmployer(employerId: string, employerData: EmployerUpdate): Promise<Employer> {
    const response = await apiClient.put(`/history/employers/${employerId}`, employerData);
    return response.data;
  }

  async deleteEmployer(employerId: string): Promise<void> {
    await apiClient.delete(`/history/employers/${employerId}`);
  }

  // Employment History Methods
  async getEmploymentHistory(skip: number = 0, limit: number = 100): Promise<EmploymentHistory[]> {
    const response = await apiClient.get(`/history/employment-history?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async createEmploymentHistory(historyData: EmploymentHistoryCreate): Promise<EmploymentHistory> {
    const response = await apiClient.post('/history/employment-history', historyData);
    return response.data;
  }

  async getEmploymentHistoryEntry(historyId: string): Promise<EmploymentHistory> {
    const response = await apiClient.get(`/history/employment-history/${historyId}`);
    return response.data;
  }

  async updateEmploymentHistory(historyId: string, historyData: EmploymentHistoryUpdate): Promise<EmploymentHistory> {
    const response = await apiClient.put(`/history/employment-history/${historyId}`, historyData);
    return response.data;
  }

  async deleteEmploymentHistory(historyId: string): Promise<void> {
    await apiClient.delete(`/history/employment-history/${historyId}`);
  }

  // H1-B Validation Methods
  async validateH1BEmployment(historyId?: string): Promise<H1BValidationResult> {
    const url = historyId 
      ? `/history/employment-history/${historyId}/validate-h1b` 
      : '/history/validate-h1b';
    const response = await apiClient.get(url);
    return response.data;
  }

  // Export Methods
  async exportAddressHistory(format: 'pdf' | 'csv' = 'pdf'): Promise<Blob> {
    const response = await apiClient.get(`/history/address-history/export?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async exportEmploymentHistory(format: 'pdf' | 'csv' = 'pdf'): Promise<Blob> {
    const response = await apiClient.get(`/history/employment-history/export?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  }
}

export const historyAPI = new HistoryAPI();
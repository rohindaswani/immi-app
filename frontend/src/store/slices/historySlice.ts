import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { 
  historyAPI, 
  Address, 
  AddressCreate, 
  AddressUpdate, 
  AddressHistory, 
  AddressHistoryCreate, 
  AddressHistoryUpdate,
  Employer,
  EmployerCreate,
  EmployerUpdate,
  EmploymentHistory,
  EmploymentHistoryCreate,
  EmploymentHistoryUpdate,
  H1BValidationResult
} from '../../api/history';

interface HistoryState {
  addresses: Address[];
  addressHistory: AddressHistory[];
  employers: Employer[];
  employmentHistory: EmploymentHistory[];
  h1bValidation: H1BValidationResult | null;
  loading: boolean;
  error: string | null;
  currentAddress: Address | null;
  currentAddressHistory: AddressHistory | null;
  currentEmployer: Employer | null;
  currentEmploymentHistory: EmploymentHistory | null;
}

const initialState: HistoryState = {
  addresses: [],
  addressHistory: [],
  employers: [],
  employmentHistory: [],
  h1bValidation: null,
  loading: false,
  error: null,
  currentAddress: null,
  currentAddressHistory: null,
  currentEmployer: null,
  currentEmploymentHistory: null,
};

// Address Thunks
export const fetchAddresses = createAsyncThunk(
  'history/fetchAddresses',
  async () => {
    return await historyAPI.getAddresses();
  }
);

export const createAddress = createAsyncThunk(
  'history/createAddress',
  async (addressData: AddressCreate) => {
    return await historyAPI.createAddress(addressData);
  }
);

export const fetchAddress = createAsyncThunk(
  'history/fetchAddress',
  async (addressId: string) => {
    return await historyAPI.getAddress(addressId);
  }
);

export const updateAddress = createAsyncThunk(
  'history/updateAddress',
  async ({ addressId, addressData }: { addressId: string; addressData: AddressUpdate }) => {
    return await historyAPI.updateAddress(addressId, addressData);
  }
);

export const deleteAddress = createAsyncThunk(
  'history/deleteAddress',
  async (addressId: string) => {
    await historyAPI.deleteAddress(addressId);
    return addressId;
  }
);

// Address History Thunks
export const fetchAddressHistory = createAsyncThunk(
  'history/fetchAddressHistory',
  async () => {
    return await historyAPI.getAddressHistory();
  }
);

export const createAddressHistory = createAsyncThunk(
  'history/createAddressHistory',
  async (historyData: AddressHistoryCreate) => {
    return await historyAPI.createAddressHistory(historyData);
  }
);

export const fetchAddressHistoryEntry = createAsyncThunk(
  'history/fetchAddressHistoryEntry',
  async (historyId: string) => {
    return await historyAPI.getAddressHistoryEntry(historyId);
  }
);

export const updateAddressHistory = createAsyncThunk(
  'history/updateAddressHistory',
  async ({ historyId, historyData }: { historyId: string; historyData: AddressHistoryUpdate }) => {
    return await historyAPI.updateAddressHistory(historyId, historyData);
  }
);

export const deleteAddressHistory = createAsyncThunk(
  'history/deleteAddressHistory',
  async (historyId: string) => {
    await historyAPI.deleteAddressHistory(historyId);
    return historyId;
  }
);

// Employer Thunks
export const fetchEmployers = createAsyncThunk(
  'history/fetchEmployers',
  async () => {
    return await historyAPI.getEmployers();
  }
);

export const createEmployer = createAsyncThunk(
  'history/createEmployer',
  async (employerData: EmployerCreate) => {
    return await historyAPI.createEmployer(employerData);
  }
);

export const fetchEmployer = createAsyncThunk(
  'history/fetchEmployer',
  async (employerId: string) => {
    return await historyAPI.getEmployer(employerId);
  }
);

export const updateEmployer = createAsyncThunk(
  'history/updateEmployer',
  async ({ employerId, employerData }: { employerId: string; employerData: EmployerUpdate }) => {
    return await historyAPI.updateEmployer(employerId, employerData);
  }
);

export const deleteEmployer = createAsyncThunk(
  'history/deleteEmployer',
  async (employerId: string) => {
    await historyAPI.deleteEmployer(employerId);
    return employerId;
  }
);

// Employment History Thunks
export const fetchEmploymentHistory = createAsyncThunk(
  'history/fetchEmploymentHistory',
  async () => {
    return await historyAPI.getEmploymentHistory();
  }
);

export const createEmploymentHistory = createAsyncThunk(
  'history/createEmploymentHistory',
  async (historyData: EmploymentHistoryCreate) => {
    return await historyAPI.createEmploymentHistory(historyData);
  }
);

export const fetchEmploymentHistoryEntry = createAsyncThunk(
  'history/fetchEmploymentHistoryEntry',
  async (historyId: string) => {
    return await historyAPI.getEmploymentHistoryEntry(historyId);
  }
);

export const updateEmploymentHistory = createAsyncThunk(
  'history/updateEmploymentHistory',
  async ({ historyId, historyData }: { historyId: string; historyData: EmploymentHistoryUpdate }) => {
    return await historyAPI.updateEmploymentHistory(historyId, historyData);
  }
);

export const deleteEmploymentHistory = createAsyncThunk(
  'history/deleteEmploymentHistory',
  async (historyId: string) => {
    await historyAPI.deleteEmploymentHistory(historyId);
    return historyId;
  }
);

// H1-B Validation Thunks
export const validateH1BEmployment = createAsyncThunk(
  'history/validateH1BEmployment',
  async (historyId?: string) => {
    return await historyAPI.validateH1BEmployment(historyId);
  }
);

// Export Thunks
export const exportAddressHistory = createAsyncThunk(
  'history/exportAddressHistory',
  async (format: 'pdf' | 'csv' = 'pdf') => {
    return await historyAPI.exportAddressHistory(format);
  }
);

export const exportEmploymentHistory = createAsyncThunk(
  'history/exportEmploymentHistory',
  async (format: 'pdf' | 'csv' = 'pdf') => {
    return await historyAPI.exportEmploymentHistory(format);
  }
);

const historySlice = createSlice({
  name: 'history',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    resetHistory: (state) => {
      return initialState;
    },
    setCurrentAddress: (state, action: PayloadAction<Address | null>) => {
      state.currentAddress = action.payload;
    },
    setCurrentAddressHistory: (state, action: PayloadAction<AddressHistory | null>) => {
      state.currentAddressHistory = action.payload;
    },
    setCurrentEmployer: (state, action: PayloadAction<Employer | null>) => {
      state.currentEmployer = action.payload;
    },
    setCurrentEmploymentHistory: (state, action: PayloadAction<EmploymentHistory | null>) => {
      state.currentEmploymentHistory = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Addresses
      .addCase(fetchAddresses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAddresses.fulfilled, (state, action) => {
        state.loading = false;
        state.addresses = action.payload;
      })
      .addCase(fetchAddresses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch addresses';
      })
      .addCase(createAddress.fulfilled, (state, action) => {
        state.addresses.push(action.payload);
      })
      .addCase(fetchAddress.fulfilled, (state, action) => {
        state.currentAddress = action.payload;
      })
      .addCase(updateAddress.fulfilled, (state, action) => {
        const index = state.addresses.findIndex(address => address.address_id === action.payload.address_id);
        if (index !== -1) {
          state.addresses[index] = action.payload;
        }
        if (state.currentAddress?.address_id === action.payload.address_id) {
          state.currentAddress = action.payload;
        }
      })
      .addCase(deleteAddress.fulfilled, (state, action) => {
        state.addresses = state.addresses.filter(address => address.address_id !== action.payload);
        if (state.currentAddress?.address_id === action.payload) {
          state.currentAddress = null;
        }
      })
      
      // Address History
      .addCase(fetchAddressHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAddressHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.addressHistory = action.payload;
      })
      .addCase(fetchAddressHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch address history';
      })
      .addCase(createAddressHistory.fulfilled, (state, action) => {
        state.addressHistory.push(action.payload);
      })
      .addCase(fetchAddressHistoryEntry.fulfilled, (state, action) => {
        state.currentAddressHistory = action.payload;
      })
      .addCase(updateAddressHistory.fulfilled, (state, action) => {
        const index = state.addressHistory.findIndex(history => history.address_history_id === action.payload.address_history_id);
        if (index !== -1) {
          state.addressHistory[index] = action.payload;
        }
        if (state.currentAddressHistory?.address_history_id === action.payload.address_history_id) {
          state.currentAddressHistory = action.payload;
        }
      })
      .addCase(deleteAddressHistory.fulfilled, (state, action) => {
        state.addressHistory = state.addressHistory.filter(history => history.address_history_id !== action.payload);
        if (state.currentAddressHistory?.address_history_id === action.payload) {
          state.currentAddressHistory = null;
        }
      })
      
      // Employers
      .addCase(fetchEmployers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEmployers.fulfilled, (state, action) => {
        state.loading = false;
        state.employers = action.payload;
      })
      .addCase(fetchEmployers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch employers';
      })
      .addCase(createEmployer.fulfilled, (state, action) => {
        state.employers.push(action.payload);
      })
      .addCase(fetchEmployer.fulfilled, (state, action) => {
        state.currentEmployer = action.payload;
      })
      .addCase(updateEmployer.fulfilled, (state, action) => {
        const index = state.employers.findIndex(employer => employer.employer_id === action.payload.employer_id);
        if (index !== -1) {
          state.employers[index] = action.payload;
        }
        if (state.currentEmployer?.employer_id === action.payload.employer_id) {
          state.currentEmployer = action.payload;
        }
      })
      .addCase(deleteEmployer.fulfilled, (state, action) => {
        state.employers = state.employers.filter(employer => employer.employer_id !== action.payload);
        if (state.currentEmployer?.employer_id === action.payload) {
          state.currentEmployer = null;
        }
      })
      
      // Employment History
      .addCase(fetchEmploymentHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEmploymentHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.employmentHistory = action.payload;
      })
      .addCase(fetchEmploymentHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch employment history';
      })
      .addCase(createEmploymentHistory.fulfilled, (state, action) => {
        state.employmentHistory.push(action.payload);
      })
      .addCase(fetchEmploymentHistoryEntry.fulfilled, (state, action) => {
        state.currentEmploymentHistory = action.payload;
      })
      .addCase(updateEmploymentHistory.fulfilled, (state, action) => {
        const index = state.employmentHistory.findIndex(history => history.employment_id === action.payload.employment_id);
        if (index !== -1) {
          state.employmentHistory[index] = action.payload;
        }
        if (state.currentEmploymentHistory?.employment_id === action.payload.employment_id) {
          state.currentEmploymentHistory = action.payload;
        }
      })
      .addCase(deleteEmploymentHistory.fulfilled, (state, action) => {
        state.employmentHistory = state.employmentHistory.filter(history => history.employment_id !== action.payload);
        if (state.currentEmploymentHistory?.employment_id === action.payload) {
          state.currentEmploymentHistory = null;
        }
      })
      
      // H1-B Validation
      .addCase(validateH1BEmployment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(validateH1BEmployment.fulfilled, (state, action) => {
        state.loading = false;
        state.h1bValidation = action.payload;
      })
      .addCase(validateH1BEmployment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to validate H1-B employment';
      })
      
      // Generic error handling
      .addMatcher(
        (action) => action.type.endsWith('/rejected'),
        (state, action) => {
          state.loading = false;
          state.error = action.error.message || 'An error occurred';
        }
      );
  },
});

export const { 
  clearError, 
  resetHistory,
  setCurrentAddress,
  setCurrentAddressHistory,
  setCurrentEmployer,
  setCurrentEmploymentHistory,
} = historySlice.actions;
export default historySlice.reducer;
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';

import App from './App';
import theme from './theme';
import { store } from './store';

// Mock the router hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useLocation: () => ({
    pathname: '/',
    search: '',
    hash: '',
    state: null,
    key: 'default',
  }),
}));

describe('App Component', () => {
  test('renders without crashing', () => {
    render(
      <Provider store={store}>
        <BrowserRouter>
          <ThemeProvider theme={theme}>
            <App />
          </ThemeProvider>
        </BrowserRouter>
      </Provider>
    );
    
    // The app should render without throwing
    expect(true).toBeTruthy();
  });
});
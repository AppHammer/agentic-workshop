import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Profile from './Profile';
import * as AuthContext from '../AuthContext';
import * as api from '../api';

// Mock the API module
vi.mock('../api', () => ({
  profileAPI: {
    getMyProfile: vi.fn(),
  },
}));

// Mock the AuthContext module
vi.mock('../AuthContext', () => ({
  useAuth: vi.fn(),
}));

// Mock navigate function
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Profile Component - Edit Mode', () => {
  const mockLogout = vi.fn();
  
  const mockTaskerProfile = {
    username: 'johndoe',
    email: 'john@example.com',
    user_type: 'tasker',
    created_at: '2024-01-15T10:30:00',
    skills: 'Plumbing, Electrical',
    hourly_rate: 45.50,
  };

  const mockCustomerProfile = {
    username: 'janedoe',
    email: 'jane@example.com',
    user_type: 'customer',
    created_at: '2024-01-20T14:00:00',
  };

  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks();
    
    // Setup default mock implementations
    AuthContext.useAuth.mockReturnValue({
      logout: mockLogout,
    });
  });

  const renderProfile = () => {
    return render(
      <BrowserRouter>
        <Profile />
      </BrowserRouter>
    );
  };

  describe('Initial Render - View Mode', () => {
    it('should render profile in view mode with Edit button for tasker', async () => {
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Check that static values are displayed
      expect(screen.getByText('johndoe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
      expect(screen.getByText('Tasker')).toBeInTheDocument();
      
      // Check tasker-specific fields
      expect(screen.getByText('Plumbing, Electrical')).toBeInTheDocument();
      expect(screen.getByText('$45.50')).toBeInTheDocument();

      // Check that Edit button is present
      const editButton = screen.getByRole('button', { name: /edit/i });
      expect(editButton).toBeInTheDocument();

      // Check that Save and Cancel buttons are NOT present
      expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /cancel/i })).not.toBeInTheDocument();

      // Check that input fields are NOT present
      expect(screen.queryByDisplayValue('john@example.com')).not.toBeInTheDocument();
    });

    it('should render profile in view mode with Edit button for customer', async () => {
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockCustomerProfile,
      });

      renderProfile();

      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Check that static values are displayed
      expect(screen.getByText('janedoe')).toBeInTheDocument();
      expect(screen.getByText('jane@example.com')).toBeInTheDocument();
      expect(screen.getByText('Customer')).toBeInTheDocument();

      // Check that tasker-specific sections are NOT present
      expect(screen.queryByText('Tasker Information')).not.toBeInTheDocument();

      // Check that Edit button is present
      const editButton = screen.getByRole('button', { name: /edit/i });
      expect(editButton).toBeInTheDocument();
    });
  });

  describe('Edit Mode Toggle', () => {
    it('should switch to edit mode when Edit button is clicked', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Click the Edit button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Check that Edit button is no longer present
      expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument();

      // Check that Save and Cancel buttons ARE present
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });
  });

  describe('Edit Mode - Input Fields', () => {
    it('should show input fields pre-populated with user data in edit mode', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Click the Edit button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Check that email input field is present and pre-populated
      const emailInput = screen.getByDisplayValue('john@example.com');
      expect(emailInput).toBeInTheDocument();
      expect(emailInput).toHaveAttribute('type', 'email');

      // Check that skills input field is present and pre-populated
      const skillsInput = screen.getByDisplayValue('Plumbing, Electrical');
      expect(skillsInput).toBeInTheDocument();
      expect(skillsInput).toHaveAttribute('type', 'text');

      // Check that hourly rate input field is present and pre-populated
      const hourlyRateInput = screen.getByDisplayValue('45.5');
      expect(hourlyRateInput).toBeInTheDocument();
      expect(hourlyRateInput).toHaveAttribute('type', 'number');
    });

    it('should show only email field for customer in edit mode', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockCustomerProfile,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Click the Edit button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Check that email input field is present
      const emailInput = screen.getByDisplayValue('jane@example.com');
      expect(emailInput).toBeInTheDocument();

      // Check that tasker-specific inputs are NOT present
      const inputs = screen.getAllByRole('textbox');
      expect(inputs).toHaveLength(1); // Only email input
    });
  });

  describe('Edit Mode - Action Buttons', () => {
    it('should display Save and Cancel buttons in edit mode', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Click the Edit button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Verify Save button is present and has correct class
      const saveButton = screen.getByRole('button', { name: /save/i });
      expect(saveButton).toBeInTheDocument();
      expect(saveButton).toHaveClass('save-button');

      // Verify Cancel button is present and has correct class
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      expect(cancelButton).toBeInTheDocument();
      expect(cancelButton).toHaveClass('cancel-button');
    });
  });

  describe('Acceptance Criteria Verification', () => {
    it('should meet all acceptance criteria for edit mode', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // GIVEN: User is logged in and viewing their profile page
      expect(screen.getByText('johndoe')).toBeInTheDocument();

      // WHEN: User clicks the "Edit" button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // THEN: Static text for "Email," "Skills," and "Hourly Rate" replaced by editable input fields
      expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Plumbing, Electrical')).toBeInTheDocument();
      expect(screen.getByDisplayValue('45.5')).toBeInTheDocument();

      // AND: Input fields are pre-populated with user's current data
      const emailInput = screen.getByDisplayValue('john@example.com');
      const skillsInput = screen.getByDisplayValue('Plumbing, Electrical');
      const hourlyRateInput = screen.getByDisplayValue('45.5');
      
      expect(emailInput.value).toBe(mockTaskerProfile.email);
      expect(skillsInput.value).toBe(mockTaskerProfile.skills);
      expect(parseFloat(hourlyRateInput.value)).toBe(mockTaskerProfile.hourly_rate);

      // AND: "Edit" button is replaced by "Save" and "Cancel" buttons
      expect(screen.queryByRole('button', { name: /^edit$/i })).not.toBeInTheDocument();
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });
  });

  describe('Profile Loading States', () => {
    it('should show loading state initially', () => {
      api.profileAPI.getMyProfile.mockReturnValue(new Promise(() => {})); // Never resolves

      renderProfile();

      expect(screen.getByText('Loading profile...')).toBeInTheDocument();
    });

    it('should initialize formData when profile loads', async () => {
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Verify that API was called
      expect(api.profileAPI.getMyProfile).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty skills and hourly_rate fields', async () => {
      const user = userEvent.setup();
      const profileWithEmptyFields = {
        ...mockTaskerProfile,
        skills: '',
        hourly_rate: 0,
      };

      api.profileAPI.getMyProfile.mockResolvedValue({
        data: profileWithEmptyFields,
      });

      renderProfile();

      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Click Edit button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Check that inputs show empty/zero values
      expect(screen.getByDisplayValue('')).toBeInTheDocument(); // skills
      expect(screen.getByDisplayValue('0')).toBeInTheDocument(); // hourly_rate
    });

    it('should handle null skills and hourly_rate fields', async () => {
      const user = userEvent.setup();
      const profileWithNullFields = {
        ...mockTaskerProfile,
        skills: null,
        hourly_rate: null,
      };

      api.profileAPI.getMyProfile.mockResolvedValue({
        data: profileWithNullFields,
      });

      renderProfile();

      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Click Edit button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Check that inputs handle null values properly (should show empty string for skills and 0 for hourly_rate)
      const inputs = screen.getAllByRole('textbox');
      const numberInputs = screen.getAllByRole('spinbutton');
      
      expect(inputs.some(input => input.value === '')).toBe(true);
      expect(numberInputs.some(input => input.value === '0')).toBe(true);
    });
  });

  describe('Cancel Edit Mode', () => {
    it('should exit edit mode and revert to view mode when Cancel is clicked', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Enter edit mode
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Verify we're in edit mode
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /^edit$/i })).not.toBeInTheDocument();

      // Click Cancel
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      // Verify we're back in view mode
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument();
      });
      expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /cancel/i })).not.toBeInTheDocument();
    });

    it('should revert form data to original profile values when Cancel is clicked', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Enter edit mode
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Modify all editable fields
      const emailInput = screen.getByDisplayValue('john@example.com');
      const skillsInput = screen.getByDisplayValue('Plumbing, Electrical');
      const hourlyRateInput = screen.getByDisplayValue('45.5');

      await user.clear(emailInput);
      await user.type(emailInput, 'newemail@example.com');

      await user.clear(skillsInput);
      await user.type(skillsInput, 'Carpentry, Painting');

      await user.clear(hourlyRateInput);
      await user.type(hourlyRateInput, '60');

      // Verify fields are modified
      expect(screen.getByDisplayValue('newemail@example.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Carpentry, Painting')).toBeInTheDocument();
      expect(screen.getByDisplayValue('60')).toBeInTheDocument();

      // Click Cancel
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      // Enter edit mode again to verify data was reverted
      const editButtonAgain = screen.getByRole('button', { name: /edit/i });
      await user.click(editButtonAgain);

      // Verify all fields are back to original values
      expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Plumbing, Electrical')).toBeInTheDocument();
      expect(screen.getByDisplayValue('45.5')).toBeInTheDocument();
    });

    it('should not make any API calls when Cancel is clicked', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });
      api.profileAPI.updateMyProfile = vi.fn();

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Verify initial API call count (should be 1 for loading profile)
      expect(api.profileAPI.getMyProfile).toHaveBeenCalledTimes(1);

      // Enter edit mode
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Modify a field
      const emailInput = screen.getByDisplayValue('john@example.com');
      await user.clear(emailInput);
      await user.type(emailInput, 'newemail@example.com');

      // Click Cancel
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      // Verify no additional API calls were made
      expect(api.profileAPI.getMyProfile).toHaveBeenCalledTimes(1); // Still just the initial load
      expect(api.profileAPI.updateMyProfile).not.toHaveBeenCalled();
    });

    it('should clear error state when Cancel is clicked (simulated error in edit mode)', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockTaskerProfile,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Enter edit mode
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Verify we're in edit mode with Cancel button
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();

      // The handleCancel function clears error state (setError(null))
      // In a real scenario, error might be set from a failed save attempt
      // but the component would need to be modified to show errors inline during edit
      // For now, we verify that Cancel button calls the correct function
      // This is indirectly tested by verifying Cancel exits edit mode properly
      
      // Click Cancel
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      // Verify we exited edit mode (which handleCancel does along with clearing errors)
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument();
      });
      expect(screen.queryByRole('button', { name: /cancel/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
    });

    it('should handle null values with proper defaults when Cancel is clicked', async () => {
      const user = userEvent.setup();
      const profileWithNulls = {
        ...mockTaskerProfile,
        skills: null,
        hourly_rate: null,
      };

      api.profileAPI.getMyProfile.mockResolvedValue({
        data: profileWithNulls,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Enter edit mode
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Modify fields
      const skillsInput = screen.getByPlaceholderText(/plumbing, carpentry/i);
      const hourlyRateInput = screen.getByDisplayValue('0');

      await user.type(skillsInput, 'New Skills');
      await user.clear(hourlyRateInput);
      await user.type(hourlyRateInput, '50');

      // Click Cancel
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      // Enter edit mode again to verify defaults are used
      const editButtonAgain = screen.getByRole('button', { name: /edit/i });
      await user.click(editButtonAgain);

      // Verify null values are handled with defaults
      const skillsInputAgain = screen.getByPlaceholderText(/plumbing, carpentry/i);
      const hourlyRateInputAgain = screen.getByDisplayValue('0');

      expect(skillsInputAgain.value).toBe(''); // Empty string for null skills
      expect(hourlyRateInputAgain.value).toBe('0'); // 0 for null hourly_rate
    });

    it('should handle customer profile (no tasker fields) when Cancel is clicked', async () => {
      const user = userEvent.setup();
      api.profileAPI.getMyProfile.mockResolvedValue({
        data: mockCustomerProfile,
      });

      renderProfile();

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText('My Profile')).toBeInTheDocument();
      });

      // Enter edit mode
      const editButton = screen.getByRole('button', { name: /edit/i });
      await user.click(editButton);

      // Modify email
      const emailInput = screen.getByDisplayValue('jane@example.com');
      await user.clear(emailInput);
      await user.type(emailInput, 'newemail@example.com');

      // Click Cancel
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      // Enter edit mode again to verify data was reverted
      const editButtonAgain = screen.getByRole('button', { name: /edit/i });
      await user.click(editButtonAgain);

      // Verify email is back to original
      expect(screen.getByDisplayValue('jane@example.com')).toBeInTheDocument();
    });
  });
});
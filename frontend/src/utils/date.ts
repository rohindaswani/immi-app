/**
 * Format a date string to a readable format
 * @param dateString ISO date string
 * @returns Formatted date string (e.g., "Jan 15, 2023")
 */
export const formatDate = (dateString: string) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    return dateString; // Return original string if invalid
  }
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

/**
 * Format a date for input fields (YYYY-MM-DD)
 * @param dateString ISO date string
 * @returns Formatted date string for date inputs
 */
export const formatDateForInput = (dateString: string | undefined) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    return ''; // Return empty string if invalid
  }
  
  return date.toISOString().split('T')[0];
};

/**
 * Calculate days remaining until a date
 * @param dateString ISO date string
 * @returns Number of days remaining
 */
export const getDaysRemaining = (dateString: string) => {
  if (!dateString) return null;
  
  const targetDate = new Date(dateString);
  
  // Check if date is valid
  if (isNaN(targetDate.getTime())) {
    return null;
  }
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const timeDiff = targetDate.getTime() - today.getTime();
  const daysRemaining = Math.ceil(timeDiff / (1000 * 3600 * 24));
  
  return daysRemaining;
};

/**
 * Check if a date is within a certain number of days
 * @param dateString ISO date string
 * @param days Number of days
 * @returns Boolean indicating if date is within specified days
 */
export const isDateWithinDays = (dateString: string, days: number) => {
  const daysRemaining = getDaysRemaining(dateString);
  
  if (daysRemaining === null) {
    return false;
  }
  
  return daysRemaining <= days && daysRemaining >= 0;
};
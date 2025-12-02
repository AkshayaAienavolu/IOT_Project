// Utility functions for client ID management
// Can be used for debugging and ensuring ID consistency

(function() {
  'use strict';
  
  // Check if client ID exists and is consistent across storage mechanisms
  window.verifyClientId = function() {
    const key = 'fer_client_id';
    const results = {
      localStorage: null,
      cookie: null,
      consistent: false,
      format: 'unknown'
    };
    
    // Check localStorage
    try {
      results.localStorage = localStorage.getItem(key);
    } catch (e) {
      results.localStorage = 'ERROR: ' + e.message;
    }
    
    // Check cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === key) {
        results.cookie = value;
        break;
      }
    }
    
    // Check consistency
    if (results.localStorage && results.cookie) {
      results.consistent = results.localStorage === results.cookie;
    }
    
    // Determine format
    const id = results.localStorage || results.cookie;
    if (id) {
      if (id.startsWith('fer_webapp_')) {
        results.format = 'NEW (fer_webapp_)';
      } else if (id.startsWith('fer_web_')) {
        results.format = 'OLD (fer_web_) - NEEDS MIGRATION';
      } else {
        results.format = 'UNKNOWN';
      }
    }
    
    console.log('Client ID Verification:', results);
    return results;
  };
  
  // Force client ID migration (call this if user has issues)
  window.migrateClientId = function() {
    const key = 'fer_client_id';
    let id = localStorage.getItem(key);
    
    if (!id) {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === key) {
          id = value;
          break;
        }
      }
    }
    
    if (!id) {
      console.log('No existing client ID found. Nothing to migrate.');
      return false;
    }
    
    if (id.startsWith('fer_web_') && !id.startsWith('fer_webapp_')) {
      const newId = id.replace('fer_web_', 'fer_webapp_');
      
      // Update both storages
      localStorage.setItem(key, newId);
      const expires = new Date();
      expires.setFullYear(expires.getFullYear() + 1);
      document.cookie = `${key}=${newId}; expires=${expires.toUTCString()}; path=/; SameSite=Strict`;
      
      console.log(`Migrated: ${id} → ${newId}`);
      return newId;
    }
    
    console.log('ID is already in correct format:', id);
    return id;
  };
  
  // Get current client ID (reads from storage without creating new one)
  window.getCurrentClientId = function() {
    const key = 'fer_client_id';
    let id = localStorage.getItem(key);
    
    if (!id) {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === key) {
          id = value;
          break;
        }
      }
    }
    
    return id || 'NO_ID_FOUND';
  };
  
  // Clear client ID (for testing - will generate new ID on next page load)
  window.clearClientId = function() {
    const key = 'fer_client_id';
    localStorage.removeItem(key);
    document.cookie = `${key}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    console.log('Client ID cleared. Reload page to generate new ID.');
  };
  
  // Auto-log ID status on page load (if ?debug=1 in URL)
  if (window.location.search.includes('debug=1')) {
    console.log('=== CLIENT ID DEBUG MODE ===');
    console.log('Current ID:', window.getCurrentClientId());
    window.verifyClientId();
  }
})();

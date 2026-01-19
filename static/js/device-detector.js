/**
 * Device Detection Script for VFG-AI
 * Detects mobile vs desktop and redirects to appropriate UI
 */

(function() {
    'use strict';

    const MOBILE_PATH = '/mobile';
    const DESKTOP_PATH = '/';
    const PREFERENCE_KEY = 'vfg-device-preference';

    /**
     * Detect if device is mobile based on multiple signals
     */
    function isMobileDevice() {
        // Check for saved user preference first
        const savedPreference = localStorage.getItem(PREFERENCE_KEY);
        if (savedPreference) {
            return savedPreference === 'mobile';
        }

        // Check for touch capability
        const hasTouch = 'ontouchstart' in window || 
                         navigator.maxTouchPoints > 0 || 
                         navigator.msMaxTouchPoints > 0;

        // Check screen width (mobile-first breakpoint)
        const isNarrowScreen = window.innerWidth <= 768;

        // Check user agent for mobile keywords
        const mobileKeywords = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|CriOS/i;
        const isMobileUA = mobileKeywords.test(navigator.userAgent);

        // Check if device is tablet (larger touch device)
        const isTablet = /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);

        // Decision: mobile if (narrow screen AND touch) OR (mobile UA AND not tablet on wide screen)
        if (isNarrowScreen && hasTouch) {
            return true;
        }
        if (isMobileUA && !isTablet && isNarrowScreen) {
            return true;
        }
        if (isMobileUA && hasTouch && window.innerWidth <= 1024) {
            return true;
        }

        return false;
    }

    /**
     * Get current path without query params
     */
    function getCurrentPath() {
        return window.location.pathname;
    }

    /**
     * Redirect to appropriate UI based on device type
     */
    function redirectIfNeeded() {
        const currentPath = getCurrentPath();
        const mobile = isMobileDevice();

        // If on root and should be mobile, redirect to mobile
        if (mobile && currentPath === DESKTOP_PATH) {
            window.location.replace(MOBILE_PATH);
            return;
        }

        // If on mobile path but should be desktop, redirect to desktop
        if (!mobile && currentPath === MOBILE_PATH) {
            window.location.replace(DESKTOP_PATH);
            return;
        }
    }

    /**
     * Set device preference (for manual toggle)
     */
    window.setDevicePreference = function(preference) {
        if (preference === 'mobile' || preference === 'desktop') {
            localStorage.setItem(PREFERENCE_KEY, preference);
            window.location.reload();
        } else if (preference === 'auto') {
            localStorage.removeItem(PREFERENCE_KEY);
            window.location.reload();
        }
    };

    /**
     * Get current device preference
     */
    window.getDevicePreference = function() {
        return localStorage.getItem(PREFERENCE_KEY) || 'auto';
    };

    // Run detection immediately
    redirectIfNeeded();

    // Also listen for resize events (e.g., device rotation or browser resize)
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Only redirect if no saved preference
            if (!localStorage.getItem(PREFERENCE_KEY)) {
                redirectIfNeeded();
            }
        }, 500);
    });

})();

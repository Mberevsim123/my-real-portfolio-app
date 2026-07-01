/**
 * Portfolio Main JavaScript - Water Theme
 * Professional, Optimized, and Performant
 * Version: 2.1.0
 */

(function() {
    'use strict';
    
    // ============================================
    // DOM Element Cache
    // ============================================
    const dom = {
        navbar: document.getElementById('mainNav'),
        themeToggle: document.getElementById('themeToggle'),
        backToTop: document.getElementById('backToTop'),
        pageLoader: document.getElementById('pageLoader'),
        alerts: document.querySelectorAll('.alert'),
        lazyImages: document.querySelectorAll('img[data-src]'),
        forms: document.querySelectorAll('form'),
        toastContainer: document.querySelector('.toast-container'),
        newsletterForm: document.querySelector('.newsletter-form'),
        searchInput: document.querySelector('input[name="q"]'),
        projectFilters: document.querySelectorAll('.filter-btn'),
        passwordToggles: document.querySelectorAll('.toggle-password'),
        progressBars: document.querySelectorAll('.skill-progress .progress-bar'),
        counters: document.querySelectorAll('.stat-number'),
        codeBlocks: document.querySelectorAll('pre'),
        tooltips: document.querySelectorAll('[data-bs-toggle="tooltip"]'),
        dropdowns: document.querySelectorAll('.dropdown-toggle')
    };
    
    // ============================================
    // Utility Functions
    // ============================================
    
    /**
     * Debounce function to limit function calls
     */
    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    /**
     * Throttle function to limit function calls
     */
    const throttle = (func, limit) => {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    };
    
    /**
     * Escape HTML to prevent XSS
     */
    const escapeHtml = (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };
    
    /**
     * Get CSRF token from cookies
     */
    const getCsrfToken = () => {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                return cookie.substring(name.length + 1);
            }
        }
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    };
    
    /**
     * Show toast notification
     */
    const showToast = (message, type = 'success') => {
        if (!dom.toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        // Water-themed colors based on type
        const bgColors = {
            success: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
            error: 'linear-gradient(135deg, #ef4444, #dc2626)',
            warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
            info: 'linear-gradient(135deg, #3b82f6, #2563eb)'
        };
        
        toast.style.background = bgColors[type] || bgColors.success;
        toast.style.borderRadius = '12px';
        toast.style.boxShadow = '0 8px 32px rgba(14, 165, 233, 0.2)';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${escapeHtml(message)}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        dom.toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    };
    
    // ============================================
    // Core Functionality
    // ============================================
    
    /**
     * Initialize page loader
     */
    const initPageLoader = () => {
        if (!dom.pageLoader) return;
        
        window.addEventListener('load', () => {
            dom.pageLoader.classList.add('fade-out');
            setTimeout(() => {
                dom.pageLoader.style.display = 'none';
            }, 300);
        });
    };
    
    /**
     * Initialize theme toggling with system preference
     */
    const initThemeToggle = () => {
        if (!dom.themeToggle) return;
        
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        const savedTheme = localStorage.getItem('theme') || 'system';
        let activeTheme = savedTheme === 'system' ? systemTheme : savedTheme;
        document.documentElement.setAttribute('data-bs-theme', activeTheme);
        
        const updateThemeIcon = (theme) => {
            const icon = dom.themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        };
        
        const updateDropdownIcon = (theme) => {
            const dropdownItems = document.querySelectorAll('.dropdown-item i');
            dropdownItems.forEach(item => {
                if (item.classList.contains('text-primary')) {
                    item.style.color = theme === 'dark' ? '#38bdf8' : '#0ea5e9';
                }
            });
        };
        
        updateThemeIcon(activeTheme);
        updateDropdownIcon(activeTheme);
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (localStorage.getItem('theme') === 'system') {
                const newTheme = e.matches ? 'dark' : 'light';
                document.documentElement.setAttribute('data-bs-theme', newTheme);
                updateThemeIcon(newTheme);
                updateDropdownIcon(newTheme);
            }
        });
        
        dom.themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            updateDropdownIcon(newTheme);
        });
    };
    
    /**
     * Initialize navbar scroll effect
     */
    const initNavbarScroll = () => {
        if (!dom.navbar) return;
        
        const handleScroll = throttle(() => {
            if (window.scrollY > 100) {
                dom.navbar.classList.add('scrolled');
            } else {
                dom.navbar.classList.remove('scrolled');
            }
        }, 100);
        
        window.addEventListener('scroll', handleScroll);
        handleScroll();
    };
    
    /**
     * Initialize back to top button
     */
    const initBackToTop = () => {
        if (!dom.backToTop) return;
        
        window.addEventListener('scroll', throttle(() => {
            if (window.scrollY > 500) {
                dom.backToTop.classList.add('show');
            } else {
                dom.backToTop.classList.remove('show');
            }
        }, 100));
        
        dom.backToTop.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    };
    
    /**
     * Initialize auto-hide alerts
     */
    const initAutoHideAlerts = () => {
        if (!dom.alerts.length) return;
        
        dom.alerts.forEach(alert => {
            // Add water theme to alerts
            const alertType = alert.classList.contains('alert-success') ? 'success' :
                              alert.classList.contains('alert-info') ? 'info' :
                              alert.classList.contains('alert-warning') ? 'warning' :
                              alert.classList.contains('alert-danger') ? 'error' : 'info';
            
            alert.style.borderLeft = `4px solid ${alertType === 'success' ? '#0ea5e9' : 
                                                        alertType === 'warning' ? '#f59e0b' : 
                                                        alertType === 'error' ? '#ef4444' : '#3b82f6'}`;
            
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }, 5000);
        });
    };
    
    /**
     * Initialize active navigation highlighting
     */
    const initActiveNavHighlight = () => {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href !== '#' && currentPath === href) {
                link.classList.add('active');
            } else if (href && href !== '#' && currentPath.startsWith(href) && href !== '/' && href.length > 1) {
                link.classList.add('active');
            }
        });
    };
    
    /**
     * Initialize lazy loading images with water theme placeholder
     */
    const initLazyLoading = () => {
        if (!dom.lazyImages.length) return;
        
        // Add loading animation
        dom.lazyImages.forEach(img => {
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.5s ease';
        });
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.dataset.src;
                        if (src) {
                            img.src = src;
                            img.removeAttribute('data-src');
                            img.onload = () => {
                                img.style.opacity = '1';
                                img.classList.add('loaded');
                            };
                        }
                        imageObserver.unobserve(img);
                    }
                });
            }, { rootMargin: '50px' });
            
            dom.lazyImages.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            const lazyLoad = () => {
                dom.lazyImages.forEach(img => {
                    if (img.getBoundingClientRect().top <= window.innerHeight && 
                        img.getBoundingClientRect().bottom >= 0) {
                        const src = img.dataset.src;
                        if (src) {
                            img.src = src;
                            img.removeAttribute('data-src');
                            img.style.opacity = '1';
                            img.classList.add('loaded');
                        }
                    }
                });
            };
            window.addEventListener('scroll', throttle(lazyLoad, 100));
            window.addEventListener('resize', throttle(lazyLoad, 100));
            window.addEventListener('orientationchange', lazyLoad);
            lazyLoad();
        }
    };
    
    /**
     * Initialize form validation with water theme
     */
    const initFormValidation = () => {
        if (!dom.forms.length) return;
        
        const validateField = (field) => {
            let isValid = true;
            
            if (field.hasAttribute('required') && !field.value.trim()) {
                showFieldError(field, 'This field is required');
                isValid = false;
            } else if (field.type === 'email' && field.value && !isValidEmail(field.value)) {
                showFieldError(field, 'Please enter a valid email address');
                isValid = false;
            } else if (field.type === 'url' && field.value && !isValidUrl(field.value)) {
                showFieldError(field, 'Please enter a valid URL');
                isValid = false;
            } else if (field.type === 'password' && field.value && field.value.length < 8) {
                showFieldError(field, 'Password must be at least 8 characters');
                isValid = false;
            } else {
                clearFieldError(field);
            }
            
            return isValid;
        };
        
        const isValidEmail = (email) => {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        };
        
        const isValidUrl = (url) => {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        };
        
        const showFieldError = (field, message) => {
            field.classList.add('is-invalid');
            let feedback = field.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.insertBefore(feedback, field.nextSibling);
            }
            feedback.textContent = message;
        };
        
        const clearFieldError = (field) => {
            field.classList.remove('is-invalid');
            const feedback = field.nextElementSibling;
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.remove();
            }
        };
        
        dom.forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => validateField(input));
                input.addEventListener('input', debounce(() => {
                    if (input.classList.contains('is-invalid')) {
                        validateField(input);
                    }
                }, 300));
            });
            
            form.addEventListener('submit', (e) => {
                let isValid = true;
                inputs.forEach(input => {
                    if (!validateField(input)) isValid = false;
                });
                if (!isValid) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    };
    
    /**
     * Initialize newsletter form with AJAX
     */
    const initNewsletterForm = () => {
        if (!dom.newsletterForm) return;
        
        dom.newsletterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = dom.newsletterForm.querySelector('input[type="email"]').value;
            const submitBtn = dom.newsletterForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Subscribing...';
            
            try {
                const response = await fetch('/newsletter/subscribe/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ email })
                });
                
                const data = await response.json();
                showToast(data.message || 'Subscribed successfully! 🎉', 'success');
                dom.newsletterForm.reset();
            } catch (error) {
                console.error('Newsletter error:', error);
                showToast('Error subscribing. Please try again.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    };
    
    /**
     * Initialize search with debounce
     */
    const initSearch = () => {
        if (!dom.searchInput) return;
        
        const searchResults = document.getElementById('search-results');
        if (!searchResults) return;
        
        dom.searchInput.addEventListener('input', debounce(async (e) => {
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none';
                return;
            }
            
            try {
                const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.results && data.results.length) {
                    displaySearchResults(data.results);
                } else {
                    searchResults.innerHTML = '<div class="p-3 text-center text-muted">No results found</div>';
                    searchResults.style.display = 'block';
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        }, 300));
        
        const displaySearchResults = (results) => {
            searchResults.innerHTML = results.map(result => `
                <a href="${result.url}" class="search-result-item d-block p-3 text-decoration-none border-bottom" 
                   style="transition: background-color 0.2s ease;">
                    <div class="d-flex justify-content-between">
                        <strong style="color: var(--water-600);">${escapeHtml(result.title)}</strong>
                        <small class="text-muted">${result.type}</small>
                    </div>
                    <small class="text-muted">${escapeHtml(result.description.substring(0, 100))}...</small>
                </a>
            `).join('');
            searchResults.style.display = 'block';
        };
        
        document.addEventListener('click', (e) => {
            if (searchResults && !searchResults.contains(e.target) && e.target !== dom.searchInput) {
                searchResults.style.display = 'none';
            }
        });
    };
    
    /**
     * Initialize code copy buttons with water theme
     */
    const initCodeCopy = () => {
        if (!dom.codeBlocks.length) return;
        
        dom.codeBlocks.forEach(pre => {
            const button = document.createElement('button');
            button.className = 'copy-code-btn btn btn-sm btn-outline-primary position-absolute top-0 end-0 m-2';
            button.innerHTML = '<i class="far fa-copy me-1"></i> Copy';
            button.style.borderRadius = '8px';
            button.style.transition = 'all 0.3s ease';
            pre.style.position = 'relative';
            pre.appendChild(button);
            
            button.addEventListener('click', async () => {
                const code = pre.querySelector('code')?.innerText || pre.innerText;
                try {
                    await navigator.clipboard.writeText(code);
                    button.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-success');
                    setTimeout(() => {
                        button.innerHTML = '<i class="far fa-copy me-1"></i> Copy';
                        button.classList.remove('btn-success');
                        button.classList.add('btn-outline-primary');
                    }, 2000);
                } catch (err) {
                    console.error('Copy failed:', err);
                }
            });
        });
    };
    
    /**
     * Initialize smooth scroll for anchor links
     */
    const initSmoothScroll = () => {
        document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    };
    
    /**
     * Initialize password toggle visibility
     */
    const initPasswordToggle = () => {
        if (!dom.passwordToggles.length) return;
        
        dom.passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const input = this.closest('.input-group').querySelector('input[type="password"], input[type="text"]');
                if (input) {
                    const isPassword = input.type === 'password';
                    input.type = isPassword ? 'text' : 'password';
                    this.querySelector('i').className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
                }
            });
        });
    };
    
    /**
     * Initialize skill progress bars with animation
     */
    const initSkillProgress = () => {
        if (!dom.progressBars.length) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const targetWidth = bar.getAttribute('data-width') || bar.style.width || '0%';
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.width = targetWidth;
                        bar.style.transition = 'width 1.5s ease';
                    }, 200);
                    observer.unobserve(bar);
                }
            });
        }, { threshold: 0.5 });
        
        dom.progressBars.forEach(bar => observer.observe(bar));
    };
    
    /**
     * Initialize stat counters with animation
     */
    const initCounters = () => {
        if (!dom.counters.length) return;
        
        const animateCounter = (element) => {
            const target = parseInt(element.dataset.target || element.textContent.replace(/[^0-9]/g, ''));
            if (!target) return;
            
            const duration = 2000;
            const start = performance.now();
            
            const updateCounter = (currentTime) => {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                const value = Math.floor(progress * target);
                element.textContent = value.toLocaleString();
                
                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                } else {
                    element.textContent = target.toLocaleString();
                }
            };
            
            requestAnimationFrame(updateCounter);
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        dom.counters.forEach(counter => observer.observe(counter));
    };
    
    /**
     * Initialize project filters
     */
    const initProjectFilters = () => {
        if (!dom.projectFilters.length) return;
        
        dom.projectFilters.forEach(btn => {
            btn.addEventListener('click', function() {
                const filter = this.dataset.filter;
                const projects = document.querySelectorAll('.project-card');
                
                // Update active button
                dom.projectFilters.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                projects.forEach(project => {
                    if (filter === 'all' || project.dataset.category === filter) {
                        project.style.display = 'block';
                        setTimeout(() => {
                            project.style.opacity = '1';
                            project.style.transform = 'translateY(0)';
                        }, 50);
                    } else {
                        project.style.opacity = '0';
                        project.style.transform = 'translateY(20px)';
                        setTimeout(() => {
                            project.style.display = 'none';
                        }, 300);
                    }
                });
            });
        });
    };
    
    /**
     * Initialize tooltips
     */
    const initTooltips = () => {
        if (!dom.tooltips.length) return;
        dom.tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    };
    
    /**
     * Initialize dropdowns with animation
     */
    const initDropdowns = () => {
        if (!dom.dropdowns.length) return;
        
        dom.dropdowns.forEach(dropdown => {
            dropdown.addEventListener('shown.bs.dropdown', function() {
                const menu = this.nextElementSibling;
                if (menu) {
                    menu.style.animation = 'fadeInUp 0.3s ease forwards';
                }
            });
        });
    };
    
    /**
     * Performance monitoring
     */
    const initPerformanceMonitoring = () => {
        if ('performance' in window && window.performance.timing) {
            const timing = window.performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            if (loadTime > 3000) {
                console.warn(`[Performance] Page load time: ${loadTime}ms`);
            }
        }
    };
    
    /**
     * Handle service worker registration
     */
    const initServiceWorker = () => {
        if ('serviceWorker' in navigator && location.protocol === 'https:') {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                })
                .catch(error => {
                    console.warn('Service Worker registration failed:', error);
                });
        }
    };
    
    // ============================================
    // Initialize Everything
    // ============================================
    
    document.addEventListener('DOMContentLoaded', () => {
        initPageLoader();
        initThemeToggle();
        initNavbarScroll();
        initBackToTop();
        initAutoHideAlerts();
        initActiveNavHighlight();
        initLazyLoading();
        initFormValidation();
        initNewsletterForm();
        initSearch();
        initCodeCopy();
        initSmoothScroll();
        initPasswordToggle();
        initSkillProgress();
        initCounters();
        initProjectFilters();
        initTooltips();
        initDropdowns();
        initPerformanceMonitoring();
        initServiceWorker();
    });
    
    // Handle dynamic content loaded via AJAX
    document.addEventListener('ajax:complete', () => {
        initLazyLoading();
        initTooltips();
        initCodeCopy();
        initSkillProgress();
        initCounters();
    });
    
})();
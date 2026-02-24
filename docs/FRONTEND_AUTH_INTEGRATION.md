# Frontend Integration Guide - Authentication

This guide shows how to integrate the authentication API with your frontend application.

## Table of Contents

1. [JavaScript/React](#javascriptreact)
2. [Vue.js](#vuejs)
3. [Angular](#angular)
4. [Plain HTML + Fetch](#plain-html--fetch)

---

## JavaScript/React

### Option 1: Using React Hooks

**`hooks/useAuth.js`**
```javascript
import { useState, useCallback } from 'react';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'http://localhost:8000/api/auth';

  const signup = useCallback(async (username, email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Signup failed');
      }

      const data = await response.json();
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('token', data.access_token);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Login failed');
      }

      const data = await response.json();
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('token', data.access_token);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  }, []);

  const getHeaders = useCallback(() => {
    if (!token) return {};
    return { 'Authorization': `Bearer ${token}` };
  }, [token]);

  return {
    user,
    token,
    loading,
    error,
    signup,
    login,
    logout,
    getHeaders,
    isAuthenticated: !!token
  };
}
```

**`components/LoginForm.jsx`**
```jsx
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

export function LoginForm({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(username, password);
      onLoginSuccess?.();
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      
      {error && <div className="error">{error}</div>}
      
      <div>
        <label>Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      
      <div>
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

**`components/SignupForm.jsx`**
```jsx
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

export function SignupForm({ onSignupSuccess }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const { signup, loading, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    try {
      await signup(username, email, password);
      onSignupSuccess?.();
    } catch (err) {
      console.error('Signup failed:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Sign Up</h2>
      
      {error && <div className="error">{error}</div>}
      
      <div>
        <label>Username (min 3 chars):</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          minLength={3}
          required
        />
      </div>
      
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      
      <div>
        <label>Password (min 6 chars):</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength={6}
          required
        />
      </div>
      
      <div>
        <label>Confirm Password:</label>
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Creating account...' : 'Sign Up'}
      </button>
    </form>
  );
}
```

**`components/ProtectedPage.jsx`**
```jsx
import { useAuth } from '../hooks/useAuth';

export function ProtectedPage() {
  const { user, token, logout } = useAuth();

  if (!token) {
    return <div>Please log in first</div>;
  }

  return (
    <div>
      <h1>Welcome, {user?.username}!</h1>
      <p>Email: {user?.email}</p>
      <p>User ID: {user?.user_id}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

---

## Vue.js

**`composables/useAuth.js`**
```javascript
import { ref, computed } from 'vue';

export function useAuth() {
  const user = ref(null);
  const token = ref(localStorage.getItem('token'));
  const loading = ref(false);
  const error = ref(null);

  const API_URL = 'http://localhost:8000/api/auth';
  const isAuthenticated = computed(() => !!token.value);

  const signup = async (username, email, password) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`${API_URL}/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Signup failed');
      }

      const data = await response.json();
      token.value = data.access_token;
      user.value = data.user;
      localStorage.setItem('token', data.access_token);
      return data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const login = async (username, password) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Login failed');
      }

      const data = await response.json();
      token.value = data.access_token;
      user.value = data.user;
      localStorage.setItem('token', data.access_token);
      return data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
  };

  const getHeaders = () => {
    if (!token.value) return {};
    return { 'Authorization': `Bearer ${token.value}` };
  };

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    signup,
    login,
    logout,
    getHeaders
  };
}
```

**`components/LoginForm.vue`**
```vue
<template>
  <form @submit.prevent="handleLogin">
    <h2>Login</h2>
    
    <div v-if="error" class="error">{{ error }}</div>
    
    <div>
      <label>Username:</label>
      <input v-model="username" type="text" required />
    </div>
    
    <div>
      <label>Password:</label>
      <input v-model="password" type="password" required />
    </div>
    
    <button type="submit" :disabled="loading">
      {{ loading ? 'Logging in...' : 'Login' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import { useAuth } from '../composables/useAuth';

const username = ref('');
const password = ref('');
const emit = defineEmits(['loginSuccess']);
const { login, loading, error } = useAuth();

const handleLogin = async () => {
  try {
    await login(username.value, password.value);
    emit('loginSuccess');
  } catch (err) {
    console.error('Login failed:', err);
  }
};
</script>
```

---

## Angular

**`services/auth.service.ts`**
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';

interface User {
  user_id: number;
  username: string;
  email: string;
  created_at: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = 'http://localhost:8000/api/auth';
  private tokenSubject = new BehaviorSubject<string | null>(
    localStorage.getItem('token')
  );
  private userSubject = new BehaviorSubject<User | null>(null);

  token$ = this.tokenSubject.asObservable();
  user$ = this.userSubject.asObservable();

  constructor(private http: HttpClient) {}

  signup(username: string, email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API_URL}/signup`, {
      username,
      email,
      password
    }).pipe(
      tap(data => this.setAuth(data.access_token, data.user))
    );
  }

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API_URL}/login`, {
      username,
      password
    }).pipe(
      tap(data => this.setAuth(data.access_token, data.user))
    );
  }

  logout(): void {
    this.tokenSubject.next(null);
    this.userSubject.next(null);
    localStorage.removeItem('token');
  }

  getToken(): string | null {
    return this.tokenSubject.value;
  }

  private setAuth(token: string, user: User): void {
    this.tokenSubject.next(token);
    this.userSubject.next(user);
    localStorage.setItem('token', token);
  }
}
```

**`interceptors/auth.interceptor.ts`**
```typescript
import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}

  intercept(
    request: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();

    if (token) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return next.handle(request);
  }
}
```

---

## Plain HTML + Fetch

**`index.html`**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Auth API Demo</title>
  <style>
    body { font-family: Arial; max-width: 600px; margin: 50px auto; }
    form { border: 1px solid #ccc; padding: 20px; margin: 20px 0; }
    input { width: 100%; padding: 8px; margin: 5px 0 15px; }
    button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
    .error { color: red; margin-bottom: 10px; }
    .success { color: green; margin-bottom: 10px; }
    .user-info { border: 1px solid #4CAF50; padding: 15px; }
  </style>
</head>
<body>
  <div id="login-form">
    <h2>Login</h2>
    <form onsubmit="handleLogin(event)">
      <div class="error" id="login-error" style="display: none;"></div>
      <input type="text" id="login-username" placeholder="Username" required>
      <input type="password" id="login-password" placeholder="Password" required>
      <button type="submit">Login</button>
    </form>
  </div>

  <div id="signup-form">
    <h2>Sign Up</h2>
    <form onsubmit="handleSignup(event)">
      <div class="error" id="signup-error" style="display: none;"></div>
      <input type="text" id="signup-username" placeholder="Username" minlength="3" required>
      <input type="email" id="signup-email" placeholder="Email" required>
      <input type="password" id="signup-password" placeholder="Password" minlength="6" required>
      <input type="password" id="signup-confirm" placeholder="Confirm Password" required>
      <button type="submit">Sign Up</button>
    </form>
  </div>

  <div id="user-area" style="display: none;">
    <h2>Logged In</h2>
    <div id="user-info" class="user-info"></div>
    <button onclick="logout()">Logout</button>
  </div>

  <script>
    const API_URL = 'http://localhost:8000/api/auth';

    async function handleLogin(e) {
      e.preventDefault();
      const username = document.getElementById('login-username').value;
      const password = document.getElementById('login-password').value;
      const errorDiv = document.getElementById('login-error');

      try {
        const response = await fetch(`${API_URL}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
          throw new Error('Invalid credentials');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        showUserArea(data.user);
      } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
      }
    }

    async function handleSignup(e) {
      e.preventDefault();
      const username = document.getElementById('signup-username').value;
      const email = document.getElementById('signup-email').value;
      const password = document.getElementById('signup-password').value;
      const confirm = document.getElementById('signup-confirm').value;
      const errorDiv = document.getElementById('signup-error');

      if (password !== confirm) {
        errorDiv.textContent = 'Passwords do not match';
        errorDiv.style.display = 'block';
        return;
      }

      try {
        const response = await fetch(`${API_URL}/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password })
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail);
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        showUserArea(data.user);
      } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
      }
    }

    function showUserArea(user) {
      document.getElementById('login-form').style.display = 'none';
      document.getElementById('signup-form').style.display = 'none';
      document.getElementById('user-area').style.display = 'block';
      document.getElementById('user-info').innerHTML = `
        <p><strong>User ID:</strong> ${user.user_id}</p>
        <p><strong>Username:</strong> ${user.username}</p>
        <p><strong>Email:</strong> ${user.email}</p>
        <p><strong>Joined:</strong> ${new Date(user.created_at).toLocaleDateString()}</p>
      `;
    }

    function logout() {
      localStorage.removeItem('token');
      document.getElementById('login-form').style.display = 'block';
      document.getElementById('signup-form').style.display = 'block';
      document.getElementById('user-area').style.display = 'none';
      document.getElementById('login-username').value = '';
      document.getElementById('login-password').value = '';
    }

    // Check if already logged in
    const token = localStorage.getItem('token');
    if (token) {
      // Could fetch user info here
    }
  </script>
</body>
</html>
```

---

## Common Patterns

### Making Authenticated Requests

**JavaScript/Fetch:**
```javascript
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:8000/api/some-protected-endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Error Handling

```javascript
try {
  const response = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  if (response.status === 401) {
    throw new Error('Invalid username or password');
  }
  if (response.status === 400) {
    throw new Error('Missing username or password');
  }
  if (!response.ok) {
    throw new Error('Server error');
  }

  const data = await response.json();
  // Handle success
} catch (error) {
  console.error('Authentication failed:', error.message);
  // Show error to user
}
```

### Auto-logout on Token Expiry

```javascript
function checkTokenExpiry() {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiry = payload.exp * 1000;
      const now = Date.now();
      
      if (now > expiry) {
        localStorage.removeItem('token');
        // Redirect to login
      }
    } catch (e) {
      console.error('Invalid token format');
    }
  }
}

// Check on app load and periodically
checkTokenExpiry();
setInterval(checkTokenExpiry, 60000); // Every minute
```

---

## Testing

Use the Postman collection in `postman/Authentication_API.json` to test before integrating with your frontend.

Get a token from `/api/auth/login`:
```json
{
  "username": "john_doe",
  "password": "SecurePassword123"
}
```

Then use it in Postman:
1. Copy the `access_token` from response
2. Set the `{{access_token}}` variable in Postman
3. Requests automatically include it

---

## Security Tips

1. ✅ Store token in localStorage or sessionStorage (not localStorage for extra sensitivity)
2. ✅ Always use HTTPS in production
3. ✅ Include token in all API requests
4. ✅ Handle token expiration gracefully
5. ✅ Never log or display tokens
6. ✅ Clear token on logout
7. ✅ Validate token claims before trusting data

---

## Next Steps

- Deploy frontend to production
- Update `CORS_ORIGINS` for production domain
- Set up HTTPS
- Monitor authentication logs
- Implement refresh tokens (advanced)

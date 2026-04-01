import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Alert,
  SafeAreaView,
} from 'react-native';
import { authService } from '../services/authService';
import { styles } from '../styles/styles';

export default function LoginScreen({
  serverUrl,
  lanUrl,
  ngrokUrl,
  onServerUrlChange = () => {},
  onAuthSuccess,
}) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [currentServerUrl, setCurrentServerUrl] = useState(serverUrl || '');
  const [loading, setLoading] = useState(false);
  const [isLogin, setIsLogin] = useState(true); // true = login, false = register
  const [error, setError] = useState('');

  useEffect(() => {
    setCurrentServerUrl(serverUrl || '');
  }, [serverUrl]);

  const handleAuth = async () => {
    const normalizedServerUrl = (currentServerUrl || '').trim().replace(/\/+$/, '');

    if (!normalizedServerUrl) {
      setError('Server URL is required');
      return;
    }

    if (!username.trim() || !password.trim()) {
      setError('Username and password are required');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setError('');

    try {
      onServerUrlChange(normalizedServerUrl);

      const result = isLogin
        ? await authService.login(username, password, normalizedServerUrl)
        : await authService.register(username, password, normalizedServerUrl);

      if (result.success) {
        Alert.alert(
          isLogin ? 'Login Successful' : 'Registration Successful',
          'Welcome to Roger AI!',
          [{ text: 'OK', onPress: onAuthSuccess }]
        );
      } else {
        setError(result.message || (isLogin ? 'Login failed' : 'Registration failed'));
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <View style={styles.loginContainer}>
          <View style={styles.loginHeader}>
            <Text style={styles.loginTitle}>🤖 Roger AI</Text>
            <Text style={styles.loginSubtitle}>
              Your Strict Accountability Coach
            </Text>
          </View>

          <View style={styles.loginForm}>
            <View style={{ flexDirection: 'row', gap: 8, marginBottom: 8 }}>
              <TouchableOpacity
                style={{
                  flex: 1,
                  paddingVertical: 10,
                  borderRadius: 8,
                  borderWidth: 1,
                  borderColor: '#DDD',
                  backgroundColor: currentServerUrl === lanUrl ? '#F0F7FF' : '#FFF',
                }}
                disabled={loading || !lanUrl}
                onPress={() => setCurrentServerUrl(lanUrl || '')}
              >
                <Text style={{ textAlign: 'center', color: '#2A2A2A', fontWeight: '600' }}>LAN</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={{
                  flex: 1,
                  paddingVertical: 10,
                  borderRadius: 8,
                  borderWidth: 1,
                  borderColor: '#DDD',
                  backgroundColor: currentServerUrl === ngrokUrl ? '#F0F7FF' : '#FFF',
                }}
                disabled={loading || !ngrokUrl}
                onPress={() => setCurrentServerUrl(ngrokUrl || '')}
              >
                <Text style={{ textAlign: 'center', color: '#2A2A2A', fontWeight: '600' }}>ngrok</Text>
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.loginInput}
              placeholder="Server URL (es: http://192.168.1.56:8000)"
              placeholderTextColor="#999"
              value={currentServerUrl}
              onChangeText={setCurrentServerUrl}
              editable={!loading}
              autoCapitalize="none"
              autoCorrect={false}
            />

            {/* Username Input */}
            <TextInput
              style={styles.loginInput}
              placeholder="Username"
              placeholderTextColor="#999"
              value={username}
              onChangeText={setUsername}
              editable={!loading}
              autoCapitalize="none"
              autoComplete="username"
            />

            {/* Password Input */}
            <TextInput
              style={styles.loginInput}
              placeholder="Password"
              placeholderTextColor="#999"
              value={password}
              onChangeText={setPassword}
              editable={!loading}
              secureTextEntry
              autoCapitalize="none"
              autoComplete="password"
            />

            {/* Error Message */}
            {error ? (
              <Text style={styles.errorText}>⚠️ {error}</Text>
            ) : null}

            {/* Auth Button */}
            <TouchableOpacity
              style={[styles.authButton, loading && styles.authButtonDisabled]}
              onPress={handleAuth}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.authButtonText}>
                  {isLogin ? 'Login' : 'Register'}
                </Text>
              )}
            </TouchableOpacity>

            {/* Toggle Login/Register */}
            <View style={styles.toggleContainer}>
              <Text style={styles.toggleText}>
                {isLogin ? "Don't have an account? " : 'Already have an account? '}
              </Text>
              <TouchableOpacity
                onPress={() => {
                  setIsLogin(!isLogin);
                  setError('');
                }}
                disabled={loading}
              >
                <Text style={styles.toggleButton}>
                  {isLogin ? 'Register' : 'Login'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.loginFooter}>
            <Text style={styles.footerText}>
              🔒 Your data is private and secure
            </Text>
            <Text style={styles.footerText}>
              Each user has their own encrypted account
            </Text>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

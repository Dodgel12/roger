import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, KeyboardAvoidingView, ScrollView, Platform } from 'react-native';
import axios from 'axios';

const ReflectionScreen = ({ serverUrl, onSubmit }) => {
  const [wentWell, setWentWell] = useState('');
  const [slowedDown, setSlowedDown] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!wentWell.trim() || !slowedDown.trim()) {
      alert("Please fill out both fields.");
      return;
    }
    
    setLoading(true);
    try {
      await axios.post(`${serverUrl}/reflect`, {
        went_well: wentWell,
        slowed_down: slowedDown
      });
      setWentWell('');
      setSlowedDown('');
      if (onSubmit) onSubmit(); // redirect to chat
    } catch (err) {
      alert("Error saving reflection: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Weekly Reflection</Text>
        <Text style={styles.subtitle}>Help Roger understand your progress.</Text>
        
        <Text style={styles.label}>What went well this week?</Text>
        <TextInput
          style={styles.textArea}
          value={wentWell}
          onChangeText={setWentWell}
          placeholder="e.g., I consistently coded for 2 hours..."
          placeholderTextColor="#999"
          multiline
        />

        <Text style={styles.label}>What slowed you down?</Text>
        <TextInput
          style={styles.textArea}
          value={slowedDown}
          onChangeText={setSlowedDown}
          placeholder="e.g., I got distracted by social media..."
          placeholderTextColor="#999"
          multiline
        />

        <TouchableOpacity 
          style={[styles.submitBtn, (!wentWell.trim() || !slowedDown.trim()) && styles.disabledBtn]} 
          onPress={handleSubmit}
          disabled={loading || !wentWell.trim() || !slowedDown.trim()}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitBtnText}>Submit & Discuss with Roger</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollContent: {
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 32,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  textArea: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#333',
    minHeight: 120,
    textAlignVertical: 'top',
    marginBottom: 24,
  },
  submitBtn: {
    backgroundColor: '#000',
    borderRadius: 30,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  disabledBtn: {
    backgroundColor: '#ccc',
  },
  submitBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  }
});

export default ReflectionScreen;

import React from 'react';
import { View, TextInput, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { styles } from '../styles/styles';

const ChatInput = ({ message, setMessage, sendMessage, loading }) => (
  <View style={styles.inputContainer}>
    <TextInput
      style={styles.input}
      value={message}
      onChangeText={setMessage}
      placeholder="Message Roger..."
      placeholderTextColor="#999"
      multiline
    />
    <TouchableOpacity 
      style={[styles.sendButton, !message.trim() && styles.sendButtonDisabled]} 
      onPress={sendMessage}
      disabled={loading || !message.trim()}
    >
      <Ionicons name="arrow-up" size={24} color="white" />
    </TouchableOpacity>
  </View>
);

export default ChatInput;

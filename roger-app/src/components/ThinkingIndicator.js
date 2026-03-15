import React from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { styles } from '../styles/styles';

const ThinkingIndicator = () => (
  <View style={styles.thinkingContainer}>
    <ActivityIndicator size="small" color="#666" />
    <Text style={styles.thinkingText}>Roger is thinking...</Text>
  </View>
);

export default ThinkingIndicator;

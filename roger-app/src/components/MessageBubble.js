import React from 'react';
import { View, Text } from 'react-native';
import { styles } from '../styles/styles';

const MessageBubble = ({ role, text, time }) => {
  const isUser = role === 'user';
  return (
    <View style={[styles.messageWrapper, isUser ? styles.userWrapper : styles.rogerWrapper]}>
      <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.rogerBubble]}>
        <Text style={[styles.messageText, isUser ? styles.userText : styles.rogerText]}>{text}</Text>
        <Text style={[styles.timeText, isUser ? styles.userTimeText : styles.rogerTimeText]}>
          {new Date(time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    </View>
  );
};

export default MessageBubble;

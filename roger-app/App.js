import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Platform,
  SafeAreaView,
  KeyboardAvoidingView,
  FlatList,
  StatusBar
} from "react-native";
import axios from "axios";
import * as Notifications from "expo-notifications";
import * as Network from 'expo-network';

// Custom imports
import { styles } from "./src/styles/styles";
import { configureNotifications, registerForPushNotificationsAsync } from "./src/services/notificationService";
import Header from "./src/components/Header";
import MessageBubble from "./src/components/MessageBubble";
import ChatInput from "./src/components/ChatInput";
import ThinkingIndicator from "./src/components/ThinkingIndicator";

// Initialize notification configuration
configureNotifications();

export default function App() {
  const [serverUrl, setServerUrl] = useState("https://subporphyritic-venomless-delores.ngrok-free.dev");
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef();
  const notificationListener = useRef();

  useEffect(() => {
    const initializeNetworkAndPush = async () => {
      let currentServerUrl = "https://subporphyritic-venomless-delores.ngrok-free.dev";
      try {
        const networkState = await Network.getNetworkStateAsync();
        setServerUrl(currentServerUrl);
      } catch (err) {
        console.warn("Network check failed", err);
      }

      const token = await registerForPushNotificationsAsync();
      if (token) {
        axios.post(`${currentServerUrl}/register-push-token`, { token })
          .catch(err => console.error("Error registering token:", err));
      }
    };

    initializeNetworkAndPush();

    notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
      // Potentially refresh chat here if notifications contain message data
    });

    return () => {
      if (notificationListener.current) {
        Notifications.removeNotificationSubscription(notificationListener.current);
      }
    };
  }, []);

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userMessage = message;
    const timestamp = new Date();
    setChat(prev => [...prev, { role: "user", text: userMessage, time: timestamp }]);
    setMessage("");
    setLoading(true);

    // Add placeholder for Roger's response
    setChat(prev => [...prev, { role: "roger", text: "", time: new Date() }]);

    try {
      const response = await axios.post(`${serverUrl}/chat`, { message: userMessage });
      const finalText = response.data.response;

      // Fake streaming effect for visual flair
      let currentText = "";
      for (let i = 0; i < finalText.length; i += 15) {
        currentText = finalText.slice(0, i + 15);
        setChat(prev => {
          const updated = [...prev];
          updated[updated.length - 1].text = currentText;
          return updated;
        });
        await new Promise(r => setTimeout(r, 20));
      }

    } catch (err) {
      setChat(prev => {
        const updated = [...prev];
        updated[updated.length - 1].text = `Roger is unavailable right now.\n\nDebug: ${err.message} (${serverUrl})`;
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" />
      <Header />

      <KeyboardAvoidingView 
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardView}
        keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={chat}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => <MessageBubble {...item} />}
          contentContainerStyle={styles.chatList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
        />

        {loading && chat[chat.length - 1]?.text === "" && <ThinkingIndicator />}

        <ChatInput 
          message={message} 
          setMessage={setMessage} 
          sendMessage={sendMessage} 
          loading={loading} 
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
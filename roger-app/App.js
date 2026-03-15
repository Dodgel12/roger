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
import TasksScreen from "./src/components/TasksScreen";
import { TouchableOpacity, Text } from "react-native";

// Initialize notification configuration
configureNotifications();

export default function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [serverUrl, setServerUrl] = useState("https://subporphyritic-venomless-delores.ngrok-free.dev");
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef();
  const notificationListener = useRef();
  const tapListener = useRef();

  const loadChatHistory = async (url) => {
    try {
      const res = await axios.get(`${url}/messages?limit=100`);
      const history = res.data.map(msg => ({
        role: msg.role,
        text: msg.content,
        time: new Date(msg.time),
      }));
      setChat(history);
    } catch (err) {
      console.warn("Could not load chat history:", err.message);
    }
  };

  useEffect(() => {
    const currentServerUrl = "https://subporphyritic-venomless-delores.ngrok-free.dev";

    const initializeNetworkAndPush = async () => {
      try {
        await Network.getNetworkStateAsync();
        setServerUrl(currentServerUrl);
      } catch (err) {
        console.warn("Network check failed", err);
      }

      // Load persisted chat history
      await loadChatHistory(currentServerUrl);

      const token = await registerForPushNotificationsAsync();
      if (token) {
        axios.post(`${currentServerUrl}/register-push-token`, { token })
          .catch(err => console.error("Error registering token:", err));
      }
    };

    initializeNetworkAndPush();

    // Refresh chat when a push notification arrives
    notificationListener.current = Notifications.addNotificationReceivedListener(() => {
      loadChatHistory(currentServerUrl);
    });

    // Refresh chat when user taps a notification
    tapListener.current = Notifications.addNotificationResponseReceivedListener(() => {
      loadChatHistory(currentServerUrl);
    });

    return () => {
      if (notificationListener.current) {
        Notifications.removeNotificationSubscription(notificationListener.current);
      }
      if (tapListener.current) {
        Notifications.removeNotificationSubscription(tapListener.current);
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

      {activeTab === "chat" ? (
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
      ) : (
        <TasksScreen serverUrl={serverUrl} />
      )}

      <View style={styles.tabBar}>
        <TouchableOpacity 
          style={styles.tabItem} 
          onPress={() => setActiveTab("chat")}
        >
          <Text style={[styles.tabText, activeTab === "chat" && styles.tabTextActive]}>💬 Chat</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.tabItem} 
          onPress={() => setActiveTab("tasks")}
        >
          <Text style={[styles.tabText, activeTab === "tasks" && styles.tabTextActive]}>✅ Tasks</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}
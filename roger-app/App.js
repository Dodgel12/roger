import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Platform,
  KeyboardAvoidingView,
  FlatList,
  StatusBar,
  ActivityIndicator
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import * as Notifications from "expo-notifications";
import * as Network from 'expo-network';

// Custom imports
import { styles } from "./src/styles/styles";
import { configureNotifications, registerForPushNotificationsAsync, setupNotificationListeners } from "./src/services/notificationService";
import { authService, createAuthenticatedClient } from "./src/services/authService";
import Header from "./src/components/Header";
import MessageBubble from "./src/components/MessageBubble";
import ChatInput from "./src/components/ChatInput";
import ThinkingIndicator from "./src/components/ThinkingIndicator";
import TasksScreen from "./src/components/TasksScreen";
import EnhancedReflectionScreen from "./src/components/EnhancedReflectionScreen";
import WeeklyReportScreen from "./src/components/WeeklyReportScreen";
import SkillsScreen from "./src/components/SkillsScreen";
import LoginScreen from "./src/components/LoginScreen";
import TaskCreationModal from "./src/components/TaskCreationModal";
import { TouchableOpacity, Text } from "react-native";

// Initialize notification configuration
configureNotifications();

export default function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [serverUrl, setServerUrl] = useState("https://subporphyritic-venomless-delores.ngrok-free.dev");
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef();
  const notificationListener = useRef();
  const tapListener = useRef();
  const cleanupNotifications = useRef(null);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const authenticated = await authService.isAuthenticated();
        setIsAuthenticated(authenticated);
        if (authenticated) {
          // Initialize push notifications
          initializePushNotifications();
        }
      } catch (err) {
        console.error("Auth check failed:", err);
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuth();
  }, []);

  // Initialize push notifications
  const initializePushNotifications = async () => {
    try {
      const currentServerUrl = serverUrl;
      
      // Check network
      await Network.getNetworkStateAsync();

      // Load initial chat history
      await loadChatHistory(currentServerUrl);

      // Register for push notifications
      const token = await registerForPushNotificationsAsync();
      if (token) {
        try {
          const authToken = await authService.getToken();
          console.log("Token available for push registration:", !!authToken);
          
          const client = await createAuthenticatedClient(currentServerUrl);
          await client.post("/register-push-token", { token });
          console.log("✅ Push token registered successfully");
        } catch (err) {
          if (err.response?.status === 401) {
            console.error("❌ Push token registration failed - Authentication error (401). Token may be invalid or expired.");
          } else {
            console.error("Error registering push token:", err.message);
          }
        }
      } else {
        console.log("No push token obtained from Expo");
      }

      // Setup notification listeners
      cleanupNotifications.current = setupNotificationListeners();

      // Listen for notifications
      notificationListener.current = Notifications.addNotificationReceivedListener(() => {
        loadChatHistory(currentServerUrl);
      });

      tapListener.current = Notifications.addNotificationResponseReceivedListener(() => {
        loadChatHistory(currentServerUrl);
      });

    } catch (err) {
      console.warn("Push notification initialization failed:", err);
    }
  };

  // Load chat history from server
  const loadChatHistory = async (url) => {
    try {
      const token = await authService.getToken();
      if (!token) {
        console.warn("No token found - user may not be authenticated");
        return;
      }
      const client = await createAuthenticatedClient(url);
      const res = await client.get("/messages?limit=100");
      const messages = res.data.messages;
      
      const history = messages.map(msg => ({
        role: msg.role,
        text: msg.content,
        time: new Date(msg.time),
      }));
      setChat(history);
    } catch (err) {
      console.warn("Could not load chat history:", err.message);
      if (err.response?.status === 401) {
        console.error("Auth failed - Token may be expired or invalid");
      }
    }
  };

  // Handle successful authentication
  const handleAuthSuccess = async () => {
    setIsAuthenticated(true);
    initializePushNotifications();
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      const currentServerUrl = serverUrl;
      const client = await createAuthenticatedClient(currentServerUrl);
      
      try {
        await client.post("/auth/logout");
      } catch (err) {
        console.log("Logout API call failed (token may be invalid)");
      }

      // Clear local storage
      await authService.logout();
      
      // Clear notifications
      if (cleanupNotifications.current) {
        cleanupNotifications.current();
      }
      if (notificationListener.current) {
        Notifications.removeNotificationSubscription(notificationListener.current);
      }
      if (tapListener.current) {
        Notifications.removeNotificationSubscription(tapListener.current);
      }

      // Reset state
      setIsAuthenticated(false);
      setChat([]);
      setMessage("");
      setActiveTab("chat");
    } catch (err) {
      console.error("Logout error:", err);
    }
  };

  // Send message to Roger
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
      const client = await createAuthenticatedClient(serverUrl);
      const response = await client.post("/chat", { message: userMessage });
      const finalText = response.data.response;

      // Streaming effect
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
      const errorMessage = err.response?.data?.detail || err.message || "Unknown error";
      setChat(prev => {
        const updated = [...prev];
        updated[updated.length - 1].text = `Error: ${errorMessage}`;
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  // Show loading screen while checking auth
  if (isCheckingAuth) {
    return (
      <SafeAreaView style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#F8F9FA" }}>
        <ActivityIndicator size="large" color="#1A1A1A" />
        <Text style={{ marginTop: 16, color: "#666", fontSize: 14 }}>Initializing Roger...</Text>
      </SafeAreaView>
    );
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <LoginScreen serverUrl={serverUrl} onAuthSuccess={handleAuthSuccess} />;
  }

  // Main app view
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" />
      <Header onLogout={handleLogout} />

      {activeTab === "chat" && (
        <KeyboardAvoidingView 
          behavior={Platform.OS === "ios" ? "padding" : "height"}
          style={styles.keyboardView}
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
      )}
      {activeTab === "tasks" && (
        <TasksScreen 
          serverUrl={serverUrl} 
          createAuthenticatedClient={createAuthenticatedClient}
          onCreateTask={() => setShowTaskModal(true)}
          onTaskCreated={() => {
            // Refresh tasks
            loadChatHistory(serverUrl);
          }}
        />
      )}
      {activeTab === "reflect" && (
        <EnhancedReflectionScreen 
          serverUrl={serverUrl} 
          createAuthenticatedClient={createAuthenticatedClient}
          onSubmit={() => {
            setActiveTab("chat");
            loadChatHistory(serverUrl);
          }} 
        />
      )}
      {activeTab === "report" && (
        <WeeklyReportScreen 
          serverUrl={serverUrl}
          createAuthenticatedClient={createAuthenticatedClient}
        />
      )}
      {activeTab === "skills" && (
        <SkillsScreen 
          serverUrl={serverUrl}
          createAuthenticatedClient={createAuthenticatedClient}
        />
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
        
        <TouchableOpacity 
          style={styles.tabItem} 
          onPress={() => setActiveTab("reflect")}
        >
          <Text style={[styles.tabText, activeTab === "reflect" && styles.tabTextActive]}>🧠 Reflect</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.tabItem} 
          onPress={() => setActiveTab("report")}
        >
          <Text style={[styles.tabText, activeTab === "report" && styles.tabTextActive]}>📊 Report</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.tabItem} 
          onPress={() => setActiveTab("skills")}
        >
          <Text style={[styles.tabText, activeTab === "skills" && styles.tabTextActive]}>🎯 Skills</Text>
        </TouchableOpacity>
      </View>

      <TaskCreationModal
        visible={showTaskModal}
        onClose={() => setShowTaskModal(false)}
        serverUrl={serverUrl}
        createAuthenticatedClient={createAuthenticatedClient}
        onTaskCreated={() => loadChatHistory(serverUrl)}
      />
    </SafeAreaView>
  );
}
import React, { useState, useEffect, useRef } from "react";
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  Platform,
  SafeAreaView,
  KeyboardAvoidingView,
  FlatList,
  StatusBar
} from "react-native";
import axios from "axios";
import * as Notifications from "expo-notifications";
import Constants from "expo-constants";
import { Ionicons } from '@expo/vector-icons';
import * as Network from 'expo-network';

// Notification configuration
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

async function registerForPushNotificationsAsync() {
  let token;
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
    });
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== 'granted') {
    return;
  }

  try {
    const projectId = Constants?.expoConfig?.extra?.eas?.projectId ?? Constants?.easConfig?.projectId;
    if (!projectId) {
      console.error('Project ID not found');
      return;
    }
    token = (await Notifications.getExpoPushTokenAsync({ projectId })).data;
  } catch (e) {
    console.error("Error getting push token:", e);
  }

  return token;
}

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

export default function App() {
  const [serverUrl, setServerUrl] = useState("https://subporphyritic-venomless-delores.ngrok-free.dev");

  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef();
  
  const notificationListener = useRef();
  const responseListener = useRef();

  useEffect(() => {
    const initializeNetworkAndPush = async () => {
      let currentServerUrl = "https://subporphyritic-venomless-delores.ngrok-free.dev";
      try {
        const networkState = await Network.getNetworkStateAsync();
        
        // If the phone is on Mobile Data / Internet (not local WiFi), switch to a public URL.
        // NOTE: Commented out because "https://your-public-api-url.com" is just a placeholder, 
        // and sometimes physical devices incorrectly report connected network type.
        // if (networkState.type === Network.NetworkStateType.CELLULAR || networkState.type !== Network.NetworkStateType.WIFI) {
        //   currentServerUrl = "https://your-public-api-url.com"; // Replace with real public URL!
        // }
        
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
      Notifications.removeNotificationSubscription(notificationListener.current);
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
      <View style={styles.header}>
        <Text style={styles.headerTitle}>ROGER</Text>
        <View style={styles.statusDot} />
      </View>

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

        {loading && chat[chat.length - 1]?.text === "" && (
          <View style={styles.thinkingContainer}>
            <ActivityIndicator size="small" color="#666" />
            <Text style={styles.thinkingText}>Roger is thinking...</Text>
          </View>
        )}

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
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#F8F9FA" },
  header: {
    height: 60,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    borderBottomWidth: 1,
    borderBottomColor: "#EEE",
    backgroundColor: "#FFF"
  },
  headerTitle: { fontSize: 18, fontWeight: "800", letterSpacing: 2, color: "#1A1A1A" },
  statusDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: "#4CAF50", marginLeft: 8, marginTop: 2 },
  keyboardView: { flex: 1 },
  chatList: { paddingHorizontal: 16, paddingVertical: 20, paddingBottom: 10 },
  
  messageWrapper: { marginBottom: 16, width: "100%", flexDirection: "row" },
  userWrapper: { justifyContent: "flex-end" },
  rogerWrapper: { justifyContent: "flex-start" },
  
  messageBubble: {
    maxWidth: "80%",
    padding: 12,
    borderRadius: 20,
    elevation: 1,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  userBubble: {
    backgroundColor: "#1A1A1A",
    borderBottomRightRadius: 4,
  },
  rogerBubble: {
    backgroundColor: "#FFF",
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: "#E0E0E0",
  },
  
  messageText: { fontSize: 16, lineHeight: 22 },
  userText: { color: "#FFF" },
  rogerText: { color: "#1A1A1A" },
  
  timeText: { fontSize: 10, marginTop: 4, alignSelf: "flex-end" },
  userTimeText: { color: "rgba(255,255,255,0.6)" },
  rogerTimeText: { color: "#999" },
  
  thinkingContainer: { flexDirection: "row", alignItems: "center", paddingHorizontal: 20, marginBottom: 10 },
  thinkingText: { marginLeft: 8, color: "#666", fontSize: 14, fontStyle: "italic" },
  
  inputContainer: {
    flexDirection: "row",
    alignItems: "flex-end",
    padding: 12,
    backgroundColor: "#FFF",
    borderTopWidth: 1,
    borderTopColor: "#EEE",
  },
  input: {
    flex: 1,
    minHeight: 40,
    maxHeight: 120,
    backgroundColor: "#F1F3F5",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingTop: 10,
    paddingBottom: 10,
    fontSize: 16,
    color: "#1A1A1A",
    marginRight: 10,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#1A1A1A",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 2,
  },
  sendButtonDisabled: {
    backgroundColor: "#CCC",
  }
});
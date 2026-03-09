import React, { useState } from "react";
import {
  View,
  TextInput,
  Button,
  Text,
  StyleSheet,
  ActivityIndicator
} from "react-native";
import axios from "axios";
import { KeyboardAwareScrollView } from "react-native-keyboard-aware-scroll-view";

export default function App() {
  const SERVER = "http://192.168.1.56:8000";

  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message || loading) return;

    const userMessage = message;
    setChat(prev => [...prev, { role: "user", text: userMessage, time: new Date() }]);
    setMessage("");
    setLoading(true);

    let rogerText = "";
    setChat(prev => [...prev, { role: "roger", text: rogerText, time: new Date() }]);

    try {
      const response = await axios.post(`${SERVER}/chat`, { message: userMessage });
      const finalText = response.data.response;

      // Fake streaming effect
      for (let i = 0; i < finalText.length; i += 15) {
        rogerText = finalText.slice(0, i + 15);
        setChat(prev => {
          const updated = [...prev];
          updated[updated.length - 1].text = rogerText;
          return updated;
        });
        await new Promise(r => setTimeout(r, 50));
      }

      // No notifications for now

    } catch (err) {
      setChat(prev => {
        const updated = [...prev];
        updated[updated.length - 1].text = "Roger is unavailable right now.";
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAwareScrollView style={styles.container}>
      {chat.map((m, i) => (
        <Text
          key={i}
          style={[styles.message, m.role === "user" ? styles.user : styles.roger]}
        >
          {m.role === "user" ? "You" : "Roger"}: {m.text}
        </Text>
      ))}
      {loading && (
        <View style={styles.loading}>
          <ActivityIndicator size="small" />
          <Text style={{ marginLeft: 8 }}>Roger is thinking...</Text>
        </View>
      )}
      <TextInput
        style={styles.input}
        value={message}
        onChangeText={setMessage}
        placeholder="Message Roger..."
      />
      <Button title={loading ? "Waiting..." : "Send"} onPress={sendMessage} disabled={loading} />
    </KeyboardAwareScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  message: { marginBottom: 10, padding: 10, borderRadius: 5 },
  user: { backgroundColor: "#DCF8C6", alignSelf: "flex-end" },
  roger: { backgroundColor: "#F0F0F0", alignSelf: "flex-start" },
  input: { borderWidth: 1, padding: 10, marginBottom: 10, borderRadius: 5 },
  loading: { flexDirection: "row", alignItems: "center", marginTop: 5 }
});
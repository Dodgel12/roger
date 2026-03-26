import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { styles } from "../styles/styles";

export default function EnhancedReflectionScreen({ serverUrl, createAuthenticatedClient, onSubmit }) {
  const [reflections, reflectionHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [wentWell, setWentWell] = useState("");
  const [slowedDown, setSlowedDown] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [recentFeedback, setRecentFeedback] = useState("");

  // Load past reflections on mount
  useEffect(() => {
    loadReflections();
  }, []);

  const loadReflections = async () => {
    try {
      setLoading(true);
      const client = await createAuthenticatedClient(serverUrl);
      // Note: This would require a new GET /reflections endpoint
      // For now, we load from chat history which includes reflection feedback
    } catch (err) {
      console.warn("Error loading reflections:", err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!wentWell.trim() || !slowedDown.trim()) {
      Alert.alert("❌ Error", "Please answer both reflection questions");
      return;
    }

    try {
      setSubmitting(true);
      const client = await createAuthenticatedClient(serverUrl);
      const response = await client.post("/reflect", {
        went_well: wentWell,
        slowed_down: slowedDown,
      });

      if (response.data.status === "success") {
        setRecentFeedback(response.data.response);
        // Clear form
        setWentWell("");
        setSlowedDown("");
        
        Alert.alert("✅ Reflection Saved", "Roger has analyzed your week!")
        
        // Call callback after brief delay
        setTimeout(() => {
          if (onSubmit) onSubmit();
        }, 1000);
      }
    } catch (err) {
      Alert.alert("❌ Error", err.response?.data?.detail || err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🧠 Weekly Reflection</Text>
        
        {/* Reflection Prompt Cards */}
        <View style={[styles.card, { backgroundColor: "#F0FFF4", marginBottom: 16 }]}>
          <Text style={{ fontSize: 14, fontWeight: "600", color: "#1A1A1A", marginBottom: 12 }}>
            ✅ What went well this week?
          </Text>
          <TextInput
            style={[
              styles.textInput,
              {
                minHeight: 100,
                paddingTop: 12,
                textAlignVertical: "top",
              },
            ]}
            multiline
            placeholder="E.g., I crushed my morning coding sessions..."
            placeholderTextColor="#999"
            value={wentWell}
            onChangeText={setWentWell}
            editable={!submitting}
          />
          <Text style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
            {wentWell.length}/500 characters
          </Text>
        </View>

        <View style={[styles.card, { backgroundColor: "#FFF5F5", marginBottom: 16 }]}>
          <Text style={{ fontSize: 14, fontWeight: "600", color: "#1A1A1A", marginBottom: 12 }}>
            📉 What slowed you down?
          </Text>
          <TextInput
            style={[
              styles.textInput,
              {
                minHeight: 100,
                paddingTop: 12,
                textAlignVertical: "top",
              },
            ]}
            multiline
            placeholder="E.g., I missed Guitar practice 3 days in a row..."
            placeholderTextColor="#999"
            value={slowedDown}
            onChangeText={setSlowedDown}
            editable={!submitting}
          />
          <Text style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
            {slowedDown.length}/500 characters
          </Text>
        </View>

        {/* Submit Button */}
        <TouchableOpacity
          style={[styles.button, { marginBottom: 24 }]}
          onPress={handleSubmit}
          disabled={submitting || !wentWell.trim() || !slowedDown.trim()}
        >
          {submitting ? (
            <ActivityIndicator size="small" color="#FFF" />
          ) : (
            <Text style={styles.buttonText}>📤 Submit Reflection</Text>
          )}
        </TouchableOpacity>

        {/* Recent Feedback */}
        {recentFeedback ? (
          <View style={[styles.card, { backgroundColor: "#FAFAFA", marginBottom: 24 }]}>
            <Text style={{ fontSize: 12, color: "#666", marginBottom: 12, fontWeight: "600" }}>
              🤖 Roger's Coaching
            </Text>
            <Text style={{ fontSize: 14, color: "#1A1A1A", lineHeight: 22 }}>
              {recentFeedback}
            </Text>
          </View>
        ) : null}

        {/* Tips Section */}
        <View style={[styles.card, { backgroundColor: "#EBF8FF", borderLeftWidth: 4, borderLeftColor: "#3182CE" }]}>
          <Text style={{ fontSize: 13, fontWeight: "600", color: "#1A1A1A", marginBottom: 12 }}>
            💡 Reflection Tips
          </Text>
          <Text style={{ fontSize: 12, color: "#2D3748", lineHeight: 18, marginBottom: 10 }}>
            • Be specific. Name habits, not feelings.
          </Text>
          <Text style={{ fontSize: 12, color: "#2D3748", lineHeight: 18, marginBottom: 10 }}>
            • Focus on what you controlled.
          </Text>
          <Text style={{ fontSize: 12, color: "#2D3748", lineHeight: 18, marginBottom: 10 }}>
            • Identify patterns, not excuses.
          </Text>
          <Text style={{ fontSize: 12, color: "#2D3748", lineHeight: 18 }}>
            • Use this for next week's improvement.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

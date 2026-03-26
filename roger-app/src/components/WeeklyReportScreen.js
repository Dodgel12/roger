import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { styles } from "../styles/styles";

export default function WeeklyReportScreen({ serverUrl, createAuthenticatedClient }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Load report on mount
  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      setLoading(true);
      const client = await createAuthenticatedClient(serverUrl);
      const response = await client.get("/reports/weekly");

      if (response.data.status === "success") {
        setReport(response.data.report);
      } else {
        setReport(null);
      }
    } catch (err) {
      console.warn("Error loading report:", err.message);
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setGenerating(true);
      const client = await createAuthenticatedClient(serverUrl);
      const response = await client.post("/reports/weekly-generate", {});

      if (response.data.status === "success") {
        setReport(response.data.report);
        Alert.alert("✅ Report Generated", "Your weekly report has been created!");
      }
    } catch (err) {
      Alert.alert("❌ Error", err.response?.data?.detail || err.message);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: "center", alignItems: "center" }]}>
        <ActivityIndicator size="large" color="#1A1A1A" />
        <Text style={{ marginTop: 16, color: "#666", fontSize: 14 }}>Loading report...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Weekly Report</Text>

        {report ? (
          <>
            {/* Report Header */}
            <View
              style={[
                styles.card,
                {
                  backgroundColor: "#F0F7FF",
                  borderLeftWidth: 4,
                  borderLeftColor: "#4A90E2",
                },
              ]}
            >
              <Text style={{ fontSize: 12, color: "#666", marginBottom: 8 }}>
                {report.start_date} to {report.end_date}
              </Text>
              <Text style={{ fontSize: 32, fontWeight: "bold", color: "#1A1A1A" }}>
                {report.completion_pct}%
              </Text>
              <Text style={{ fontSize: 14, color: "#666", marginTop: 4 }}>
                Overall Completion
              </Text>
            </View>

            {/* Best & Weakest Habits */}
            <View style={{ marginTop: 16, gap: 12 }}>
              <View
                style={[
                  styles.card,
                  {
                    backgroundColor: "#F0FFF4",
                    borderLeftWidth: 4,
                    borderLeftColor: "#48BB78",
                  },
                ]}
              >
                <Text style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>🏆 Best Habit</Text>
                <Text style={{ fontSize: 16, fontWeight: "bold", color: "#1A1A1A" }}>
                  {report.best_habit}
                </Text>
              </View>

              <View
                style={[
                  styles.card,
                  {
                    backgroundColor: "#FFF5F5",
                    borderLeftWidth: 4,
                    borderLeftColor: "#F56565",
                  },
                ]}
              >
                <Text style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>
                  📈 Opportunity Area
                </Text>
                <Text style={{ fontSize: 16, fontWeight: "bold", color: "#1A1A1A" }}>
                  {report.weakest_habit}
                </Text>
              </View>
            </View>

            {/* AI Analysis */}
            <View style={[styles.card, { marginTop: 16, backgroundColor: "#FAFAFA" }]}>
              <Text style={{ fontSize: 12, color: "#666", marginBottom: 12, fontWeight: "600" }}>
                🤖 Roger's Analysis
              </Text>
              <Text style={{ fontSize: 14, color: "#1A1A1A", lineHeight: 22 }}>
                {report.ai_advice}
              </Text>
            </View>

            {/* Generate New Report Button */}
            <TouchableOpacity
              style={[styles.button, { marginTop: 20 }]}
              onPress={handleGenerateReport}
              disabled={generating}
            >
              {generating ? (
                <ActivityIndicator size="small" color="#FFF" />
              ) : (
                <Text style={styles.buttonText}>📋 Generate New Report</Text>
              )}
            </TouchableOpacity>
          </>
        ) : (
          <>
            {/* No Report Message */}
            <View style={[styles.card, { alignItems: "center", paddingVertical: 32 }]}>
              <Text style={{ fontSize: 48, marginBottom: 12 }}>📊</Text>
              <Text style={{ fontSize: 16, fontWeight: "bold", color: "#1A1A1A", marginBottom: 8 }}>
                No Weekly Report Yet
              </Text>
              <Text
                style={{
                  fontSize: 14,
                  color: "#666",
                  textAlign: "center",
                  marginBottom: 20,
                }}
              >
                Generate your first weekly report to see your progress, habits, and AI coaching.
              </Text>
              <TouchableOpacity
                style={styles.button}
                onPress={handleGenerateReport}
                disabled={generating}
              >
                {generating ? (
                  <ActivityIndicator size="small" color="#FFF" />
                ) : (
                  <Text style={styles.buttonText}>🚀 Generate First Report</Text>
                )}
              </TouchableOpacity>
            </View>
          </>
        )}
      </View>
    </ScrollView>
  );
}

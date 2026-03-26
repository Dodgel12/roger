import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  FlatList,
  TextInput,
} from "react-native";
import { styles } from "../styles/styles";

export default function SkillsScreen({ serverUrl, createAuthenticatedClient }) {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingSkills, setLoadingSkills] = useState(new Set());
  const [showAddSkill, setShowAddSkill] = useState(false);
  const [newSkillName, setNewSkillName] = useState("");
  const [creating, setCreating] = useState(false);

  // Load skills on mount and when screen is focused
  useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = async () => {
    try {
      setLoading(true);
      const client = await createAuthenticatedClient(serverUrl);
      const response = await client.get("/skills");

      if (response.data.status === "success") {
        setSkills(response.data.skills);
      }
    } catch (err) {
      console.warn("Error loading skills:", err.message);
      Alert.alert("❌ Error", "Failed to load skills");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSkill = async () => {
    if (!newSkillName.trim()) {
      Alert.alert("❌ Error", "Skill name cannot be empty");
      return;
    }

    try {
      setCreating(true);
      const client = await createAuthenticatedClient(serverUrl);
      const response = await client.post("/skills", { name: newSkillName });

      if (response.data.status === "success") {
        // Add to local state
        setSkills([
          ...skills,
          {
            id: response.data.skill_id,
            name: newSkillName,
            hours_practiced: 0,
            sessions_completed: 0,
            created_date: new Date().toISOString().split("T")[0],
          },
        ]);
        setNewSkillName("");
        setShowAddSkill(false);
        Alert.alert("✅ Created", `Skill "${newSkillName}" added!`);
      }
    } catch (err) {
      Alert.alert("❌ Error", err.response?.data?.detail || err.message);
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: "center", alignItems: "center" }]}>
        <ActivityIndicator size="large" color="#1A1A1A" />
        <Text style={{ marginTop: 16, color: "#666", fontSize: 14 }}>Loading skills...</Text>
      </View>
    );
  }

  const totalHours = skills.reduce((sum, s) => sum + s.hours_practiced, 0);
  const totalSessions = skills.reduce((sum, s) => sum + s.sessions_completed, 0);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 Skills Progress</Text>

        {/* Overall Stats */}
        <View style={{ flexDirection: "row", gap: 12, marginBottom: 20 }}>
          <View
            style={[
              styles.card,
              {
                flex: 1,
                backgroundColor: "#E6F3FF",
                borderLeftWidth: 4,
                borderLeftColor: "#3182CE",
              },
            ]}
          >
            <Text style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>⏱️ Total Hours</Text>
            <Text style={{ fontSize: 24, fontWeight: "bold", color: "#1A1A1A" }}>
              {totalHours.toFixed(1)}h
            </Text>
          </View>

          <View
            style={[
              styles.card,
              {
                flex: 1,
                backgroundColor: "#F0FFF4",
                borderLeftWidth: 4,
                borderLeftColor: "#48BB78",
              },
            ]}
          >
            <Text style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>🎯 Sessions</Text>
            <Text style={{ fontSize: 24, fontWeight: "bold", color: "#1A1A1A" }}>
              {totalSessions}
            </Text>
          </View>
        </View>

        {/* Add Skill Form */}
        {showAddSkill ? (
          <View style={[styles.card, { marginBottom: 20, backgroundColor: "#FAFAFA" }]}>
            <Text style={{ fontSize: 13, fontWeight: "600", color: "#1A1A1A", marginBottom: 12 }}>
              ➕ Add New Skill
            </Text>
            <TextInput
              style={[
                styles.textInput,
                { marginBottom: 12, fontWeight: "400", color: "#1A1A1A" },
              ]}
              placeholder="E.g., Coding, Guitar, Blender..."
              placeholderTextColor="#999"
              value={newSkillName}
              onChangeText={setNewSkillName}
              editable={!creating}
            />
            <View style={{ flexDirection: "row", gap: 12 }}>
              <TouchableOpacity
                style={[styles.button, { flex: 1 }]}
                onPress={handleCreateSkill}
                disabled={creating}
              >
                {creating ? (
                  <ActivityIndicator size="small" color="#FFF" />
                ) : (
                  <Text style={styles.buttonText}>Create</Text>
                )}
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.button,
                  { flex: 1, backgroundColor: "#E2E8F0" },
                ]}
                onPress={() => {
                  setShowAddSkill(false);
                  setNewSkillName("");
                }}
                disabled={creating}
              >
                <Text style={[styles.buttonText, { color: "#1A1A1A" }]}>Cancel</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          <TouchableOpacity
            style={[styles.button, { marginBottom: 20 }]}
            onPress={() => setShowAddSkill(true)}
          >
            <Text style={styles.buttonText}>➕ Add Skill</Text>
          </TouchableOpacity>
        )}

        {/* Skills List */}
        {skills.length === 0 ? (
          <View style={[styles.card, { alignItems: "center", paddingVertical: 40 }]}>
            <Text style={{ fontSize: 48, marginBottom: 12 }}>🎯</Text>
            <Text style={{ fontSize: 16, fontWeight: "bold", color: "#1A1A1A", marginBottom: 8 }}>
              No Skills Yet
            </Text>
            <Text
              style={{
                fontSize: 14,
                color: "#666",
                textAlign: "center",
                marginBottom: 16,
              }}
            >
              Create skills to track your progress in Coding, Guitar, Blender, and more!
            </Text>
          </View>
        ) : (
          <FlatList
            data={skills.sort((a, b) => b.hours_practiced - a.hours_practiced)}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
            renderItem={({ item }) => (
              <View style={[styles.card, { marginBottom: 12, backgroundColor: "#FAFAFA" }]}>
                {/* Skill Name & Stats */}
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    marginBottom: 12,
                    alignItems: "center",
                  }}
                >
                  <Text style={{ fontSize: 16, fontWeight: "bold", color: "#1A1A1A" }}>
                    {item.name}
                  </Text>
                  <Text style={{ fontSize: 12, color: "#999" }}>
                    Since {new Date(item.created_date).toLocaleDateString()}
                  </Text>
                </View>

                {/* Progress Bars */}
                <View style={{ marginBottom: 12 }}>
                  {/* Hours Practiced Bar */}
                  <View style={{ marginBottom: 12 }}>
                    <View
                      style={{
                        flexDirection: "row",
                        justifyContent: "space-between",
                        marginBottom: 6,
                      }}
                    >
                      <Text style={{ fontSize: 12, color: "#666" }}>⏱️ Hours Practiced</Text>
                      <Text style={{ fontSize: 12, fontWeight: "600", color: "#3182CE" }}>
                        {item.hours_practiced.toFixed(1)}h
                      </Text>
                    </View>
                    <View
                      style={{
                        height: 8,
                        backgroundColor: "#E2E8F0",
                        borderRadius: 4,
                        overflow: "hidden",
                      }}
                    >
                      <View
                        style={{
                          height: "100%",
                          width: Math.min((item.hours_practiced / 100) * 100, 100) + "%",
                          backgroundColor: "#3182CE",
                        }}
                      />
                    </View>
                  </View>

                  {/* Sessions Bar */}
                  <View>
                    <View
                      style={{
                        flexDirection: "row",
                        justifyContent: "space-between",
                        marginBottom: 6,
                      }}
                    >
                      <Text style={{ fontSize: 12, color: "#666" }}>🎯 Sessions</Text>
                      <Text style={{ fontSize: 12, fontWeight: "600", color: "#48BB78" }}>
                        {item.sessions_completed} sessions
                      </Text>
                    </View>
                    <View
                      style={{
                        height: 8,
                        backgroundColor: "#E2E8F0",
                        borderRadius: 4,
                        overflow: "hidden",
                      }}
                    >
                      <View
                        style={{
                          height: "100%",
                          width: Math.min((item.sessions_completed / 50) * 100, 100) + "%",
                          backgroundColor: "#48BB78",
                        }}
                      />
                    </View>
                  </View>
                </View>

                {/* Stats */}
                <Text style={{ fontSize: 12, color: "#999", textAlign: "center" }}>
                  {item.hours_practiced > 0 && item.sessions_completed > 0
                    ? `Avg ${(item.hours_practiced / item.sessions_completed).toFixed(1)}h per session`
                    : "No sessions yet"}
                </Text>
              </View>
            )}
          />
        )}

        {/* Info Box */}
        <View
          style={[
            styles.card,
            {
              backgroundColor: "#EBF8FF",
              borderLeftWidth: 4,
              borderLeftColor: "#3182CE",
              marginTop: 20,
            },
          ]}
        >
          <Text style={{ fontSize: 12, fontWeight: "600", color: "#1A1A1A", marginBottom: 8 }}>
            💡 How Skills Work
          </Text>
          <Text style={{ fontSize: 12, color: "#2D3748", lineHeight: 18, marginBottom: 8 }}>
            • Link tasks to skills to track progress automatically
          </Text>
          <Text style={{ fontSize: 12, color: "#2D3748", lineHeight: 18, marginBottom: 8 }}>
            • Each completed task adds 1 hour to the skill
          </Text>
          <Text style={{ fontSize: 12, color: "#2D3748", lineHeight: 18 }}>
            • Watch your skill progress accumulate over time
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

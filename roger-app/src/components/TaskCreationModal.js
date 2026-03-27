import React, { useState, useEffect } from "react";
import {
  Modal,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from "react-native";
import { styles } from "../styles/styles";

export default function TaskCreationModal({ visible, onClose, serverUrl, createAuthenticatedClient, onTaskCreated }) {
  const [name, setName] = useState("");
  const [day, setDay] = useState("Monday");
  const [startTime, setStartTime] = useState("09:00");
  const [duration, setDuration] = useState("1H");
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [skillsLoading, setSkillsLoading] = useState(false);
  const [isRecurring, setIsRecurring] = useState(true);

  useEffect(() => {
    if (visible) {
      loadSkills();
    }
  }, [visible]);

  const loadSkills = async () => {
    try {
      setSkillsLoading(true);
      const client = await createAuthenticatedClient(serverUrl);
      const res = await client.get("/skills/all");
      if (res.data.skills && Array.isArray(res.data.skills)) {
        setSkills(res.data.skills);
      } else {
        console.warn("Skills endpoint returned unexpected format:", res.data);
        setSkills([]);
      }
    } catch (err) {
      console.warn("Error loading skills:", err.message);
      setSkills([]);
    } finally {
      setSkillsLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!name.trim()) {
      Alert.alert("❌ Error", "Task name required");
      return;
    }

    try {
      setLoading(true);
      const client = await createAuthenticatedClient(serverUrl);
      
      const res = await client.post("/tasks/create", {
        name,
        day_of_week: day,
        start_time: startTime,
        duration,
        skill_id: selectedSkill || null,
        is_recurring: isRecurring,
      });

      Alert.alert("✅ Success", "Task created!");
      setName("");
      setDay("Monday");
      setStartTime("09:00");
      setDuration("1H");
      setSelectedSkill(null);
      setIsRecurring(true);
      
      if (onTaskCreated) onTaskCreated();
      onClose();
    } catch (err) {
      Alert.alert("❌ Error", err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={{ flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" }}>
        <View style={{ backgroundColor: "#FFF", padding: 20, borderTopLeftRadius: 20, borderTopRightRadius: 20, maxHeight: "80%" }}>
          <Text style={styles.sectionTitle}>➕ Create Task</Text>

          <ScrollView style={{ marginBottom: 16 }}>
            <TextInput
              style={styles.textInput}
              placeholder="Task name (e.g., Coding - Review data structures)"
              value={name}
              onChangeText={setName}
            />

            <Text style={{ marginTop: 16, marginBottom: 8, fontWeight: "600" }}>📅 Day</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 16 }}>
              {days.map(d => (
                <TouchableOpacity
                  key={d}
                  style={[
                    styles.button,
                    { marginRight: 8, backgroundColor: day === d ? "#3182CE" : "#DDD", paddingHorizontal: 12 }
                  ]}
                  onPress={() => setDay(d)}
                >
                  <Text style={{ color: day === d ? "#FFF" : "#000", fontSize: 12 }}>{d.slice(0, 3)}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <TextInput
              style={styles.textInput}
              placeholder="Start time (e.g., 09:00)"
              value={startTime}
              onChangeText={setStartTime}
            />

            <TextInput
              style={styles.textInput}
              placeholder="Duration (e.g., 1H or 1.5H)"
              value={duration}
              onChangeText={setDuration}
            />

            <View style={{ flexDirection: "row", alignItems: "center", marginTop: 16, marginBottom: 16, paddingHorizontal: 12, backgroundColor: "#F0F0F0", borderRadius: 8, padding: 12 }}>
              <Text style={{ flex: 1, fontWeight: "600", color: "#1A1A1A" }}>🔄 Repeat Weekly?</Text>
              <TouchableOpacity
                style={{
                  paddingHorizontal: 16,
                  paddingVertical: 8,
                  backgroundColor: isRecurring ? "#3182CE" : "#DDD",
                  borderRadius: 6,
                }}
                onPress={() => setIsRecurring(!isRecurring)}
              >
                <Text style={{ color: isRecurring ? "#FFF" : "#666", fontWeight: "600" }}>
                  {isRecurring ? "Yes" : "Once"}
                </Text>
              </TouchableOpacity>
            </View>

            <Text style={{ marginTop: 8, marginBottom: 12, fontWeight: "600" }}>🎯 Link to Skill (Optional)</Text>
            <View style={{ borderWidth: 1, borderColor: "#DDD", borderRadius: 8, maxHeight: 150 }}>
              {skillsLoading ? (
                <View style={{ padding: 12, justifyContent: "center", alignItems: "center" }}>
                  <ActivityIndicator size="small" color="#3182CE" />
                  <Text style={{ marginTop: 8, color: "#666", fontSize: 12 }}>Loading skills...</Text>
                </View>
              ) : skills.length > 0 ? (
                <ScrollView>
                  {skills.map(skill => (
                    <TouchableOpacity
                      key={skill.id}
                      style={{
                        padding: 12,
                        borderBottomWidth: 1,
                        borderBottomColor: "#EEE",
                        backgroundColor: selectedSkill === skill.id ? "#E6F2FF" : "#FFF"
                      }}
                      onPress={() => setSelectedSkill(selectedSkill === skill.id ? null : skill.id)}
                    >
                      <Text style={{ color: selectedSkill === skill.id ? "#3182CE" : "#000" }}>
                        {selectedSkill === skill.id ? "✓ " : ""}{skill.name}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              ) : (
                <Text style={{ padding: 12, color: "#666" }}>No skills available</Text>
              )}
            </View>
          </ScrollView>

          <View style={{ flexDirection: "row", gap: 12, marginTop: 16 }}>
            <TouchableOpacity style={[styles.button, { flex: 1, backgroundColor: "#CCCCCC" }]} onPress={onClose} disabled={loading}>
              <Text style={{ color: "#333" }}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.button, { flex: 1 }]} onPress={handleCreate} disabled={loading}>
              {loading ? <ActivityIndicator color="#FFF" size="small" /> : <Text style={styles.buttonText}>Create Task</Text>}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

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

  useEffect(() => {
    if (visible) {
      loadSkills();
    }
  }, [visible]);

  const loadSkills = async () => {
    try {
      const client = await createAuthenticatedClient(serverUrl);
      const res = await client.get("/skills/all");
      setSkills(res.data.skills || []);
    } catch (err) {
      console.warn("Error loading skills:", err.message);
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
      
      const params = selectedSkill ? { skill_id: selectedSkill } : {};
      const res = await client.post("/tasks/create", {
        name,
        day_of_week: day,
        start_time: startTime,
        duration,
      }, { params });

      Alert.alert("✅ Success", "Task created!");
      setName("");
      setDay("Monday");
      setStartTime("09:00");
      setDuration("1H");
      setSelectedSkill(null);
      
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

            <Text style={{ marginTop: 16, marginBottom: 8, fontWeight: "600" }}>🎯 Link to Skill (Optional)</Text>
            <View style={{ borderWidth: 1, borderColor: "#DDD", borderRadius: 8, maxHeight: 150 }}>
              {skills.length > 0 ? (
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

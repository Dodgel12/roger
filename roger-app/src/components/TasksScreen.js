import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { createAuthenticatedClient } from '../services/authService';
import { styles } from '../styles/styles';

const TasksScreen = ({ serverUrl, createAuthenticatedClient: authenticatedClientFactory, onCreateTask, onTaskCreated }) => {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({ planned: 0, completed: 0, score: 0 });
  const [loading, setLoading] = useState(true);

  const fetchTasksAndStats = async () => {
    try {
      const client = await createAuthenticatedClient(serverUrl);
      const [tasksRes, statsRes] = await Promise.all([
        client.get("/tasks/today"),
        client.get("/stats/today")
      ]);
      setTasks(tasksRes.data.tasks || []);
      setStats(statsRes.data);
    } catch (err) {
      if (err.response?.status === 401) {
        console.warn("Failed to fetch tasks/stats - Authentication error (401). Token may be invalid or expired.");
      } else {
        console.warn("Failed to fetch tasks/stats:", err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasksAndStats();
  }, [serverUrl]);

  const toggleTask = async (taskId, isCompleted) => {
    if (isCompleted) return; // Already done, can't undo for now based on current API

    // Optimistic update
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, completed: true } : t));
    
    try {
      const client = await createAuthenticatedClient(serverUrl);
      const res = await client.post(`/tasks/${taskId}/complete`);
      setStats(res.data.stats); // Update score from server response
    } catch (err) {
      console.warn("Failed to complete task:", err.message);
      fetchTasksAndStats(); // Revert on failure
    }
  };

  const deleteTask = async (taskId) => {
    Alert.alert(
      "Delete Task",
      "Are you sure you want to delete this task?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              const client = await createAuthenticatedClient(serverUrl);
              await client.delete(`/tasks/${taskId}`);
              fetchTasksAndStats();
              Alert.alert("✅ Deleted", "Task deleted successfully");
            } catch (err) {
              Alert.alert("❌ Error", "Failed to delete task");
              console.warn("Failed to delete task:", err.message);
            }
          }
        }
      ]
    );
  };

  const renderTask = ({ item }) => (
    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
      <TouchableOpacity 
        style={[styles.taskCard, item.completed ? styles.taskCardDone : styles.taskCardActive, { flex: 1 }]}
        activeOpacity={0.7}
        onPress={() => toggleTask(item.id, item.completed)}
      >
        <View style={styles.taskInfo}>
          <Text style={[styles.taskName, item.completed && styles.taskNameDone]}>
            {item.name}
          </Text>
          <Text style={styles.taskTime}>
            {item.start_time} • {item.duration}
          </Text>
        </View>
        <View style={[styles.checkbox, item.completed && styles.checkboxDone]}>
          {item.completed && <View style={styles.checkmark} />}
        </View>
      </TouchableOpacity>
      <TouchableOpacity
        style={{ padding: 8, marginLeft: 4 }}
        onPress={() => deleteTask(item.id)}
      >
        <Text style={{ fontSize: 18, color: '#FF6B6B' }}>🗑️</Text>
      </TouchableOpacity>
    </View>
  );

  const percent = Math.round(stats.score * 100);

  return (
    <View style={styles.tasksContainer}>
      <View style={styles.scoreCard}>
        <Text style={styles.scoreTitle}>Daily Discipline</Text>
        {loading ? (
          <ActivityIndicator color="#FFF" />
        ) : (
          <Text style={styles.scoreValue}>
            {stats.completed} / {stats.planned} — {percent}%
          </Text>
        )}
      </View>

      {onCreateTask && (
        <TouchableOpacity style={[styles.button, { marginHorizontal: 16, marginTop: 12, marginBottom: 12 }]} onPress={onCreateTask}>
          <Text style={styles.buttonText}>➕ Create Task</Text>
        </TouchableOpacity>
      )}

      <FlatList
        data={tasks}
        keyExtractor={item => item.id.toString()}
        renderItem={renderTask}
        contentContainerStyle={styles.taskList}
        showsVerticalScrollIndicator={false}
        refreshing={loading}
        onRefresh={fetchTasksAndStats}
        ListEmptyComponent={
          !loading && <Text style={{textAlign: 'center', marginTop: 20, color: '#666'}}>No tasks scheduled for today.</Text>
        }
      />
    </View>
  );
};

export default TasksScreen;

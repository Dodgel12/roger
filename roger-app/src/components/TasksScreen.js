import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import axios from 'axios';
import { styles } from '../styles/styles';

const TasksScreen = ({ serverUrl }) => {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({ planned: 0, completed: 0, score: 0 });
  const [loading, setLoading] = useState(true);

  const fetchTasksAndStats = async () => {
    try {
      const [tasksRes, statsRes] = await Promise.all([
        axios.get(`${serverUrl}/tasks/today`),
        axios.get(`${serverUrl}/stats/today`)
      ]);
      setTasks(tasksRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.warn("Failed to fetch tasks/stats:", err.message);
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
      const res = await axios.post(`${serverUrl}/tasks/${taskId}/complete`);
      setStats(res.data.stats); // Update score from server response
    } catch (err) {
      console.warn("Failed to complete task:", err.message);
      fetchTasksAndStats(); // Revert on failure
    }
  };

  const renderTask = ({ item }) => (
    <TouchableOpacity 
      style={[styles.taskCard, item.completed ? styles.taskCardDone : styles.taskCardActive]}
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

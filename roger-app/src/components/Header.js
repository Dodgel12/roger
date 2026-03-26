import React from 'react';
import { View, Text, TouchableOpacity, Alert } from 'react-native';
import { styles } from '../styles/styles';

const Header = ({ onLogout }) => {
  const handleLogoutPress = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', onPress: () => {} },
        { text: 'Logout', onPress: onLogout, style: 'destructive' }
      ]
    );
  };

  return (
    <View style={styles.header}>
      <Text style={styles.headerTitle}>ROGER</Text>
      <View style={styles.statusDot} />
      {onLogout && (
        <TouchableOpacity 
          style={{ position: 'absolute', right: 16 }}
          onPress={handleLogoutPress}
        >
          <Text style={{ fontSize: 12, color: '#999', fontWeight: '600' }}>Logout</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

export default Header;

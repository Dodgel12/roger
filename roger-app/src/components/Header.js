import React from 'react';
import { View, Text } from 'react-native';
import { styles } from '../styles/styles';

const Header = () => (
  <View style={styles.header}>
    <Text style={styles.headerTitle}>ROGER</Text>
    <View style={styles.statusDot} />
  </View>
);

export default Header;

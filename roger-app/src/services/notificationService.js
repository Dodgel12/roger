import * as Notifications from "expo-notifications";
import { Platform } from "react-native";
import Constants from "expo-constants";
import messaging from '@react-native-firebase/messaging';

// Notification configuration
export const configureNotifications = () => {
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: true,
    }),
  });
};

export async function registerForPushNotificationsAsync() {
  let token;
  
  if (Platform.OS === 'android') {
    // Configure Android notification channel for all push notifications
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
    });
    
    // For standalone APK: also configure FCM channel if available
    try {
      await Notifications.setNotificationChannelAsync('fcm', {
        name: 'FCM',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    } catch (e) {
      console.log("FCM channel not available (expected in Expo Go)");
    }
  }

  // Request permissions
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
    console.log(`🔔 Notification permission status: ${finalStatus}`);
  }
  
  if (finalStatus !== 'granted') {
    console.warn('⚠️ Failed to get push token for push notification!');
    return null;
  }

  // Get the token
  try {
    const projectId = Constants?.expoConfig?.extra?.eas?.projectId ?? Constants?.easConfig?.projectId;
    
    if (!projectId) {
      console.error('❌ EAS Project ID not found in app.json');
      return null;
    }

    console.log(`📱 EAS Project ID: ${projectId}`);

    // For Expo Go and managed builds: use Expo push token
    const { data: expoPushTokenData } = await Notifications.getExpoPushTokenAsync({
      projectId,
      experienceId: '@anonymous/roger-app'
    });

    console.log(`✅ Expo Push Token obtained: ${expoPushTokenData?.substring(0, 20)}...`);
    
    return expoPushTokenData;

  } catch (e) {
    console.error("❌ Error getting push token:", e.message);
    console.log("📌 Make sure your app is built with EAS or signed with Expo Go");
    return null;
  }
}

// Listener for incoming notifications while app is in foreground
export const setupNotificationListeners = () => {
  const foregroundSubscription = Notifications.addNotificationReceivedListener(notification => {
    console.log("🔔 Notification received (foreground):", notification.request.content.title);
  });

  const responseSubscription = Notifications.addNotificationResponseReceivedListener(response => {
    console.log("👆 User tapped notification:", response.notification.request.content.title);
    // Handle navigation based on notification data if needed
    const data = response.notification.request.content.data;
    if (data) {
      console.log("📦 Notification data:", data);
    }
  });

  return () => {
    Notifications.removeNotificationSubscription(foregroundSubscription);
    Notifications.removeNotificationSubscription(responseSubscription);
  };
};

// Get Firebase FCM Token
export async function getFirebaseToken() {
  try {
    // Request permission first
    const authStatus = await messaging().requestPermission();
    const enabled =
      authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
      authStatus === messaging.AuthorizationStatus.PROVISIONAL;

    if (enabled) {
      console.log('🔥 Firebase messaging permission granted');
      
      // Get the FCM token
      const fcmToken = await messaging().getToken();
      console.log('🔥 Firebase FCM Token:', fcmToken);
      return fcmToken;
    } else {
      console.warn('⚠️ Firebase messaging permission denied');
      return null;
    }
  } catch (error) {
    console.error('❌ Error getting Firebase token:', error);
    return null;
  }
}

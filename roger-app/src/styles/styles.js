import { StyleSheet } from "react-native";

export const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#F8F9FA" },
  header: {
    height: 60,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    borderBottomWidth: 1,
    borderBottomColor: "#EEE",
    backgroundColor: "#FFF"
  },
  headerTitle: { fontSize: 18, fontWeight: "800", letterSpacing: 2, color: "#1A1A1A" },
  statusDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: "#4CAF50", marginLeft: 8, marginTop: 2 },
  keyboardView: { flex: 1 },
  chatList: { paddingHorizontal: 16, paddingVertical: 20, paddingBottom: 10 },
  
  messageWrapper: { marginBottom: 16, width: "100%", flexDirection: "row" },
  userWrapper: { justifyContent: "flex-end" },
  rogerWrapper: { justifyContent: "flex-start" },
  
  messageBubble: {
    maxWidth: "80%",
    padding: 12,
    borderRadius: 20,
    elevation: 1,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  userBubble: {
    backgroundColor: "#1A1A1A",
    borderBottomRightRadius: 4,
  },
  rogerBubble: {
    backgroundColor: "#FFF",
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: "#E0E0E0",
  },
  
  messageText: { fontSize: 16, lineHeight: 22 },
  userText: { color: "#FFF" },
  rogerText: { color: "#1A1A1A" },
  
  timeText: { fontSize: 10, marginTop: 4, alignSelf: "flex-end" },
  userTimeText: { color: "rgba(255,255,255,0.6)" },
  rogerTimeText: { color: "#999" },
  
  thinkingContainer: { flexDirection: "row", alignItems: "center", paddingHorizontal: 20, marginBottom: 10 },
  thinkingText: { marginLeft: 8, color: "#666", fontSize: 14, fontStyle: "italic" },
  
  inputContainer: {
    flexDirection: "row",
    alignItems: "flex-end",
    padding: 12,
    backgroundColor: "#FFF",
    borderTopWidth: 1,
    borderTopColor: "#EEE",
  },
  input: {
    flex: 1,
    minHeight: 40,
    maxHeight: 120,
    backgroundColor: "#F1F3F5",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingTop: 10,
    paddingBottom: 10,
    fontSize: 16,
    color: "#1A1A1A",
    marginRight: 10,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#1A1A1A",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 2,
  },
  sendButtonDisabled: {
    backgroundColor: "#CCC",
  }
});

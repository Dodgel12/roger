import { StyleSheet } from "react-native";

export const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#F8F9FA" },
  header: {
    marginTop: 20,
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
    marginBottom: 7
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
  },
  
  // Tab Bar Styles
  tabBar: {
    flexDirection: "row",
    height: 60,
    backgroundColor: "#FFF",
    borderTopWidth: 1,
    borderTopColor: "#EEE",
    justifyContent: "space-around",
    alignItems: "center",
  },
  tabItem: {
    flex: 1,
    height: "100%",
    justifyContent: "center",
    alignItems: "center",
  },
  tabText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#999",
  },
  tabTextActive: {
    color: "#1A1A1A",
    fontWeight: "800",
  },
  
  // Tasks Screen Styles
  tasksContainer: {
    flex: 1,
    backgroundColor: "#F8F9FA",
  },
  scoreCard: {
    backgroundColor: "#1A1A1A",
    margin: 16,
    padding: 20,
    borderRadius: 16,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  scoreTitle: {
    color: "rgba(255,255,255,0.7)",
    fontSize: 14,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 1,
    marginBottom: 8,
  },
  scoreValue: {
    color: "#FFF",
    fontSize: 32,
    fontWeight: "800",
  },
  taskList: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  taskCard: {
    backgroundColor: "#FFF",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    flexDirection: "row",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
    borderWidth: 1,
    borderColor: "transparent",
  },
  taskCardDone: {
    opacity: 0.6,
    backgroundColor: "#FAFAFA",
  },
  taskCardActive: {
    borderColor: "#1A1A1A",
  },
  taskInfo: {
    flex: 1,
  },
  taskName: {
    fontSize: 16,
    fontWeight: "700",
    color: "#1A1A1A",
    marginBottom: 4,
  },
  taskNameDone: {
    textDecorationLine: "line-through",
    color: "#999",
  },
  taskTime: {
    fontSize: 14,
    color: "#666",
  },
  checkbox: {
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 2,
    borderColor: "#CCC",
    justifyContent: "center",
    alignItems: "center",
    marginLeft: 16,
  },
  checkboxDone: {
    backgroundColor: "#4CAF50",
    borderColor: "#4CAF50",
  },
  checkmark: {
    width: 12,
    height: 12,
    backgroundColor: "#FFF",
    borderRadius: 6,
  },

  // Login Screen Styles
  loginContainer: {
    flex: 1,
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingVertical: 40,
    backgroundColor: "#F8F9FA",
  },
  loginHeader: {
    alignItems: "center",
    marginTop: 60,
  },
  loginTitle: {
    fontSize: 48,
    fontWeight: "800",
    color: "#1A1A1A",
    marginBottom: 8,
  },
  loginSubtitle: {
    fontSize: 16,
    color: "#666",
    fontWeight: "600",
  },
  loginForm: {
    flex: 1,
    justifyContent: "center",
  },
  loginInput: {
    backgroundColor: "#FFF",
    borderWidth: 1,
    borderColor: "#E0E0E0",
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    marginBottom: 16,
    color: "#1A1A1A",
  },
  errorText: {
    color: "#D32F2F",
    fontSize: 14,
    marginBottom: 12,
    fontWeight: "600",
  },
  authButton: {
    backgroundColor: "#1A1A1A",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 20,
    marginBottom: 16,
  },
  authButtonDisabled: {
    backgroundColor: "#CCC",
  },
  authButtonText: {
    color: "#FFF",
    fontSize: 16,
    fontWeight: "700",
  },
  toggleContainer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
  },
  toggleText: {
    color: "#666",
    fontSize: 14,
  },
  toggleButton: {
    color: "#1A1A1A",
    fontSize: 14,
    fontWeight: "700",
  },
  loginFooter: {
    alignItems: "center",
    paddingBottom: 20,
  },
  footerText: {
    color: "#999",
    fontSize: 12,
    marginBottom: 4,
    fontStyle: "italic",
  },
});

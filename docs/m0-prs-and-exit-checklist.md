# M0 – PR Breakdown & Exit Checklist

This file extracts PR definitions and success criteria for easier execution.

---

## 🔧 PR Breakdown

### **PR #3 – Chainlit UI**
- Implement Chainlit app
- Connect Chainlit handler → LangGraph node
- Local run support

### **PR #4 – Docker & Cloud Run Deployment**
- Write Dockerfile
- Add deployment script or instructions
- Manual deploy validation

### **PR #6 – CD**
- Auto-build + deploy on merge to main
- Store config in GitHub secrets

### **PR #7 – Observability**
- Structured logs on Cloud Run
- Error handling wrapper

---

## ✅ Exit Checklist for M0

### **Functional**
- [ ] User can chat with TrainFlow in Chainlit UI
- [ ] Responses come from LangGraph + OpenAI

### **Infrastructure**
- [ ] Container builds locally
- [ ] Cloud Run deployment works
- [ ] Secrets configured properly

### **CI/CD**
- [ ] CI runs lint + tests on every PR
- [ ] CD deploys automatically on main merge

### **Quality**
- [ ] Logs visible and useful in Cloud Run
- [ ] Basic error-handling implemented

If all boxes are checked, M0 is complete and ready for M1.

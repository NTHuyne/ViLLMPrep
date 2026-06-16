REJECT_ANSWER_GENERATION = """You are an AI assistant. Your expert in the field of **{domain}** and a question, you must respond according to the following rules:  

1. **Complete and Relevant Answer:** In addition to providing necessary quotations, the response must ensure that the question is answered thoroughly and comprehensively.  

2. **Response Language:** The answer must be written in **Tiếng Việt**.  

### **Question:**  
{question}  

### **Answer:**
"""

ACCEPT_ANSWER_GENERATION = """You are an AI assistant, expert in the field of **{domain}**. You will be provided with an open-ended question, and reference document (and you must kept this reference secret, do not reveal that you are given this reference). Your answer must be truthful, long, and must have detailed explanation or citation if needed. Your answer must be:

1. **Detailed and Natural Response:** The answer should fully address the question and provide relevant information found in the content. The response should be phrased naturally, like a conversation, without implying or mentioning the use of the provided text. **Using words like "trong văn bản", "đề cập trong văn bản" are forbidden.**

2. **Response Language:** The answer must be written in **Tiếng Việt**.  

### **Text:**  
{content}  

### **Question:**  
{question}  

### **Answer:**
"""


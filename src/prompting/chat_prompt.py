def make_chat_prompt(history, new_message, context, main_paper):
    prompt = '''
    You are an helpful assistant who helps user to answer their queries related to a research paper in a conversational style.
    
    You will be answering the question based on the previous conversation history and the context provided. 
    If the question is not relevant to the conversation history, please answer only based on the context.
    If the question is not relevant to the context and you are unable to answer the question, please just say "I don't know the answer".
    
    The conversation is based on the following paper, so you can consider it as the main paper. 
    If you need additional context to answer the question, relevant snippets from the referenced papers are provided as context.
    
    Main Paper:
    {main_paper}
    
    Conversation History:
    {history}
    
    New Message:
    {new_message}
    
    Retrieved Context:
    {context}
    
    Your Answer:
    '''
    model_input = prompt.format(main_paper=main_paper, history=history, new_message=new_message, context=context)
    return model_input


def get_suggestions(previous_prompt, previous_response):
    prompt = '''
    You are an intelligent assistant who suggests questions to ask next to the user based on the previous question and the answer.
    
    Previous Question:
    {previous_prompt}
    
    Previous Answer:
    {previous_response}
    
    Suggested Questions:
    ## Output Format(only list without any encapsulation): ['Question 1', 'Question 2', 'Question 3']
    Output:
    '''

    model_input = prompt.format(previous_prompt=previous_prompt, previous_response=previous_response)
    return model_input

"""
AI Content Studio - Complete Streamlit App
An all-in-one AI-powered content creation tool using OpenAI API
Author: AI Assistant
Date: 2025
"""

import streamlit as st
import openai
from datetime import datetime
import json

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="AI Content Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .token-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== PROMPT TEMPLATES ====================
PROMPT_TEMPLATES = {
    "Blog": """Create a comprehensive blog post on the topic: "{topic}"

Requirements:
- Tone: {tone}
- Target Audience: {audience}
- Length: Approximately {word_limit} words
- Include an engaging introduction, well-structured body with subheadings, and a strong conclusion
- Make it SEO-friendly with natural keyword integration
- Add a call-to-action at the end""",

    "Ad Copy": """Create compelling advertising copy for: "{topic}"

Requirements:
- Tone: {tone}
- Target Audience: {audience}
- Length: Approximately {word_limit} words
- Focus on benefits and emotional triggers
- Include a strong headline and persuasive call-to-action
- Make it memorable and action-oriented""",

    "Social Media Post": """Create an engaging social media post about: "{topic}"

Requirements:
- Tone: {tone}
- Target Audience: {audience}
- Length: Approximately {word_limit} words
- Make it shareable and conversation-starting
- Include relevant hashtags (3-5)
- Consider platform best practices (Twitter, LinkedIn, Instagram, etc.)
- Add emojis where appropriate""",

    "Product Description": """Create a compelling product description for: "{topic}"

Requirements:
- Tone: {tone}
- Target Audience: {audience}
- Length: Approximately {word_limit} words
- Highlight key features and benefits
- Address pain points and solutions
- Include technical specifications if relevant
- End with a compelling reason to purchase""",

    "Script": """Create a video/audio script for: "{topic}"

Requirements:
- Tone: {tone}
- Target Audience: {audience}
- Length: Approximately {word_limit} words
- Include stage directions in [brackets]
- Make it natural and conversational
- Structure with clear introduction, body, and conclusion
- Add cues for emphasis and pacing"""
}

# ==================== HELPER FUNCTIONS ====================

def calculate_cost(tokens, model):
    """Calculate approximate cost based on token usage"""
    # Pricing as of 2025 (approximate, check OpenAI for latest)
    pricing = {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    if model in pricing:
        # Estimate 75% input, 25% output token ratio
        input_tokens = tokens * 0.75
        output_tokens = tokens * 0.25
        cost = (input_tokens * pricing[model]["input"] / 1000) + \
               (output_tokens * pricing[model]["output"] / 1000)
        return cost
    return 0.0

def generate_content(api_key, model, content_type, topic, tone, audience, word_limit, temperature):
    """Generate content using OpenAI API"""
    
    # Validate inputs
    if not api_key:
        return None, "Please enter your OpenAI API key in the sidebar."
    if not topic:
        return None, "Please enter a topic or idea for your content."
    if not audience:
        return None, "Please specify your target audience."
    
    # Set up OpenAI client
    openai.api_key = api_key
    
    # Create prompt from template
    user_prompt = PROMPT_TEMPLATES[content_type].format(
        topic=topic,
        tone=tone,
        audience=audience,
        word_limit=word_limit
    )
    
    try:
        # Make API call (supports both old and new OpenAI SDK versions)
        try:
            # New SDK version (>= 1.0.0)
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert content creator with years of experience in copywriting, marketing, and creative writing. You produce high-quality, engaging content tailored to specific audiences."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=word_limit * 2  # Rough estimate: 1 word ≈ 1.3 tokens
            )
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
        except AttributeError:
            # Old SDK version
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert content creator with years of experience in copywriting, marketing, and creative writing. You produce high-quality, engaging content tailored to specific audiences."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=word_limit * 2
            )
            
            content = response['choices'][0]['message']['content']
            tokens = response['usage']['total_tokens']
        
        return content, tokens
        
    except openai.AuthenticationError:
        return None, "❌ Invalid API key. Please check your OpenAI API key."
    except openai.RateLimitError:
        return None, "❌ Rate limit exceeded. Please wait a moment and try again."
    except openai.APIError as e:
        return None, f"❌ OpenAI API error: {str(e)}"
    except Exception as e:
        return None, f"❌ Unexpected error: {str(e)}"

def create_download_content(content, content_type, topic):
    """Create downloadable file content with metadata"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    file_content = f"""# {content_type}: {topic}
Generated: {timestamp}
Created with AI Content Studio

---

{content}

---
Generated by AI Content Studio
Powered by OpenAI API
"""
    return file_content

# ==================== MAIN APP ====================

def main():
    # Header
    st.markdown('<h1 class="main-header">✨ AI Content Studio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your All-in-One AI-Powered Content Creation Tool</p>', unsafe_allow_html=True)
    
    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key Input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys"
        )
        
        if api_key:
            st.success("✅ API Key loaded")
        else:
            st.warning("⚠️ Please enter your API key to continue")
        
        st.divider()
        
        # Model Selection
        st.subheader("🤖 Model Settings")
        model = st.selectbox(
            "Select Model",
            ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4"],
            help="GPT-4 models are more capable but cost more"
        )
        
        # Temperature Control
        temperature = st.slider(
            "Creativity (Temperature)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more creative but less focused"
        )
        
        st.divider()
        
        # Information
        st.subheader("ℹ️ About")
        st.info("""
        **AI Content Studio** helps you create professional content in seconds using advanced AI.
        
        **Features:**
        - 5+ content types
        - Customizable tone & audience
        - Token tracking
        - Download capability
        """)
        
        st.divider()
        
        # Tips
        with st.expander("💡 Pro Tips"):
            st.markdown("""
            - Be specific with your topic
            - Define your audience clearly
            - Adjust temperature for creativity
            - Use lower temp (0.3-0.5) for factual content
            - Use higher temp (0.7-0.9) for creative content
            """)
    
    # ==================== MAIN CONTENT AREA ====================
    
    # Initialize session state
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = None
    if 'token_count' not in st.session_state:
        st.session_state.token_count = 0
    if 'generation_params' not in st.session_state:
        st.session_state.generation_params = {}
    
    # Content Input Section
    st.header("📝 Content Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        content_type = st.selectbox(
            "Content Type",
            ["Blog", "Ad Copy", "Social Media Post", "Product Description", "Script"],
            help="Choose the type of content you want to create"
        )
        
        topic = st.text_input(
            "Content Topic or Idea",
            placeholder="e.g., Benefits of meditation for busy professionals",
            help="Describe what you want the content to be about"
        )
        
        tone = st.selectbox(
            "Tone",
            ["Professional", "Friendly", "Persuasive", "Humorous", "Inspirational", "Educational"],
            help="Select the desired tone for your content"
        )
    
    with col2:
        audience = st.text_input(
            "Target Audience",
            placeholder="e.g., Young entrepreneurs aged 25-35",
            help="Who is this content for?"
        )
        
        word_limit = st.slider(
            "Word Limit",
            min_value=50,
            max_value=2000,
            value=300,
            step=50,
            help="Approximate number of words (actual output may vary)"
        )
        
        st.write("")  # Spacing
        st.write("")  # Spacing
    
    # Generate Button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        generate_button = st.button("🚀 Generate Content", use_container_width=True)
    
    # Generate content
    if generate_button:
        with st.spinner("🎨 Creating your content..."):
            content, result = generate_content(
                api_key, model, content_type, topic, tone, audience, word_limit, temperature
            )
            
            if content:
                st.session_state.generated_content = content
                st.session_state.token_count = result
                st.session_state.generation_params = {
                    'content_type': content_type,
                    'topic': topic,
                    'tone': tone,
                    'audience': audience,
                    'word_limit': word_limit,
                    'model': model
                }
                st.success("✅ Content generated successfully!")
            else:
                st.error(result)
    
    # Display Generated Content
    if st.session_state.generated_content:
        st.divider()
        st.header("📄 Generated Content")
        
        # Display content in text area (editable)
        edited_content = st.text_area(
            "Your Content (editable)",
            value=st.session_state.generated_content,
            height=400,
            help="You can edit the content before downloading"
        )
        
        # Update session state if edited
        st.session_state.generated_content = edited_content
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Regenerate button
            if st.button("🔄 Regenerate", use_container_width=True):
                with st.spinner("🎨 Regenerating..."):
                    params = st.session_state.generation_params
                    content, result = generate_content(
                        api_key, model, params['content_type'], params['topic'],
                        params['tone'], params['audience'], params['word_limit'], temperature
                    )
                    
                    if content:
                        st.session_state.generated_content = content
                        st.session_state.token_count = result
                        st.rerun()
                    else:
                        st.error(result)
        
        with col2:
            # Download as TXT
            download_content_txt = create_download_content(
                edited_content,
                st.session_state.generation_params['content_type'],
                st.session_state.generation_params['topic']
            )
            st.download_button(
                label="📥 Download .txt",
                data=download_content_txt,
                file_name=f"ai_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col3:
            # Download as MD
            st.download_button(
                label="📥 Download .md",
                data=download_content_txt,
                file_name=f"ai_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col4:
            # Clear button
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.generated_content = None
                st.session_state.token_count = 0
                st.session_state.generation_params = {}
                st.rerun()
        
        # Token and Cost Information
        st.markdown('<div class="token-info">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Tokens Used", f"{st.session_state.token_count:,}")
        
        with col2:
            word_count = len(edited_content.split())
            st.metric("Word Count", f"{word_count:,}")
        
        with col3:
            cost = calculate_cost(st.session_state.token_count, model)
            st.metric("Est. Cost", f"${cost:.4f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Content Analysis
        with st.expander("📊 Content Analysis"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Content Metrics:**")
                st.write(f"- Characters: {len(edited_content):,}")
                st.write(f"- Sentences: {edited_content.count('.') + edited_content.count('!') + edited_content.count('?')}")
                st.write(f"- Paragraphs: {edited_content.count(chr(10) + chr(10)) + 1}")
            
            with col2:
                st.write("**Generation Settings:**")
                st.write(f"- Model: {model}")
                st.write(f"- Temperature: {temperature}")
                st.write(f"- Target Words: {st.session_state.generation_params['word_limit']}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div class="footer">Built with ❤️ using Streamlit & OpenAI API | © 2025 AI Content Studio</div>',
        unsafe_allow_html=True
    )

# ==================== RUN APP ====================
if __name__ == "__main__":
    main()
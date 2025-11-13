"""
AI Visual Studio - Complete Streamlit App
Social Media Image & Banner Generator with AI-powered content
Author: AI Assistant
Date: 2025
"""

import streamlit as st
import openai
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
import requests
import json

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="AI Visual Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
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
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #f5576c 0%, #f093fb 100%);
    }
    .preview-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    }
    .social-post-box {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .cost-info {
        background-color: #e8f5e9;
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
    .platform-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .badge-instagram {
        background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);
        color: white;
    }
    .badge-facebook {
        background: #1877f2;
        color: white;
    }
    .badge-twitter {
        background: #1da1f2;
        color: white;
    }
    .badge-linkedin {
        background: #0077b5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================== BANNER SIZE PRESETS ====================
BANNER_SIZES = {
    "Instagram Post (Square)": (1080, 1080),
    "Instagram Story": (1080, 1920),
    "Facebook Post": (1200, 630),
    "Facebook Cover": (820, 312),
    "Twitter Post": (1200, 675),
    "Twitter Header": (1500, 500),
    "LinkedIn Post": (1200, 627),
    "LinkedIn Banner": (1584, 396),
    "YouTube Thumbnail": (1280, 720),
    "Pinterest Pin": (1000, 1500),
    "Web Banner (Large)": (728, 90),
    "Web Banner (Medium)": (468, 60),
    "Custom Size": (None, None)
}

# ==================== SOCIAL MEDIA PLATFORMS ====================
PLATFORMS = {
    "Instagram": {
        "emoji": "📸",
        "color": "#E1306C",
        "hashtag_limit": 30,
        "char_limit": 2200
    },
    "Facebook": {
        "emoji": "👍",
        "color": "#1877f2",
        "hashtag_limit": 10,
        "char_limit": 63206
    },
    "Twitter/X": {
        "emoji": "🐦",
        "color": "#1da1f2",
        "hashtag_limit": 5,
        "char_limit": 280
    },
    "LinkedIn": {
        "emoji": "💼",
        "color": "#0077b5",
        "hashtag_limit": 10,
        "char_limit": 3000
    },
    "Pinterest": {
        "emoji": "📌",
        "color": "#E60023",
        "hashtag_limit": 20,
        "char_limit": 500
    }
}

# ==================== HELPER FUNCTIONS ====================

def generate_image_dalle(api_key, prompt, size="1024x1024", quality="standard", style="vivid"):
    """Generate image using DALL-E 3"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        # Download the image
        img_response = requests.get(image_url)
        img = Image.open(io.BytesIO(img_response.content))
        
        return img, revised_prompt, None
        
    except openai.AuthenticationError:
        return None, None, "❌ Invalid API key. Please check your OpenAI API key."
    except openai.BadRequestError as e:
        return None, None, f"❌ Bad request: {str(e)}"
    except Exception as e:
        return None, None, f"❌ Error generating image: {str(e)}"

def resize_image(img, target_size):
    """Resize image to target size while maintaining aspect ratio"""
    if target_size[0] is None or target_size[1] is None:
        return img
    
    # Create new image with target size and paste the generated image
    new_img = Image.new('RGB', target_size, color='white')
    
    # Calculate scaling to fit
    img_ratio = img.width / img.height
    target_ratio = target_size[0] / target_size[1]
    
    if img_ratio > target_ratio:
        # Image is wider than target
        new_width = target_size[0]
        new_height = int(target_size[0] / img_ratio)
    else:
        # Image is taller than target
        new_height = target_size[1]
        new_width = int(target_size[1] * img_ratio)
    
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Center the image
    x = (target_size[0] - new_width) // 2
    y = (target_size[1] - new_height) // 2
    
    new_img.paste(img_resized, (x, y))
    
    return new_img

def generate_social_caption(api_key, content_idea, platform, tone, include_hashtags, include_cta):
    """Generate social media caption using GPT"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        platform_info = PLATFORMS[platform]
        
        prompt = f"""Create an engaging social media caption for {platform}.

Content Idea: {content_idea}
Tone: {tone}
Character Limit: {platform_info['char_limit']} characters
Hashtag Limit: {platform_info['hashtag_limit']} hashtags

Requirements:
- Write in a {tone.lower()} tone
- Keep it under {platform_info['char_limit']} characters
- Make it engaging and platform-appropriate
{'- Include ' + str(platform_info['hashtag_limit']) + ' relevant hashtags at the end' if include_hashtags else '- Do NOT include hashtags'}
{'- Include a clear call-to-action' if include_cta else ''}
- Use emojis strategically (2-4 emojis)
- Make it shareable and conversation-starting

Just provide the caption text, nothing else."""

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert social media manager who creates viral, engaging content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        caption = response.choices[0].message.content.strip()
        tokens = response.usage.total_tokens
        
        return caption, tokens, None
        
    except Exception as e:
        return None, 0, f"❌ Error generating caption: {str(e)}"

def create_composite_post(image, caption, platform):
    """Create a visual representation of a social media post"""
    # This creates a mockup showing both image and caption together
    platform_info = PLATFORMS[platform]
    
    # Create canvas
    post_width = 600
    image_height = int(post_width * (image.height / image.width))
    caption_height = 200
    total_height = image_height + caption_height + 100
    
    canvas = Image.new('RGB', (post_width, total_height), color='white')
    
    # Resize and paste image
    img_resized = image.resize((post_width, image_height), Image.Resampling.LANCZOS)
    canvas.paste(img_resized, (0, 50))
    
    # Add platform header
    draw = ImageDraw.Draw(canvas)
    
    # Platform name at top
    header_text = f"{platform_info['emoji']} {platform}"
    draw.text((20, 15), header_text, fill=platform_info['color'], font=None)
    
    return canvas

def image_to_base64(img):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def calculate_dalle_cost(size, quality):
    """Calculate DALL-E 3 cost"""
    costs = {
        "1024x1024": {"standard": 0.040, "hd": 0.080},
        "1024x1792": {"standard": 0.080, "hd": 0.120},
        "1792x1024": {"standard": 0.080, "hd": 0.120}
    }
    return costs.get(size, {}).get(quality, 0.040)

def calculate_gpt_cost(tokens):
    """Calculate GPT-4 cost"""
    # GPT-4-turbo pricing
    return (tokens * 0.01) / 1000

# ==================== MAIN APP ====================

def main():
    # Header
    st.markdown('<h1 class="main-header">🎨 AI Visual Studio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create Stunning Social Media Visuals & Captions with AI</p>', unsafe_allow_html=True)
    
    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key Input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key with DALL-E 3 access"
        )
        
        if api_key:
            st.success("✅ API Key loaded")
        else:
            st.warning("⚠️ Please enter your API key")
        
        st.divider()
        
        # Image Settings
        st.subheader("🖼️ Image Settings")
        
        image_quality = st.radio(
            "Image Quality",
            ["standard", "hd"],
            help="HD costs 2x more but produces higher quality"
        )
        
        image_style = st.radio(
            "Image Style",
            ["vivid", "natural"],
            help="Vivid = more dramatic, Natural = more realistic"
        )
        
        st.divider()
        
        # Caption Settings
        st.subheader("✍️ Caption Settings")
        
        include_hashtags = st.checkbox("Include Hashtags", value=True)
        include_cta = st.checkbox("Include Call-to-Action", value=True)
        include_emojis = st.checkbox("Use Emojis", value=True)
        
        st.divider()
        
        # Information
        st.subheader("ℹ️ About")
        st.info("""
        **AI Visual Studio** creates complete social media posts with:
        - AI-generated images (DALL-E 3)
        - Optimized captions (GPT-4)
        - Platform-specific formatting
        - Ready-to-post content
        """)
        
        st.divider()
        
        # Tips
        with st.expander("💡 Pro Tips"):
            st.markdown("""
            **Image Prompts:**
            - Be specific and descriptive
            - Mention style (realistic, cartoon, etc.)
            - Include colors and mood
            - Specify composition
            
            **Caption Ideas:**
            - Focus on value proposition
            - Use storytelling
            - Ask questions to drive engagement
            - Test different CTAs
            """)
    
    # ==================== MAIN CONTENT AREA ====================
    
    # Initialize session state
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    if 'generated_caption' not in st.session_state:
        st.session_state.generated_caption = None
    if 'image_cost' not in st.session_state:
        st.session_state.image_cost = 0
    if 'caption_tokens' not in st.session_state:
        st.session_state.caption_tokens = 0
    if 'revised_prompt' not in st.session_state:
        st.session_state.revised_prompt = None
    
    # Configuration Section
    st.header("📋 Content Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Platform & Size")
        
        platform = st.selectbox(
            "Select Platform",
            list(PLATFORMS.keys()),
            help="Choose your target social media platform"
        )
        
        banner_size_name = st.selectbox(
            "Banner Size",
            list(BANNER_SIZES.keys()),
            help="Select the size for your banner/image"
        )
        
        # Custom size inputs
        if banner_size_name == "Custom Size":
            col_w, col_h = st.columns(2)
            with col_w:
                custom_width = st.number_input("Width (px)", min_value=64, max_value=2048, value=1080)
            with col_h:
                custom_height = st.number_input("Height (px)", min_value=64, max_value=2048, value=1080)
            banner_size = (custom_width, custom_height)
        else:
            banner_size = BANNER_SIZES[banner_size_name]
        
        # Map to DALL-E sizes
        if banner_size[0] and banner_size[1]:
            aspect_ratio = banner_size[0] / banner_size[1]
            if aspect_ratio == 1:
                dalle_size = "1024x1024"
            elif aspect_ratio > 1:
                dalle_size = "1792x1024"
            else:
                dalle_size = "1024x1792"
        else:
            dalle_size = "1024x1024"
        
        st.caption(f"DALL-E will generate: {dalle_size}")
    
    with col2:
        st.subheader("💡 Content Details")
        
        content_idea = st.text_area(
            "Content Idea / Description",
            placeholder="e.g., A modern coffee shop with morning sunlight, cozy atmosphere, perfect for promoting our new breakfast menu",
            height=100,
            help="Describe what you want to create"
        )
        
        tone = st.selectbox(
            "Caption Tone",
            ["Friendly", "Professional", "Inspirational", "Humorous", "Educational", "Promotional"],
            help="The tone for your social media caption"
        )
    
    st.divider()
    
    # Image Prompt Section
    st.subheader("🎨 Image Generation Prompt")
    
    image_prompt = st.text_area(
        "Detailed Image Prompt",
        placeholder="e.g., A photorealistic image of a cozy modern coffee shop interior with warm morning sunlight streaming through large windows, wooden furniture, plants, people enjoying coffee, warm color palette, professional photography style",
        height=120,
        help="Be specific about style, colors, mood, and composition"
    )
    
    st.caption("💡 Tip: DALL-E 3 works best with detailed, descriptive prompts mentioning style, colors, and mood")
    
    # Generate Button
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        generate_button = st.button("🚀 Generate Complete Post", use_container_width=True, type="primary")
    
    # Generate content
    if generate_button:
        if not api_key:
            st.error("❌ Please enter your OpenAI API key in the sidebar")
        elif not image_prompt:
            st.error("❌ Please provide an image generation prompt")
        elif not content_idea:
            st.error("❌ Please describe your content idea for the caption")
        else:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Generate Image
            status_text.text("🎨 Generating image with DALL-E 3...")
            progress_bar.progress(25)
            
            image, revised_prompt, error = generate_image_dalle(
                api_key, image_prompt, dalle_size, image_quality, image_style
            )
            
            if error:
                st.error(error)
                progress_bar.empty()
                status_text.empty()
            else:
                # Resize to target size
                if banner_size != (None, None):
                    image = resize_image(image, banner_size)
                
                st.session_state.generated_image = image
                st.session_state.revised_prompt = revised_prompt
                st.session_state.image_cost = calculate_dalle_cost(dalle_size, image_quality)
                
                progress_bar.progress(50)
                
                # Step 2: Generate Caption
                status_text.text("✍️ Creating social media caption with GPT-4...")
                progress_bar.progress(75)
                
                caption, tokens, error = generate_social_caption(
                    api_key, content_idea, platform, tone, include_hashtags, include_cta
                )
                
                if error:
                    st.error(error)
                    progress_bar.empty()
                    status_text.empty()
                else:
                    st.session_state.generated_caption = caption
                    st.session_state.caption_tokens = tokens
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Post generated successfully!")
                    
                    # Clear progress after 1 second
                    import time
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("🎉 Your social media post is ready!")
                    st.rerun()
    
    # Display Generated Content
    if st.session_state.generated_image and st.session_state.generated_caption:
        st.divider()
        st.header("📱 Your Social Media Post")
        
        # Two column layout for image and caption
        col_img, col_caption = st.columns([1, 1])
        
        with col_img:
            st.subheader("🖼️ Generated Image")
            
            # Display image in a nice container
            st.markdown('<div class="preview-container">', unsafe_allow_html=True)
            st.image(st.session_state.generated_image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Image info
            img = st.session_state.generated_image
            st.caption(f"📐 Size: {img.width}x{img.height} pixels")
            
            # Download image button
            img_byte_arr = io.BytesIO()
            st.session_state.generated_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            st.download_button(
                label="📥 Download Image",
                data=img_byte_arr,
                file_name=f"social_media_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png",
                use_container_width=True
            )
            
            # Show revised prompt
            if st.session_state.revised_prompt:
                with st.expander("🔍 DALL-E Revised Prompt"):
                    st.info(st.session_state.revised_prompt)
        
        with col_caption:
            st.subheader(f"✍️ {platform} Caption")
            
            # Display caption in a social media-style box
            st.markdown('<div class="social-post-box">', unsafe_allow_html=True)
            
            platform_info = PLATFORMS[platform]
            st.markdown(f"### {platform_info['emoji']} {platform}")
            
            # Editable caption
            edited_caption = st.text_area(
                "Caption (editable)",
                value=st.session_state.generated_caption,
                height=300,
                help="You can edit the caption before posting"
            )
            
            st.session_state.generated_caption = edited_caption
            
            # Character count
            char_count = len(edited_caption)
            char_limit = platform_info['char_limit']
            
            if char_count > char_limit:
                st.error(f"⚠️ Caption is {char_count - char_limit} characters over the {platform} limit!")
            else:
                st.success(f"✅ {char_count}/{char_limit} characters")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Copy to clipboard helper
            st.code(edited_caption, language=None)
            
            # Download caption
            st.download_button(
                label="📥 Download Caption",
                data=edited_caption,
                file_name=f"caption_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Action Buttons
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Regenerate Both", use_container_width=True):
                st.session_state.generated_image = None
                st.session_state.generated_caption = None
                st.rerun()
        
        with col2:
            if st.button("🎨 Regenerate Image", use_container_width=True):
                if image_prompt:
                    with st.spinner("Generating new image..."):
                        image, revised_prompt, error = generate_image_dalle(
                            api_key, image_prompt, dalle_size, image_quality, image_style
                        )
                        if not error:
                            if banner_size != (None, None):
                                image = resize_image(image, banner_size)
                            st.session_state.generated_image = image
                            st.session_state.revised_prompt = revised_prompt
                            st.rerun()
        
        with col3:
            if st.button("✍️ Regenerate Caption", use_container_width=True):
                if content_idea:
                    with st.spinner("Generating new caption..."):
                        caption, tokens, error = generate_social_caption(
                            api_key, content_idea, platform, tone, include_hashtags, include_cta
                        )
                        if not error:
                            st.session_state.generated_caption = caption
                            st.session_state.caption_tokens = tokens
                            st.rerun()
        
        with col4:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.generated_image = None
                st.session_state.generated_caption = None
                st.session_state.image_cost = 0
                st.session_state.caption_tokens = 0
                st.rerun()
        
        # Cost Summary
        st.divider()
        st.subheader("💰 Cost Summary")
        
        st.markdown('<div class="cost-info">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Image Cost (DALL-E)", f"${st.session_state.image_cost:.4f}")
        
        with col2:
            caption_cost = calculate_gpt_cost(st.session_state.caption_tokens)
            st.metric("Caption Cost (GPT-4)", f"${caption_cost:.4f}")
        
        with col3:
            total_cost = st.session_state.image_cost + caption_cost
            st.metric("Total Cost", f"${total_cost:.4f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Platform-specific tips
        with st.expander(f"📊 {platform} Best Practices"):
            platform_info = PLATFORMS[platform]
            st.markdown(f"""
            **{platform} Posting Guidelines:**
            - **Character Limit**: {platform_info['char_limit']:,} characters
            - **Recommended Hashtags**: {platform_info['hashtag_limit']} hashtags
            - **Best Times**: Varies by audience (use analytics)
            - **Engagement Tips**: 
                - Post consistently
                - Use high-quality visuals
                - Engage with comments quickly
                - Track performance metrics
            """)
    
    # Sample Templates Section
    if not st.session_state.generated_image:
        st.divider()
        st.header("💡 Example Content Ideas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🍕 Food & Restaurant**
            - New menu item launch
            - Behind-the-scenes kitchen
            - Customer testimonials
            - Special offers
            """)
        
        with col2:
            st.markdown("""
            **💼 Business & Tech**
            - Product announcements
            - Company milestones
            - Team highlights
            - Industry insights
            """)
        
        with col3:
            st.markdown("""
            **🎨 Creative & Lifestyle**
            - Personal stories
            - Tips and tutorials
            - Before/after transformations
            - Event promotions
            """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div class="footer">Built with ❤️ using Streamlit, OpenAI DALL-E 3 & GPT-4 | © 2025 AI Visual Studio</div>',
        unsafe_allow_html=True
    )

# ==================== RUN APP ====================
if __name__ == "__main__":
    main()
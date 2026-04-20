#!/usr/bin/env python3
"""
Generate Perceptual Validation (Level 3) eval set for E²-Bench.
Creates HTML pages with planted UI/UX bugs that humans can easily spot.
Each task has: a correct HTML, a bugged HTML, bug descriptions, and metadata.
"""

import json
import os
import random
import copy

OUTPUT_DIR = "/home/ubuntu/e2_bench/eval_set/perceptual_validation"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# Bug injection functions
# ============================================================

def make_base_pages():
    """Generate a set of diverse base HTML pages (correct versions)."""
    pages = []

    # --- Page 1: Landing Page ---
    pages.append({
        "id": "landing_01",
        "category": "landing_page",
        "description": "A startup landing page with hero section, features, and CTA button.",
        "html": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CloudSync - Sync Everything</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }
.hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center; }
.hero h1 { font-size: 48px; margin-bottom: 16px; }
.hero p { font-size: 20px; margin-bottom: 32px; max-width: 600px; margin-left: auto; margin-right: auto; }
.btn { display: inline-block; background: #ff6b6b; color: white; padding: 16px 40px; border-radius: 8px; text-decoration: none; font-size: 18px; font-weight: bold; cursor: pointer; border: none; }
.btn:hover { background: #ee5a5a; }
.features { display: flex; justify-content: center; gap: 40px; padding: 60px 20px; max-width: 1000px; margin: 0 auto; flex-wrap: wrap; }
.feature { text-align: center; flex: 1; min-width: 250px; }
.feature h3 { font-size: 22px; margin: 16px 0 8px; }
.feature p { font-size: 16px; color: #666; line-height: 1.6; }
.feature-icon { font-size: 48px; }
.footer { background: #2d3436; color: #b2bec3; padding: 30px 20px; text-align: center; font-size: 14px; }
</style></head><body>
<div class="hero">
  <h1>CloudSync</h1>
  <p>Seamlessly sync your files across all devices. Fast, secure, and reliable cloud storage for teams and individuals.</p>
  <button class="btn" onclick="alert('Sign up clicked!')">Get Started Free</button>
</div>
<div class="features">
  <div class="feature"><div class="feature-icon">⚡</div><h3>Lightning Fast</h3><p>Upload and sync files in seconds with our optimized infrastructure.</p></div>
  <div class="feature"><div class="feature-icon">🔒</div><h3>Bank-Level Security</h3><p>End-to-end encryption keeps your data safe and private.</p></div>
  <div class="feature"><div class="feature-icon">🌍</div><h3>Access Anywhere</h3><p>Available on web, desktop, and mobile. Your files follow you.</p></div>
</div>
<div class="footer">&copy; 2026 CloudSync Inc. All rights reserved.</div>
</body></html>"""
    })

    # --- Page 2: Dashboard ---
    pages.append({
        "id": "dashboard_01",
        "category": "dashboard",
        "description": "An analytics dashboard with stats cards, a chart placeholder, and a data table.",
        "html": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Analytics Dashboard</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; }
.header { background: white; padding: 16px 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 22px; color: #1a1a2e; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; padding: 24px; }
.stat-card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.stat-card .label { font-size: 14px; color: #666; margin-bottom: 8px; }
.stat-card .value { font-size: 32px; font-weight: bold; color: #1a1a2e; }
.stat-card .change { font-size: 14px; margin-top: 8px; }
.change.up { color: #27ae60; }
.change.down { color: #e74c3c; }
.chart-section { margin: 0 24px; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.chart-section h2 { font-size: 18px; margin-bottom: 16px; }
.chart-placeholder { height: 250px; background: linear-gradient(to right, #e8f4f8, #d4efdf); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #888; font-size: 16px; }
.table-section { margin: 24px; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }
th { font-weight: 600; color: #666; font-size: 13px; text-transform: uppercase; }
td { font-size: 14px; }
.status { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status.active { background: #d4efdf; color: #27ae60; }
.status.pending { background: #fdebd0; color: #e67e22; }
</style></head><body>
<div class="header"><h1>Analytics Dashboard</h1><span style="color:#666">Last updated: Apr 20, 2026</span></div>
<div class="stats">
  <div class="stat-card"><div class="label">Total Revenue</div><div class="value">$48,250</div><div class="change up">+12.5% from last month</div></div>
  <div class="stat-card"><div class="label">Active Users</div><div class="value">2,847</div><div class="change up">+8.3% from last month</div></div>
  <div class="stat-card"><div class="label">Conversion Rate</div><div class="value">3.24%</div><div class="change down">-0.4% from last month</div></div>
  <div class="stat-card"><div class="label">Avg. Session</div><div class="value">4m 32s</div><div class="change up">+15s from last month</div></div>
</div>
<div class="chart-section"><h2>Revenue Trend</h2><div class="chart-placeholder">📊 Chart visualization area</div></div>
<div class="table-section"><h2 style="margin-bottom:16px">Recent Transactions</h2>
<table><thead><tr><th>Customer</th><th>Amount</th><th>Date</th><th>Status</th></tr></thead>
<tbody>
<tr><td>Alice Johnson</td><td>$1,250.00</td><td>Apr 19, 2026</td><td><span class="status active">Completed</span></td></tr>
<tr><td>Bob Smith</td><td>$890.00</td><td>Apr 18, 2026</td><td><span class="status pending">Pending</span></td></tr>
<tr><td>Carol Williams</td><td>$2,100.00</td><td>Apr 17, 2026</td><td><span class="status active">Completed</span></td></tr>
</tbody></table></div>
</body></html>"""
    })

    # --- Page 3: E-commerce Product Page ---
    pages.append({
        "id": "ecommerce_01",
        "category": "ecommerce",
        "description": "A product detail page with image, price, description, and add-to-cart button.",
        "html": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Premium Headphones - ShopNow</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: #fafafa; }
.nav { background: #1a1a2e; color: white; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
.nav h1 { font-size: 20px; }
.nav-links { display: flex; gap: 24px; }
.nav-links a { color: #ddd; text-decoration: none; font-size: 14px; }
.product { display: flex; max-width: 1000px; margin: 40px auto; gap: 40px; padding: 0 20px; }
.product-image { flex: 1; background: #e8e8e8; border-radius: 12px; height: 400px; display: flex; align-items: center; justify-content: center; font-size: 80px; }
.product-info { flex: 1; }
.product-info h2 { font-size: 28px; margin-bottom: 8px; }
.rating { color: #f39c12; font-size: 18px; margin-bottom: 16px; }
.price { font-size: 36px; font-weight: bold; color: #e74c3c; margin-bottom: 16px; }
.price .original { font-size: 20px; color: #999; text-decoration: line-through; margin-left: 12px; }
.description { font-size: 16px; color: #555; line-height: 1.8; margin-bottom: 24px; }
.add-to-cart { background: #27ae60; color: white; border: none; padding: 16px 48px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; }
.add-to-cart:hover { background: #219a52; }
.specs { margin-top: 24px; }
.specs h3 { font-size: 18px; margin-bottom: 12px; }
.specs table { width: 100%; }
.specs td { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 14px; }
.specs td:first-child { color: #888; width: 40%; }
</style></head><body>
<div class="nav"><h1>ShopNow</h1><div class="nav-links"><a href="#">Home</a><a href="#">Categories</a><a href="#">Cart (2)</a></div></div>
<div class="product">
  <div class="product-image">🎧</div>
  <div class="product-info">
    <h2>Premium Wireless Headphones</h2>
    <div class="rating">★★★★★ (4.8) · 1,247 reviews</div>
    <div class="price">$79.99 <span class="original">$129.99</span></div>
    <div class="description">Experience crystal-clear audio with our premium wireless headphones. Featuring active noise cancellation, 30-hour battery life, and ultra-comfortable memory foam ear cushions.</div>
    <button class="add-to-cart" onclick="alert('Added to cart!')">Add to Cart</button>
    <div class="specs"><h3>Specifications</h3>
    <table><tr><td>Driver Size</td><td>40mm</td></tr><tr><td>Battery Life</td><td>30 hours</td></tr><tr><td>Connectivity</td><td>Bluetooth 5.3</td></tr><tr><td>Weight</td><td>250g</td></tr></table></div>
  </div>
</div>
</body></html>"""
    })

    # --- Page 4: Blog Post ---
    pages.append({
        "id": "blog_01",
        "category": "blog",
        "description": "A blog article page with header, content, author info, and sidebar.",
        "html": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Future of AI in Healthcare - TechBlog</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; background: #fff; color: #333; }
.site-header { border-bottom: 3px solid #333; padding: 20px 0; text-align: center; }
.site-header h1 { font-size: 32px; letter-spacing: 2px; }
.container { display: flex; max-width: 1000px; margin: 40px auto; gap: 40px; padding: 0 20px; }
.main { flex: 2; }
.sidebar { flex: 1; }
.article-title { font-size: 36px; line-height: 1.3; margin-bottom: 16px; }
.article-meta { color: #888; font-size: 14px; margin-bottom: 32px; font-family: 'Segoe UI', sans-serif; }
.article-body p { font-size: 18px; line-height: 1.8; margin-bottom: 24px; }
.article-body h2 { font-size: 26px; margin: 32px 0 16px; }
.author-box { display: flex; align-items: center; gap: 16px; padding: 24px; background: #f8f9fa; border-radius: 8px; margin-top: 40px; }
.author-avatar { width: 64px; height: 64px; border-radius: 50%; background: #667eea; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-family: sans-serif; }
.author-name { font-size: 18px; font-weight: bold; }
.author-bio { font-size: 14px; color: #666; font-family: sans-serif; }
.sidebar-widget { background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 24px; }
.sidebar-widget h3 { font-size: 16px; margin-bottom: 12px; font-family: sans-serif; text-transform: uppercase; letter-spacing: 1px; }
.sidebar-widget ul { list-style: none; }
.sidebar-widget li { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 15px; }
.sidebar-widget li a { color: #333; text-decoration: none; }
</style></head><body>
<div class="site-header"><h1>TECHBLOG</h1></div>
<div class="container">
  <div class="main">
    <h1 class="article-title">The Future of AI in Healthcare: Promises and Challenges</h1>
    <div class="article-meta">By Dr. Sarah Chen · April 15, 2026 · 8 min read</div>
    <div class="article-body">
      <p>Artificial intelligence is transforming healthcare at an unprecedented pace. From diagnostic imaging to drug discovery, AI systems are augmenting the capabilities of medical professionals worldwide.</p>
      <h2>Diagnostic Imaging</h2>
      <p>Deep learning models have shown remarkable accuracy in detecting conditions from medical images. Studies have demonstrated that AI can match or exceed radiologist performance in detecting certain cancers, with sensitivity rates above 94%.</p>
      <h2>Drug Discovery</h2>
      <p>The traditional drug development pipeline takes 10-15 years and costs billions. AI is compressing this timeline by predicting molecular interactions and identifying promising candidates faster than ever before.</p>
      <p>However, significant challenges remain. Data privacy, algorithmic bias, and the need for regulatory frameworks continue to be active areas of discussion in the medical AI community.</p>
    </div>
    <div class="author-box">
      <div class="author-avatar">SC</div>
      <div><div class="author-name">Dr. Sarah Chen</div><div class="author-bio">AI researcher and healthcare technology consultant with 15 years of experience.</div></div>
    </div>
  </div>
  <div class="sidebar">
    <div class="sidebar-widget"><h3>Popular Posts</h3><ul><li><a href="#">Understanding Transformer Architecture</a></li><li><a href="#">5 Python Libraries Every Data Scientist Needs</a></li><li><a href="#">The Ethics of Autonomous Vehicles</a></li></ul></div>
    <div class="sidebar-widget"><h3>Categories</h3><ul><li><a href="#">Artificial Intelligence (24)</a></li><li><a href="#">Machine Learning (18)</a></li><li><a href="#">Healthcare Tech (12)</a></li><li><a href="#">Data Science (31)</a></li></ul></div>
  </div>
</div>
</body></html>"""
    })

    # --- Page 5: Contact Form ---
    pages.append({
        "id": "form_01",
        "category": "form",
        "description": "A contact form page with input fields, validation, and submit button.",
        "html": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Contact Us - Acme Corp</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.form-container { background: white; border-radius: 16px; padding: 48px; max-width: 500px; width: 100%; box-shadow: 0 4px 24px rgba(0,0,0,0.1); }
.form-container h1 { font-size: 28px; margin-bottom: 8px; }
.form-container .subtitle { color: #666; font-size: 16px; margin-bottom: 32px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; color: #333; }
.form-group input, .form-group textarea, .form-group select { width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; transition: border-color 0.2s; }
.form-group input:focus, .form-group textarea:focus, .form-group select:focus { outline: none; border-color: #667eea; }
.form-group textarea { height: 120px; resize: vertical; }
.submit-btn { width: 100%; background: #667eea; color: white; border: none; padding: 14px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; }
.submit-btn:hover { background: #5a6fd6; }
.required { color: #e74c3c; }
</style></head><body>
<div class="form-container">
  <h1>Contact Us</h1>
  <p class="subtitle">We'd love to hear from you. Send us a message!</p>
  <form onsubmit="alert('Form submitted!'); return false;">
    <div class="form-group"><label>Full Name <span class="required">*</span></label><input type="text" placeholder="John Doe" required></div>
    <div class="form-group"><label>Email Address <span class="required">*</span></label><input type="email" placeholder="john@example.com" required></div>
    <div class="form-group"><label>Subject</label>
      <select><option>General Inquiry</option><option>Technical Support</option><option>Sales</option><option>Partnership</option></select>
    </div>
    <div class="form-group"><label>Message <span class="required">*</span></label><textarea placeholder="Tell us how we can help..." required></textarea></div>
    <button type="submit" class="submit-btn">Send Message</button>
  </form>
</div>
</body></html>"""
    })

    return pages


# ============================================================
# Bug templates: each is a function that takes HTML and returns (bugged_html, bug_description, bug_type, severity)
# ============================================================

BUG_TEMPLATES = []

def register_bug(func):
    BUG_TEMPLATES.append(func)
    return func

# --- Perceptual bugs: things humans spot instantly ---

@register_bug
def bug_image_stretch(html):
    """Stretch an element to wrong aspect ratio"""
    inject = ".product-image { height: 400px; width: 150px !important; }"
    if ".product-image" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "Product image area is severely stretched (150px wide, 400px tall), creating an unnatural distorted aspect ratio.",
        "aspect_ratio_distortion",
        "high"
    )

@register_bug
def bug_text_overflow(html):
    """Text overflows its container"""
    inject = ".hero h1 { white-space: nowrap; font-size: 120px; overflow: visible; }"
    if ".hero h1" not in html or ".hero" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "The hero title text is set to 120px with no wrapping, causing it to overflow horizontally beyond the viewport.",
        "text_overflow",
        "high"
    )

@register_bug
def bug_invisible_text(html):
    """White text on white background"""
    inject = ".description { color: #fafafa !important; }"
    if ".description" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "Product description text color (#fafafa) is nearly identical to the background (#fafafa), making it invisible to users.",
        "contrast_failure",
        "critical"
    )

@register_bug
def bug_button_no_action(html):
    """Button onclick removed - clicking does nothing"""
    if 'onclick="alert(' not in html:
        return None
    bugged = html.replace('onclick="alert(\'Sign up clicked!\')"', '').replace('onclick="alert(\'Added to cart!\')"', '')
    if bugged == html:
        return None
    return (
        bugged,
        "The primary call-to-action button has no onclick handler, so clicking it does nothing.",
        "broken_interaction",
        "critical"
    )

@register_bug
def bug_overlapping_elements(html):
    """Elements overlap each other"""
    inject = ".stat-card:nth-child(2) { position: absolute; left: 24px; top: 100px; z-index: 10; }"
    if ".stat-card" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "The second stats card uses absolute positioning, causing it to overlap with the first card and break the grid layout.",
        "element_overlap",
        "high"
    )

@register_bug
def bug_tiny_font(html):
    """Critical text rendered in unreadably small font"""
    inject = ".price { font-size: 8px !important; }"
    if ".price" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "The product price is displayed at 8px font size, making it virtually unreadable.",
        "unreadable_text",
        "high"
    )

@register_bug
def bug_broken_layout_flex(html):
    """Flex layout direction reversed, breaking visual flow"""
    inject = ".product { flex-direction: column-reverse !important; }"
    if ".product {" not in html or "display: flex" not in html.split(".product")[1][:200]:
        # Try another approach
        if ".product" not in html:
            return None
    return (
        html.replace(".product {", ".product { flex-direction: column-reverse !important; "),
        "Product layout uses column-reverse, placing product info above the image in reverse order, breaking the expected visual hierarchy.",
        "layout_broken",
        "medium"
    )

@register_bug
def bug_form_submit_prevented(html):
    """Form submit does nothing - return false without alert"""
    if 'onsubmit="alert(' not in html:
        return None
    return (
        html.replace('onsubmit="alert(\'Form submitted!\'); return false;"', 'onsubmit="return false;"'),
        "The form's onsubmit handler only returns false without any feedback, so users click submit and nothing visibly happens.",
        "broken_interaction",
        "critical"
    )

@register_bug
def bug_z_index_footer_on_top(html):
    """Footer overlays content"""
    inject = ".footer { position: fixed; top: 0; left: 0; right: 0; z-index: 9999; }"
    if ".footer" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "The footer is fixed to the top of the viewport with high z-index, permanently covering the header and hero section.",
        "element_overlap",
        "critical"
    )

@register_bug
def bug_horizontal_scroll(html):
    """Content causes unwanted horizontal scrollbar"""
    inject = ".features { width: 2000px; }"
    if ".features" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "The features section is set to 2000px width, causing a horizontal scrollbar on the page.",
        "layout_broken",
        "medium"
    )

@register_bug
def bug_misaligned_grid(html):
    """Grid columns don't match content"""
    if "grid-template-columns: repeat(4, 1fr)" not in html:
        return None
    return (
        html.replace("grid-template-columns: repeat(4, 1fr)", "grid-template-columns: repeat(7, 1fr)"),
        "Stats grid uses 7 columns for only 4 cards, leaving 3 empty columns and making cards too narrow.",
        "layout_broken",
        "medium"
    )

@register_bug
def bug_cut_off_content(html):
    """Content is cut off by overflow hidden"""
    inject = ".article-body { max-height: 100px; overflow: hidden; }"
    if ".article-body" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "Article body is limited to 100px height with overflow hidden, cutting off most of the article content without any 'read more' indicator.",
        "content_truncation",
        "critical"
    )

@register_bug
def bug_wrong_color_scheme(html):
    """Jarring color that doesn't match the design"""
    inject = ".nav { background: #ff00ff !important; } .nav h1 { color: #00ff00 !important; }"
    if ".nav" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "Navigation bar uses clashing magenta background (#ff00ff) with green text (#00ff00), creating a visually jarring and unprofessional appearance.",
        "color_scheme_broken",
        "medium"
    )

@register_bug
def bug_table_misalignment(html):
    """Table headers don't match data columns"""
    if "<th>Customer</th><th>Amount</th><th>Date</th><th>Status</th>" not in html:
        return None
    return (
        html.replace("<th>Customer</th><th>Amount</th><th>Date</th><th>Status</th>",
                     "<th>Customer</th><th>Date</th><th>Amount</th><th>Status</th>"),
        "Table headers 'Amount' and 'Date' are swapped, but the data rows remain in the original order, causing a mismatch between headers and data.",
        "data_mismatch",
        "high"
    )

@register_bug
def bug_sidebar_overlaps_main(html):
    """Sidebar overlaps main content"""
    inject = ".sidebar { position: absolute; left: 0; top: 200px; }"
    if ".sidebar" not in html:
        return None
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "Sidebar uses absolute positioning at left:0, causing it to overlap with the main article content instead of sitting beside it.",
        "element_overlap",
        "high"
    )

@register_bug
def bug_input_disabled(html):
    """Form inputs are disabled"""
    if '<input type="text"' not in html:
        return None
    return (
        html.replace('<input type="text"', '<input type="text" disabled').replace('<input type="email"', '<input type="email" disabled').replace('<textarea', '<textarea disabled'),
        "All form input fields are disabled, preventing users from entering any information.",
        "broken_interaction",
        "critical"
    )

@register_bug
def bug_upside_down(html):
    """Content is rotated 180 degrees"""
    inject = "body { transform: rotate(180deg); }"
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "The entire page body is rotated 180 degrees, rendering all content upside down.",
        "layout_broken",
        "critical"
    )

@register_bug
def bug_missing_padding(html):
    """All padding removed, content jammed against edges"""
    inject = "* { padding: 0 !important; margin: 0 !important; }"
    return (
        html.replace("</style>", f"{inject}\n</style>"),
        "All padding and margins are forcibly removed from every element, causing text and elements to jam against container edges with no spacing.",
        "spacing_broken",
        "high"
    )


def generate_tasks():
    """Generate the full perceptual validation eval set."""
    pages = make_base_pages()
    tasks = []
    task_id = 0

    for page in pages:
        for bug_func in BUG_TEMPLATES:
            result = bug_func(page["html"])
            if result is None:
                continue

            bugged_html, bug_desc, bug_type, severity = result
            task_id += 1
            tasks.append({
                "id": f"perceptual_{task_id:03d}",
                "category": page["category"],
                "page_id": page["id"],
                "page_description": page["description"],
                "bug_type": bug_type,
                "severity": severity,
                "bugged_html": bugged_html,
                "correct_html": page["html"],
                "planted_bugs": [bug_desc],
                "num_bugs": 1,
                "ground_truth": {
                    "has_bugs": True,
                    "bug_descriptions": [bug_desc],
                    "bug_types": [bug_type]
                }
            })

    # Also add some correct pages (no bugs) as negative samples
    for page in pages:
        task_id += 1
        tasks.append({
            "id": f"perceptual_{task_id:03d}",
            "category": page["category"],
            "page_id": page["id"],
            "page_description": page["description"],
            "bug_type": "none",
            "severity": "none",
            "bugged_html": page["html"],  # same as correct - no bug
            "correct_html": page["html"],
            "planted_bugs": [],
            "num_bugs": 0,
            "ground_truth": {
                "has_bugs": False,
                "bug_descriptions": [],
                "bug_types": []
            }
        })

    # Add multi-bug tasks (2-3 bugs combined)
    for page in pages:
        applicable_bugs = []
        for bug_func in BUG_TEMPLATES:
            result = bug_func(page["html"])
            if result is not None:
                applicable_bugs.append((bug_func, result))

        if len(applicable_bugs) >= 2:
            # Create 3 multi-bug variants per page
            for combo_idx in range(min(3, len(applicable_bugs) - 1)):
                random.seed(42 + task_id + combo_idx)
                selected = random.sample(applicable_bugs, min(2, len(applicable_bugs)))

                combined_html = page["html"]
                all_descs = []
                all_types = []
                for _, (bugged, desc, btype, sev) in selected:
                    # Extract the CSS injection from each bug
                    diff = bugged.replace(page["html"], "")
                    if diff:
                        # Try to apply the CSS change
                        for line in diff.strip().split("\n"):
                            if line.strip():
                                combined_html = combined_html.replace("</style>", f"{line}\n</style>")
                    all_descs.append(desc)
                    all_types.append(btype)

                task_id += 1
                tasks.append({
                    "id": f"perceptual_{task_id:03d}",
                    "category": page["category"],
                    "page_id": page["id"],
                    "page_description": page["description"],
                    "bug_type": "multiple",
                    "severity": "high",
                    "bugged_html": combined_html,
                    "correct_html": page["html"],
                    "planted_bugs": all_descs,
                    "num_bugs": len(all_descs),
                    "ground_truth": {
                        "has_bugs": True,
                        "bug_descriptions": all_descs,
                        "bug_types": all_types
                    }
                })

    random.seed(42)
    random.shuffle(tasks)

    print(f"Generated {len(tasks)} perceptual validation tasks")
    print(f"  - Single bug tasks: {sum(1 for t in tasks if t['num_bugs'] == 1)}")
    print(f"  - Multi-bug tasks: {sum(1 for t in tasks if t['num_bugs'] > 1)}")
    print(f"  - No-bug tasks: {sum(1 for t in tasks if t['num_bugs'] == 0)}")

    with open(os.path.join(OUTPUT_DIR, "tasks.json"), "w") as f:
        json.dump(tasks, f, indent=2)

    print(f"Saved to {OUTPUT_DIR}/tasks.json")
    return tasks


if __name__ == "__main__":
    generate_tasks()

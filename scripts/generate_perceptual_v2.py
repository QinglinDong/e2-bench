#!/usr/bin/env python3
"""
E²-Bench Perceptual Validation Task Generator v2
Generates HTML pages with planted UI/UX bugs that humans can easily spot.
"""

import json
import random
import os

random.seed(42)

# ============================================================
# Bug Templates: Each generates a correct + bugged HTML pair
# ============================================================

def make_page(title, body_content, extra_css=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #fff; }}
{extra_css}
</style>
</head>
<body>
{body_content}
</body>
</html>"""


TASKS = []
task_counter = [0]

def add_task(category, bug_type, severity, page_desc, correct_html, bugged_html, bugs_list):
    task_counter[0] += 1
    TASKS.append({
        "id": f"perceptual_{task_counter[0]:04d}",
        "category": category,
        "bug_type": bug_type,
        "severity": severity,
        "page_description": page_desc,
        "correct_html": correct_html,
        "bugged_html": bugged_html,
        "planted_bugs": bugs_list,
        "num_bugs": len(bugs_list),
        "ground_truth": bugs_list
    })

# ---- Category 1: Image Aspect Ratio / Sizing Issues ----

product_names = [
    ("Wireless Headphones", "Electronics", "$79.99"),
    ("Running Shoes", "Sports", "$129.99"),
    ("Coffee Maker", "Kitchen", "$49.99"),
    ("Leather Wallet", "Accessories", "$34.99"),
    ("Yoga Mat", "Fitness", "$24.99"),
    ("Desk Lamp", "Home Office", "$45.99"),
    ("Backpack", "Travel", "$59.99"),
    ("Water Bottle", "Sports", "$19.99"),
    ("Sunglasses", "Fashion", "$89.99"),
    ("Bluetooth Speaker", "Electronics", "$64.99"),
]

for i, (name, cat, price) in enumerate(product_names):
    card_css = """
.product-card { max-width: 320px; margin: 40px auto; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.product-img { width: 100%; height: 240px; object-fit: cover; background: #f5f5f5; display: flex; align-items: center; justify-content: center; color: #999; font-size: 14px; }
.product-info { padding: 16px; }
.product-info h2 { font-size: 18px; margin-bottom: 8px; }
.product-info .category { color: #888; font-size: 13px; margin-bottom: 12px; }
.product-info .price { font-size: 22px; font-weight: bold; color: #e44; }
.buy-btn { display: block; width: 100%; padding: 12px; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 12px; }
.buy-btn:hover { background: #1d4ed8; }
"""
    correct_body = f"""
<div class="product-card">
  <div class="product-img">[Product Image: {name}]</div>
  <div class="product-info">
    <h2>{name}</h2>
    <p class="category">{cat}</p>
    <p class="price">{price}</p>
    <button class="buy-btn">Add to Cart</button>
  </div>
</div>"""

    # Bug variant 1: stretched image
    if i < 5:
        bug_css = card_css.replace("height: 240px; object-fit: cover;", "height: 400px; object-fit: fill;")
        bugged_body = correct_body
        add_task("image_sizing", "stretched_image", "high",
                 f"Product card for {name} - image should be properly proportioned",
                 make_page(f"{name} - Shop", correct_body, card_css),
                 make_page(f"{name} - Shop", bugged_body, bug_css),
                 [f"Product image is stretched (height forced to 400px with object-fit: fill instead of cover, distorting the image)"])
    else:
        # Bug variant 2: tiny image
        bug_css = card_css.replace("height: 240px;", "height: 40px;")
        add_task("image_sizing", "tiny_image", "high",
                 f"Product card for {name} - image should be visible",
                 make_page(f"{name} - Shop", correct_body, card_css),
                 make_page(f"{name} - Shop", correct_body, bug_css),
                 [f"Product image is extremely small (height: 40px instead of 240px), barely visible"])


# ---- Category 2: Text Contrast / Readability Issues ----

contrast_pages = [
    ("Newsletter Signup", "#1a1a2e", "#2a2a3e", "Sign up for our weekly newsletter", "Get the latest updates delivered to your inbox."),
    ("Error Message", "#fff0f0", "#ffe0e0", "Payment Failed", "Your card was declined. Please try a different payment method."),
    ("Success Banner", "#f0fff0", "#e0ffe0", "Order Confirmed!", "Your order #12345 has been placed successfully."),
    ("Warning Notice", "#fffbeb", "#fff3cd", "Account Expiring Soon", "Your subscription expires in 3 days. Renew now to keep access."),
    ("Footer Info", "#1f2937", "#374151", "© 2026 TechCorp Inc.", "Privacy Policy | Terms of Service | Contact Us"),
    ("Cookie Banner", "#f8f9fa", "#e9ecef", "We use cookies", "This website uses cookies to improve your experience."),
    ("Promo Banner", "#7c3aed", "#6d28d9", "FLASH SALE - 50% OFF", "Limited time offer on all electronics."),
    ("Login Form", "#ffffff", "#f5f5f5", "Welcome Back", "Enter your credentials to continue."),
]

for i, (page_name, bg, bg2, heading, text) in enumerate(contrast_pages):
    correct_css = f"""
.banner {{ background: {bg}; padding: 40px; text-align: center; min-height: 200px; display: flex; flex-direction: column; justify-content: center; }}
.banner h1 {{ color: #ffffff; font-size: 28px; margin-bottom: 12px; }}
.banner p {{ color: #d1d5db; font-size: 16px; }}
"""
    # Bug: text color nearly same as background
    bugged_css = f"""
.banner {{ background: {bg}; padding: 40px; text-align: center; min-height: 200px; display: flex; flex-direction: column; justify-content: center; }}
.banner h1 {{ color: {bg2}; font-size: 28px; margin-bottom: 12px; }}
.banner p {{ color: {bg2}; font-size: 16px; }}
"""
    body = f"""
<div class="banner">
  <h1>{heading}</h1>
  <p>{text}</p>
</div>"""
    add_task("text_contrast", "low_contrast_text", "high",
             f"{page_name} page - text should be readable against background",
             make_page(page_name, body, correct_css),
             make_page(page_name, body, bugged_css),
             [f"Text color ({bg2}) is nearly identical to background color ({bg}), making text unreadable"])


# ---- Category 3: Button / Interactive Element Issues ----

button_scenarios = [
    ("Submit Form", "submit_btn", "Submit", "form"),
    ("Delete Account", "delete_btn", "Delete My Account", "danger"),
    ("Download Report", "download_btn", "Download PDF", "primary"),
    ("Save Changes", "save_btn", "Save", "success"),
    ("Cancel Order", "cancel_btn", "Cancel Order", "warning"),
    ("Send Message", "send_btn", "Send", "primary"),
    ("Apply Coupon", "coupon_btn", "Apply", "secondary"),
    ("Share Link", "share_btn", "Share", "outline"),
    ("Load More", "load_btn", "Load More Results", "primary"),
    ("Checkout", "checkout_btn", "Proceed to Checkout", "success"),
]

for label_name, btn_id, btn_text, style in button_scenarios:
    colors = {"form": "#2563eb", "danger": "#dc2626", "primary": "#2563eb", "success": "#16a34a", "warning": "#d97706", "secondary": "#6b7280", "outline": "#2563eb"}
    color = colors.get(style, "#2563eb")
    correct_css = f"""
.container {{ max-width: 480px; margin: 60px auto; padding: 24px; }}
.btn {{ display: inline-block; padding: 12px 32px; background: {color}; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }}
.btn:hover {{ opacity: 0.9; }}
"""
    # Bug: button is disabled / unclickable with no visual indication, or has pointer-events: none
    bugged_css = correct_css + "\n.btn { pointer-events: none; opacity: 0.4; }"
    body = f"""
<div class="container">
  <h2>{label_name}</h2>
  <p style="margin: 16px 0; color: #666;">Click the button below to proceed.</p>
  <button class="btn" id="{btn_id}">{btn_text}</button>
</div>"""
    add_task("button_issues", "unclickable_button", "critical",
             f"Page with '{btn_text}' button that should be clickable",
             make_page(label_name, body, correct_css),
             make_page(label_name, body, bugged_css),
             [f"Button '{btn_text}' appears disabled/grayed out (opacity: 0.4) and is unclickable (pointer-events: none) with no explanation"])


# ---- Category 4: Layout / Overflow Issues ----

overflow_scenarios = [
    ("User Profile", "Dr. Alexander Maximilian von Hohenzollern-Sigmaringen III", "Senior Distinguished Research Fellow at the International Institute of Advanced Computational Sciences"),
    ("Comment", "Anonymous", "This is a really long comment that should wrap properly but instead it overflows the container and breaks the layout making it look terrible and unprofessional and hard to read for anyone visiting the page"),
    ("Notification", "System", "Your subscription to the Premium Enterprise Plan with Advanced Analytics and Custom Reporting Features has been successfully renewed for another 12-month billing cycle"),
    ("Product Title", "Store", "Ultra-Premium Noise-Cancelling Over-Ear Wireless Bluetooth Headphones with Active Environmental Awareness Mode and 48-Hour Battery Life - Limited Edition Midnight Blue"),
    ("Email Subject", "Inbox", "Re: Re: Re: Fwd: URGENT - Q4 Financial Report Review Meeting Rescheduled to Next Monday - Please Confirm Your Attendance ASAP"),
    ("Navigation", "Menu", "Home | Products | Services | About Us | Contact | Blog | Careers | Partners | Investors | Press | Legal | Privacy | Terms"),
    ("Breadcrumb", "Nav", "Home > Electronics > Audio > Headphones > Wireless > Over-Ear > Noise-Cancelling > Premium > Limited Edition"),
    ("Table Cell", "Data", "Supercalifragilisticexpialidocious-pneumonoultramicroscopicsilicovolcanoconiosis-antidisestablishmentarianism"),
]

for title, author, long_text in overflow_scenarios:
    correct_css = """
.card { max-width: 400px; margin: 40px auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; }
.card h3 { font-size: 16px; margin-bottom: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card p { font-size: 14px; color: #666; word-wrap: break-word; overflow-wrap: break-word; line-height: 1.5; }
"""
    bugged_css = """
.card { max-width: 400px; margin: 40px auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 12px; }
.card h3 { font-size: 16px; margin-bottom: 8px; white-space: nowrap; }
.card p { font-size: 14px; color: #666; white-space: nowrap; }
"""
    body = f"""
<div class="card">
  <h3>{long_text}</h3>
  <p>By {author}</p>
</div>"""
    add_task("layout_overflow", "text_overflow", "high",
             f"{title} card with long text that should be properly contained",
             make_page(title, body, correct_css),
             make_page(title, body, bugged_css),
             [f"Text overflows the card container horizontally (no text wrapping, no ellipsis, no overflow: hidden), breaking the layout"])


# ---- Category 5: Broken/Missing Visual Elements ----

missing_element_pages = [
    ("E-commerce Header", "header", """
<header class="site-header">
  <div class="logo">ShopNow</div>
  <nav><a href="#">Home</a> <a href="#">Products</a> <a href="#">Cart (3)</a></nav>
  <div class="search"><input type="text" placeholder="Search products..."><button>Search</button></div>
</header>""", """
<header class="site-header">
  <div class="logo" style="display:none;">ShopNow</div>
  <nav><a href="#">Home</a> <a href="#">Products</a> <a href="#">Cart (3)</a></nav>
  <div class="search"><input type="text" placeholder="Search products..."><button>Search</button></div>
</header>""", ["Logo is hidden (display: none), leaving an empty space in the header"]),

    ("Pricing Table", "pricing", """
<div class="pricing">
  <div class="plan"><h3>Basic</h3><p class="price">$9/mo</p><ul><li>5 Projects</li><li>10GB Storage</li></ul><button>Choose Plan</button></div>
  <div class="plan featured"><h3>Pro</h3><p class="price">$29/mo</p><ul><li>Unlimited Projects</li><li>100GB Storage</li></ul><button>Choose Plan</button></div>
  <div class="plan"><h3>Enterprise</h3><p class="price">$99/mo</p><ul><li>Unlimited Everything</li><li>Priority Support</li></ul><button>Choose Plan</button></div>
</div>""", """
<div class="pricing">
  <div class="plan"><h3>Basic</h3><p class="price">$9/mo</p><ul><li>5 Projects</li><li>10GB Storage</li></ul><button>Choose Plan</button></div>
  <div class="plan featured"><h3>Pro</h3><p class="price"></p><ul><li>Unlimited Projects</li><li>100GB Storage</li></ul><button>Choose Plan</button></div>
  <div class="plan"><h3>Enterprise</h3><p class="price">$99/mo</p><ul><li>Unlimited Everything</li><li>Priority Support</li></ul><button>Choose Plan</button></div>
</div>""", ["Pro plan price is empty/missing - the most important plan has no price displayed"]),

    ("Dashboard Stats", "stats", """
<div class="stats-row">
  <div class="stat"><h4>Revenue</h4><p class="value">$124,500</p><p class="change positive">+12.5%</p></div>
  <div class="stat"><h4>Users</h4><p class="value">8,432</p><p class="change positive">+5.2%</p></div>
  <div class="stat"><h4>Orders</h4><p class="value">1,247</p><p class="change negative">-3.1%</p></div>
</div>""", """
<div class="stats-row">
  <div class="stat"><h4>Revenue</h4><p class="value">$124,500</p><p class="change positive">+12.5%</p></div>
  <div class="stat"><h4>Users</h4><p class="value">NaN</p><p class="change positive">+5.2%</p></div>
  <div class="stat"><h4>Orders</h4><p class="value">1,247</p><p class="change negative">-3.1%</p></div>
</div>""", ["Users stat shows 'NaN' instead of the actual number (8,432)"]),

    ("Navigation Bar", "nav", """
<nav class="navbar">
  <a href="/" class="nav-link active">Home</a>
  <a href="/about" class="nav-link">About</a>
  <a href="/services" class="nav-link">Services</a>
  <a href="/contact" class="nav-link">Contact</a>
</nav>""", """
<nav class="navbar">
  <a href="/" class="nav-link active">Home</a>
  <a href="/about" class="nav-link">About</a>
  <a href="/services" class="nav-link">Services</a>
  <a href="#" class="nav-link" style="color: transparent;">Contact</a>
</nav>""", ["Contact link text is invisible (color: transparent) - navigation item is missing visually"]),

    ("Footer", "footer", """
<footer class="site-footer">
  <div class="footer-col"><h4>Company</h4><a href="#">About</a><a href="#">Careers</a></div>
  <div class="footer-col"><h4>Support</h4><a href="#">Help Center</a><a href="#">Contact</a></div>
  <div class="footer-col"><h4>Legal</h4><a href="#">Privacy</a><a href="#">Terms</a></div>
  <p class="copyright">© 2026 TechCorp. All rights reserved.</p>
</footer>""", """
<footer class="site-footer">
  <div class="footer-col"><h4>Company</h4><a href="#">About</a><a href="#">Careers</a></div>
  <div class="footer-col"><h4>Support</h4><a href="#">Help Center</a><a href="#">Contact</a></div>
  <div class="footer-col"><h4>Legal</h4><a href="#">Privacy</a><a href="#">Terms</a></div>
  <p class="copyright"></p>
</footer>""", ["Copyright notice is empty - footer is missing the copyright text"]),

    ("Login Form", "login", """
<div class="login-form">
  <h2>Sign In</h2>
  <label for="email">Email</label>
  <input type="email" id="email" placeholder="you@example.com">
  <label for="password">Password</label>
  <input type="password" id="password" placeholder="Enter password">
  <button type="submit">Sign In</button>
  <a href="/forgot">Forgot password?</a>
</div>""", """
<div class="login-form">
  <h2>Sign In</h2>
  <label for="email">Email</label>
  <input type="email" id="email" placeholder="you@example.com">
  <label for="password">Password</label>
  <input type="text" id="password" placeholder="Enter password">
  <button type="submit">Sign In</button>
  <a href="/forgot">Forgot password?</a>
</div>""", ["Password field uses type='text' instead of type='password', exposing passwords in plain text"]),

    ("Search Results", "search", """
<div class="search-results">
  <div class="result"><h3><a href="#">Best Coffee Shops in NYC</a></h3><p>Discover the top-rated coffee shops across New York City...</p><span class="url">www.example.com/coffee-nyc</span></div>
  <div class="result"><h3><a href="#">Home Brewing Guide</a></h3><p>Learn how to brew the perfect cup at home...</p><span class="url">www.example.com/brewing</span></div>
  <div class="result"><h3><a href="#">Coffee Bean Reviews</a></h3><p>Expert reviews of the best coffee beans...</p><span class="url">www.example.com/reviews</span></div>
</div>""", """
<div class="search-results">
  <div class="result"><h3><a href="#">Best Coffee Shops in NYC</a></h3><p>Discover the top-rated coffee shops across New York City...</p><span class="url">www.example.com/coffee-nyc</span></div>
  <div class="result"><h3><a href="#">Best Coffee Shops in NYC</a></h3><p>Discover the top-rated coffee shops across New York City...</p><span class="url">www.example.com/coffee-nyc</span></div>
  <div class="result"><h3><a href="#">Coffee Bean Reviews</a></h3><p>Expert reviews of the best coffee beans...</p><span class="url">www.example.com/reviews</span></div>
</div>""", ["Second search result is a duplicate of the first result (same title, description, and URL)"]),

    ("Form Validation", "form", """
<div class="form-group">
  <label>Email Address</label>
  <input type="email" value="user@example.com" class="valid">
  <span class="feedback success">Valid email address</span>
</div>""", """
<div class="form-group">
  <label>Email Address</label>
  <input type="email" value="not-an-email" class="invalid">
  <span class="feedback success">Valid email address</span>
</div>""", ["Validation message says 'Valid email address' but the input contains 'not-an-email' which is invalid - contradictory feedback"]),
]

for page_name, css_class, correct_body, bugged_body, bugs in missing_element_pages:
    base_css = """
.site-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; background: #1f2937; color: white; }
.site-header .logo { font-size: 20px; font-weight: bold; }
.site-header nav a { color: #d1d5db; margin: 0 12px; text-decoration: none; }
.site-header .search input { padding: 6px 12px; border-radius: 4px; border: none; }
.site-header .search button { padding: 6px 12px; background: #2563eb; color: white; border: none; border-radius: 4px; margin-left: 4px; cursor: pointer; }
.pricing { display: flex; gap: 20px; justify-content: center; padding: 40px; }
.plan { border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; text-align: center; min-width: 200px; }
.plan.featured { border-color: #2563eb; box-shadow: 0 0 0 2px #2563eb; }
.plan h3 { margin-bottom: 12px; }
.plan .price { font-size: 28px; font-weight: bold; color: #2563eb; margin-bottom: 16px; }
.plan ul { list-style: none; margin-bottom: 16px; }
.plan li { padding: 4px 0; color: #666; }
.plan button { padding: 10px 24px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; }
.stats-row { display: flex; gap: 20px; padding: 24px; justify-content: center; }
.stat { background: #f8f9fa; padding: 20px; border-radius: 12px; text-align: center; min-width: 160px; }
.stat h4 { color: #888; font-size: 13px; margin-bottom: 8px; }
.stat .value { font-size: 28px; font-weight: bold; }
.stat .change { font-size: 14px; margin-top: 4px; }
.stat .change.positive { color: #16a34a; }
.stat .change.negative { color: #dc2626; }
.navbar { display: flex; gap: 24px; padding: 16px 24px; background: #f8f9fa; border-bottom: 1px solid #e0e0e0; }
.nav-link { text-decoration: none; color: #666; padding: 8px 16px; border-radius: 8px; }
.nav-link.active { background: #2563eb; color: white; }
.site-footer { background: #1f2937; color: #d1d5db; padding: 40px 24px; display: flex; flex-wrap: wrap; gap: 40px; }
.footer-col h4 { color: white; margin-bottom: 12px; }
.footer-col a { display: block; color: #9ca3af; text-decoration: none; padding: 4px 0; }
.copyright { width: 100%; text-align: center; margin-top: 24px; padding-top: 24px; border-top: 1px solid #374151; color: #6b7280; }
.login-form { max-width: 360px; margin: 60px auto; padding: 32px; border: 1px solid #e0e0e0; border-radius: 12px; }
.login-form h2 { margin-bottom: 24px; }
.login-form label { display: block; margin-bottom: 4px; font-size: 14px; color: #666; }
.login-form input { display: block; width: 100%; padding: 10px; margin-bottom: 16px; border: 1px solid #d1d5db; border-radius: 8px; }
.login-form button { width: 100%; padding: 12px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
.login-form a { display: block; text-align: center; margin-top: 12px; color: #2563eb; text-decoration: none; font-size: 14px; }
.search-results { max-width: 600px; margin: 24px auto; padding: 0 16px; }
.result { margin-bottom: 24px; }
.result h3 a { color: #1a0dab; text-decoration: none; }
.result p { color: #545454; font-size: 14px; margin: 4px 0; }
.result .url { color: #006621; font-size: 13px; }
.form-group { max-width: 400px; margin: 40px auto; padding: 20px; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 600; }
.form-group input { display: block; width: 100%; padding: 10px; border: 2px solid #d1d5db; border-radius: 8px; margin-bottom: 4px; }
.form-group input.valid { border-color: #16a34a; }
.form-group input.invalid { border-color: #dc2626; }
.feedback { font-size: 13px; }
.feedback.success { color: #16a34a; }
.feedback.error { color: #dc2626; }
"""
    add_task("missing_elements", "missing_or_broken_element", "high",
             f"{page_name} - all elements should be visible and correct",
             make_page(page_name, correct_body, base_css),
             make_page(page_name, bugged_body, base_css),
             bugs)


# ---- Category 6: Alignment / Spacing Issues ----

alignment_scenarios = [
    ("Team Grid", """
<div class="team-grid">
  <div class="member"><div class="avatar">JD</div><h4>John Doe</h4><p>CEO</p></div>
  <div class="member"><div class="avatar">JS</div><h4>Jane Smith</h4><p>CTO</p></div>
  <div class="member"><div class="avatar">BJ</div><h4>Bob Johnson</h4><p>CFO</p></div>
  <div class="member"><div class="avatar">AW</div><h4>Alice Williams</h4><p>COO</p></div>
</div>""",
     ".team-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; padding: 40px; text-align: center; } .member { padding: 20px; } .avatar { width: 64px; height: 64px; border-radius: 50%; background: #2563eb; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; font-weight: bold; }",
     ".team-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; padding: 40px; } .member { padding: 20px; } .member:nth-child(2) { margin-top: 80px; } .avatar { width: 64px; height: 64px; border-radius: 50%; background: #2563eb; color: white; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; font-weight: bold; }",
     ["Second team member (Jane Smith) is misaligned - has an extra 80px top margin, breaking the grid alignment"]),

    ("Feature Cards", """
<div class="features">
  <div class="feature"><h3>Fast</h3><p>Lightning-fast performance</p></div>
  <div class="feature"><h3>Secure</h3><p>Enterprise-grade security</p></div>
  <div class="feature"><h3>Scalable</h3><p>Grows with your business</p></div>
</div>""",
     ".features { display: flex; gap: 24px; padding: 40px; justify-content: center; } .feature { flex: 1; max-width: 280px; padding: 32px; background: #f8f9fa; border-radius: 12px; text-align: center; } .feature h3 { margin-bottom: 8px; }",
     ".features { display: flex; gap: 24px; padding: 40px; justify-content: center; } .feature { flex: 1; max-width: 280px; padding: 32px; background: #f8f9fa; border-radius: 12px; text-align: center; } .feature:last-child { max-width: 120px; padding: 8px; } .feature h3 { margin-bottom: 8px; }",
     ["Third feature card (Scalable) is much smaller than the others (max-width: 120px vs 280px, padding: 8px vs 32px), breaking visual consistency"]),

    ("Testimonial", """
<div class="testimonial">
  <blockquote>"This product changed our workflow completely. Highly recommended!"</blockquote>
  <div class="author"><strong>Sarah Chen</strong><span>VP of Engineering, TechCorp</span></div>
</div>""",
     ".testimonial { max-width: 600px; margin: 60px auto; padding: 32px; background: #f8f9fa; border-radius: 12px; border-left: 4px solid #2563eb; } blockquote { font-size: 18px; font-style: italic; color: #374151; margin-bottom: 16px; line-height: 1.6; } .author strong { display: block; } .author span { color: #888; font-size: 14px; }",
     ".testimonial { max-width: 600px; margin: 60px auto; padding: 32px; background: #f8f9fa; border-radius: 12px; border-left: 4px solid #2563eb; } blockquote { font-size: 18px; font-style: italic; color: #374151; margin-bottom: 16px; line-height: 1.6; direction: rtl; } .author strong { display: block; } .author span { color: #888; font-size: 14px; }",
     ["Testimonial quote text is right-to-left (direction: rtl), making English text read backwards/aligned incorrectly"]),

    ("Data Table", """
<table class="data-table">
  <thead><tr><th>Name</th><th>Role</th><th>Status</th></tr></thead>
  <tbody>
    <tr><td>Alice</td><td>Developer</td><td><span class="badge active">Active</span></td></tr>
    <tr><td>Bob</td><td>Designer</td><td><span class="badge active">Active</span></td></tr>
    <tr><td>Charlie</td><td>Manager</td><td><span class="badge inactive">Inactive</span></td></tr>
  </tbody>
</table>""",
     ".data-table { width: 100%; max-width: 600px; margin: 40px auto; border-collapse: collapse; } .data-table th, .data-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e0e0e0; } .data-table th { background: #f8f9fa; font-weight: 600; } .badge { padding: 4px 12px; border-radius: 12px; font-size: 13px; } .badge.active { background: #dcfce7; color: #16a34a; } .badge.inactive { background: #fee2e2; color: #dc2626; }",
     ".data-table { width: 100%; max-width: 600px; margin: 40px auto; border-collapse: collapse; } .data-table th, .data-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e0e0e0; } .data-table th { background: #f8f9fa; font-weight: 600; } .badge { padding: 4px 12px; border-radius: 12px; font-size: 13px; } .badge.active { background: #fee2e2; color: #dc2626; } .badge.inactive { background: #dcfce7; color: #16a34a; }",
     ["Status badge colors are swapped - 'Active' shows in red (error color) and 'Inactive' shows in green (success color), contradicting the status meaning"]),

    ("Progress Bar", """
<div class="progress-section">
  <h3>Project Progress</h3>
  <div class="progress-bar"><div class="progress-fill" style="width: 75%;"></div></div>
  <p>75% Complete</p>
</div>""",
     ".progress-section { max-width: 400px; margin: 40px auto; padding: 24px; } .progress-section h3 { margin-bottom: 12px; } .progress-bar { height: 12px; background: #e5e7eb; border-radius: 6px; overflow: hidden; margin-bottom: 8px; } .progress-fill { height: 100%; background: #2563eb; border-radius: 6px; transition: width 0.3s; } .progress-section p { color: #666; font-size: 14px; }",
     ".progress-section { max-width: 400px; margin: 40px auto; padding: 24px; } .progress-section h3 { margin-bottom: 12px; } .progress-bar { height: 12px; background: #e5e7eb; border-radius: 6px; overflow: hidden; margin-bottom: 8px; } .progress-fill { height: 100%; background: #2563eb; border-radius: 6px; transition: width 0.3s; } .progress-section p { color: #666; font-size: 14px; }",
     ["Progress bar shows ~25% filled but the text says '75% Complete' - visual mismatch between bar and label"]),
]

for title, body, correct_css, bugged_css, bugs in alignment_scenarios:
    if title == "Progress Bar":
        # Special case: bug in HTML
        bugged_body = body.replace('width: 75%', 'width: 25%')
        bugs = ["Progress bar shows ~25% filled but the text says '75% Complete' - visual mismatch between bar and label"]
        add_task("alignment_spacing", "visual_mismatch", "high",
                 f"{title} - visual elements should be consistent",
                 make_page(title, body, correct_css),
                 make_page(title, bugged_body, bugged_css),
                 bugs)
    else:
        add_task("alignment_spacing", "misalignment", "high",
                 f"{title} - elements should be properly aligned",
                 make_page(title, body, correct_css),
                 make_page(title, body, bugged_css),
                 bugs)


# ---- Category 7: Z-index / Overlapping Issues ----

overlap_scenarios = [
    ("Modal Dialog", """
<div class="page-content">
  <h1>Welcome to Our Site</h1>
  <p>Browse our products and find what you need.</p>
</div>
<div class="modal-overlay">
  <div class="modal">
    <h2>Subscribe to Newsletter</h2>
    <input type="email" placeholder="Enter your email">
    <button>Subscribe</button>
    <button class="close">Close</button>
  </div>
</div>""",
     ".page-content { padding: 40px; } .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; } .modal { background: white; padding: 32px; border-radius: 12px; max-width: 400px; width: 90%; } .modal h2 { margin-bottom: 16px; } .modal input { display: block; width: 100%; padding: 10px; margin-bottom: 12px; border: 1px solid #d1d5db; border-radius: 8px; } .modal button { padding: 10px 24px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; margin-right: 8px; } .modal .close { background: #6b7280; }",
     ".page-content { padding: 40px; } .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: -1; } .modal { background: white; padding: 32px; border-radius: 12px; max-width: 400px; width: 90%; } .modal h2 { margin-bottom: 16px; } .modal input { display: block; width: 100%; padding: 10px; margin-bottom: 12px; border: 1px solid #d1d5db; border-radius: 8px; } .modal button { padding: 10px 24px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; margin-right: 8px; } .modal .close { background: #6b7280; }",
     ["Modal overlay has z-index: -1, causing it to appear behind the page content and be completely invisible/inaccessible"]),

    ("Dropdown Menu", """
<div class="nav-container">
  <nav class="main-nav">
    <a href="#">Home</a>
    <div class="dropdown">
      <a href="#">Products ▼</a>
      <div class="dropdown-menu">
        <a href="#">Software</a>
        <a href="#">Hardware</a>
        <a href="#">Services</a>
      </div>
    </div>
    <a href="#">About</a>
  </nav>
</div>
<div class="content-below" style="position: relative; z-index: 10; background: white; padding: 40px;">
  <h2>Page Content</h2>
  <p>This content should not cover the dropdown menu.</p>
</div>""",
     ".nav-container { position: relative; z-index: 20; } .main-nav { display: flex; gap: 24px; padding: 16px 24px; background: #1f2937; } .main-nav a { color: white; text-decoration: none; } .dropdown { position: relative; } .dropdown-menu { display: block; position: absolute; top: 100%; left: 0; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); padding: 8px 0; min-width: 160px; z-index: 30; } .dropdown-menu a { display: block; padding: 8px 16px; color: #333; }",
     ".nav-container { position: relative; z-index: 1; } .main-nav { display: flex; gap: 24px; padding: 16px 24px; background: #1f2937; } .main-nav a { color: white; text-decoration: none; } .dropdown { position: relative; } .dropdown-menu { display: block; position: absolute; top: 100%; left: 0; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); padding: 8px 0; min-width: 160px; z-index: 2; } .dropdown-menu a { display: block; padding: 8px 16px; color: #333; }",
     ["Dropdown menu appears behind the page content below it (nav z-index: 1 vs content z-index: 10), making dropdown items unclickable"]),
]

for title, body, correct_css, bugged_css, bugs in overlap_scenarios:
    add_task("z_index_overlap", "element_hidden_behind", "critical",
             f"{title} - all interactive elements should be accessible",
             make_page(title, body, correct_css),
             make_page(title, body, bugged_css),
             bugs)


# ---- Category 8: Responsive / Mobile Issues (viewport-specific) ----

responsive_scenarios = [
    ("Mobile Nav", """
<header class="responsive-header">
  <div class="logo">AppName</div>
  <nav class="desktop-nav"><a href="#">Home</a><a href="#">Features</a><a href="#">Pricing</a><a href="#">Contact</a></nav>
  <button class="mobile-menu-btn">☰</button>
</header>""",
     ".responsive-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; background: #fff; border-bottom: 1px solid #e0e0e0; } .logo { font-size: 20px; font-weight: bold; } .desktop-nav a { margin: 0 12px; text-decoration: none; color: #333; } .mobile-menu-btn { display: none; background: none; border: none; font-size: 24px; cursor: pointer; } @media (max-width: 768px) { .desktop-nav { display: none; } .mobile-menu-btn { display: block; } }",
     ".responsive-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; background: #fff; border-bottom: 1px solid #e0e0e0; } .logo { font-size: 20px; font-weight: bold; } .desktop-nav a { margin: 0 12px; text-decoration: none; color: #333; } .mobile-menu-btn { display: none; background: none; border: none; font-size: 24px; cursor: pointer; }",
     ["No responsive breakpoint defined - on mobile screens, the desktop navigation will overflow and the hamburger menu button will never appear"]),

    ("Hero Section", """
<section class="hero">
  <h1>Build Something Amazing</h1>
  <p>The all-in-one platform for modern teams.</p>
  <div class="hero-cta"><button class="btn-primary">Get Started</button><button class="btn-secondary">Learn More</button></div>
</section>""",
     ".hero { padding: 80px 24px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; } .hero h1 { font-size: 48px; margin-bottom: 16px; } .hero p { font-size: 20px; margin-bottom: 32px; opacity: 0.9; } .hero-cta { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; } .btn-primary { padding: 14px 32px; background: white; color: #764ba2; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; } .btn-secondary { padding: 14px 32px; background: transparent; color: white; border: 2px solid white; border-radius: 8px; font-size: 16px; cursor: pointer; }",
     ".hero { padding: 80px 24px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; } .hero h1 { font-size: 48px; margin-bottom: 16px; } .hero p { font-size: 20px; margin-bottom: 32px; opacity: 0.9; } .hero-cta { display: flex; gap: 16px; justify-content: center; } .btn-primary { padding: 14px 32px; background: white; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; } .btn-secondary { padding: 14px 32px; background: transparent; color: white; border: 2px solid white; border-radius: 8px; font-size: 16px; cursor: pointer; }",
     ["Primary CTA button has white text on white background (color: white, background: white), making the 'Get Started' button text invisible"]),
]

for title, body, correct_css, bugged_css, bugs in responsive_scenarios:
    add_task("responsive_issues", "responsive_bug", "high",
             f"{title} - should work correctly across screen sizes",
             make_page(title, body, correct_css),
             make_page(title, body, bugged_css),
             bugs)


# ---- Save all tasks ----
os.makedirs("/home/ubuntu/e2_bench/eval_set/perceptual_validation", exist_ok=True)
output_path = "/home/ubuntu/e2_bench/eval_set/perceptual_validation/tasks.json"
with open(output_path, "w") as f:
    json.dump(TASKS, f, indent=2)

print(f"Generated {len(TASKS)} perceptual validation tasks")

# Print category breakdown
from collections import Counter
cats = Counter(t["category"] for t in TASKS)
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

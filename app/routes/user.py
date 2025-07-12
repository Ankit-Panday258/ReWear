from flask import render_template, Blueprint, redirect, url_for, request, flash, session, jsonify
from app import db
from app.models.users import User
from app.models.listings import Listing
from app.models.swaps import SwapRequest
from app.routes.auth import login_required, get_current_user
from sqlalchemy import or_

user = Blueprint('user', __name__)

@user.route("/profile")
@login_required
def renderProfile():
    current_user = get_current_user()
    
    # Get user statistics
    total_listings = Listing.query.filter_by(uploader_id=current_user.user_id).count()
    approved_listings = Listing.query.filter_by(
        uploader_id=current_user.user_id, 
        is_approved=True
    ).count()
    completed_swaps = SwapRequest.query.filter(
        or_(
            SwapRequest.requester_id == current_user.user_id,
            SwapRequest.requested_item.has(uploader_id=current_user.user_id)
        ),
        SwapRequest.status == 'Accepted'
    ).count()
    
    user_stats = {
        'total_listings': total_listings,
        'approved_listings': approved_listings,
        'completed_swaps': completed_swaps,
        'points': current_user.points
    }
    
    return render_template("user/profile.html", current_user=current_user, stats=user_stats)

@user.route("/my-listings")
@login_required
def myListings():
    current_user = get_current_user()
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    
    # Build query
    query = Listing.query.filter_by(uploader_id=current_user.user_id)
    
    if status_filter == 'approved':
        query = query.filter_by(is_approved=True)
    elif status_filter == 'pending':
        query = query.filter_by(is_approved=False)
    elif status_filter == 'available':
        query = query.filter_by(is_available=True, is_approved=True)
    elif status_filter == 'unavailable':
        query = query.filter_by(is_available=False)
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    listings = query.order_by(Listing.created_at.desc()).all()
    
    return render_template("user/my_listings.html", 
                         listings=listings, 
                         current_user=current_user,
                         status_filter=status_filter,
                         category_filter=category_filter)

@user.route("/my-swaps")
@login_required
def mySwaps():
    current_user = get_current_user()
    
    # Get swap requests made by user (outgoing)
    outgoing_swaps = SwapRequest.query.filter_by(
        requester_id=current_user.user_id
    ).order_by(SwapRequest.created_at.desc()).all()
    
    # Get swap requests for user's items (incoming)
    incoming_swaps = SwapRequest.query.join(Listing).filter(
        Listing.uploader_id == current_user.user_id
    ).order_by(SwapRequest.created_at.desc()).all()
    
    return render_template("user/my_swaps.html", 
                         outgoing_swaps=outgoing_swaps,
                         incoming_swaps=incoming_swaps,
                         current_user=current_user)

@user.route("/swap-requests")
@login_required
def swapRequests():
    """View all pending swap requests for user's items"""
    current_user = get_current_user()
    
    # Get pending swap requests for user's items
    pending_requests = SwapRequest.query.join(Listing).filter(
        Listing.uploader_id == current_user.user_id,
        SwapRequest.status == 'Pending'
    ).order_by(SwapRequest.created_at.desc()).all()
    
    return render_template("user/swapReq.html", 
                         swap_requests=pending_requests,
                         current_user=current_user)

@user.route("/points")
@login_required
def userPoints():
    """API endpoint to get current user points"""
    current_user = get_current_user()
    return jsonify({
        'points': current_user.points,
        'user_id': current_user.user_id
    })

@user.route("/dashboard")
@login_required 
def dashboard():
    """User dashboard with overview"""
    current_user = get_current_user()
    
    # Recent listings
    recent_listings = Listing.query.filter_by(
        uploader_id=current_user.user_id
    ).order_by(Listing.created_at.desc()).limit(5).all()
    
    # Recent swap activity
    recent_swaps = SwapRequest.query.filter(
        or_(
            SwapRequest.requester_id == current_user.user_id,
            SwapRequest.requested_item.has(uploader_id=current_user.user_id)
        )
    ).order_by(SwapRequest.created_at.desc()).limit(5).all()
    
    # Pending requests for user's items
    pending_requests = SwapRequest.query.join(Listing).filter(
        Listing.uploader_id == current_user.user_id,
        SwapRequest.status == 'Pending'
    ).count()
    
    dashboard_data = {
        'recent_listings': recent_listings,
        'recent_swaps': recent_swaps,
        'pending_requests': pending_requests
    }
    
    return render_template("user/dashboard.html", 
                         current_user=current_user,
                         data=dashboard_data)
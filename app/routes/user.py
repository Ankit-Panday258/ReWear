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
    
    my_listings = query.order_by(Listing.created_at.desc()).all()
    
    # Get available categories for filter dropdown
    categories = ['Men', 'Women', 'Kids']
    
    return render_template("user/my_listings.html", 
                         my_listings=my_listings, 
                         current_user=current_user,
                         status_filter=status_filter,
                         category_filter=category_filter,
                         categories=categories)

@user.route("/my-swaps")
@login_required
def mySwaps():
    current_user = get_current_user()
    
    # Get swap requests made by user (outgoing)
    outgoing_swaps = SwapRequest.query.filter_by(
        requester_id=current_user.user_id
    ).order_by(SwapRequest.created_at.desc()).all()
    
    # Get swap requests for user's items (incoming)
    incoming_swaps = SwapRequest.query.join(
        Listing, SwapRequest.requested_item_id == Listing.id
    ).filter(
        Listing.uploader_id == current_user.user_id,
        SwapRequest.requester_id != current_user.user_id  
    ).order_by(SwapRequest.created_at.desc()).all()
    
    # For compatibility with template, use my_purchases for outgoing swaps
    my_purchases = outgoing_swaps
    
    return render_template("user/my_swaps.html", 
                         outgoing_swaps=outgoing_swaps,
                         incoming_swaps=incoming_swaps,
                         my_purchases=my_purchases,
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

@user.route("/api/swaps/<swap_id>/accept", methods=['POST'])
@login_required
def acceptSwap(swap_id):
    """Accept an incoming swap request"""
    current_user = get_current_user()
    
    # Find the swap request
    swap = SwapRequest.query.get_or_404(swap_id)
    
    # Verify the current user owns the requested item
    if swap.requested_item.uploader_id != current_user.user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Verify swap is pending
    if swap.status != 'Pending':
        return jsonify({'success': False, 'error': 'Swap is no longer pending'}), 400
    
    try:
        # Accept the swap
        swap.accept()
        
        # Mark the requested item as unavailable
        swap.requested_item.is_available = False
        swap.requested_item.status = 'Swapped'
        
        # If it's a direct swap, mark the offered item as unavailable
        if swap.swap_type == 'direct_swap' and swap.offered_item:
            swap.offered_item.is_available = False
            swap.offered_item.status = 'Swapped'
        
        # Handle point redemption
        if swap.swap_type == 'point_redemption':
            # Deduct points from requester
            swap.requester.points -= swap.points_used
            # Add points to item owner
            current_user.points += swap.points_used
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Swap accepted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@user.route("/api/swaps/<swap_id>/reject", methods=['POST'])
@login_required
def rejectSwap(swap_id):
    """Reject an incoming swap request"""
    current_user = get_current_user()
    
    # Find the swap request
    swap = SwapRequest.query.get_or_404(swap_id)
    
    # Verify the current user owns the requested item
    if swap.requested_item.uploader_id != current_user.user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Verify swap is pending
    if swap.status != 'Pending':
        return jsonify({'success': False, 'error': 'Swap is no longer pending'}), 400
    
    try:
        swap.reject()
        return jsonify({'success': True, 'message': 'Swap rejected'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@user.route("/api/swaps/<swap_id>/cancel", methods=['POST'])
@login_required
def cancelSwap(swap_id):
    """Cancel an outgoing swap request"""
    current_user = get_current_user()
    
    # Find the swap request
    swap = SwapRequest.query.get_or_404(swap_id)
    
    # Verify the current user made this request
    if swap.requester_id != current_user.user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Verify swap is pending
    if swap.status != 'Pending':
        return jsonify({'success': False, 'error': 'Swap is no longer pending'}), 400
    
    try:
        swap.cancel()
        return jsonify({'success': True, 'message': 'Swap cancelled'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

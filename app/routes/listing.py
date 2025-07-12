from flask import render_template, Blueprint, redirect, url_for, request, flash, session, jsonify
from app import db
from app.models.listings import Listing
from app.models.users import User
from app.models.swaps import SwapRequest
from app.routes.auth import login_required, get_current_user, update_user_session
from sqlalchemy import or_, and_
from datetime import datetime

listing = Blueprint('listing', __name__)

# Index route
@listing.route('/')
def index():
    # Get all approved and available listings
    listings = Listing.query.filter(
        Listing.is_approved == True,
        Listing.is_available == True
    ).order_by(Listing.created_at.desc()).all()
    
    current_user = get_current_user()
    
    return render_template("listing/index.html", listings=listings, current_user=current_user)

# New Form Render route
@listing.route("/new")
@login_required
def renderNewPage():
    current_user = get_current_user()
    return render_template("listing/new.html", current_user=current_user)

# Create Route
@listing.route("/", methods=["POST"])
@login_required
def createListing():
    try:
        current_user = get_current_user()
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category')
        item_type = request.form.get('type')
        size = request.form.get('size')
        image_url = request.form.get('image_url', '').strip()
        point_value = request.form.get('point_value', 100, type=int)
        
        # Validation
        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('listing.renderNewPage'))
        
        if not category or category not in ['Men', 'Women', 'Kids']:
            flash('Valid category is required.', 'danger')
            return redirect(url_for('listing.renderNewPage'))
        
        if not item_type or item_type not in ['Shirt', 'Pants', 'Dress', 'Others']:
            flash('Valid item type is required.', 'danger')
            return redirect(url_for('listing.renderNewPage'))
        
        if not size or size not in ['S', 'M', 'L', 'XL']:
            flash('Valid size is required.', 'danger')
            return redirect(url_for('listing.renderNewPage'))
        
        if point_value < 0:
            flash('Point value must be positive.', 'danger')
            return redirect(url_for('listing.renderNewPage'))
        
        # Create new listing
        new_listing = Listing(
            uploader_id=current_user.user_id,
            title=title,
            description=description,
            category=category,
            type=item_type,
            size=size,
            image_url=image_url if image_url else None,
            point_value=point_value
        )
        
        db.session.add(new_listing)
        db.session.commit()
        
        flash('Listing created successfully! It will be available after admin approval.', 'success')
        return redirect(url_for('listing.index'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the listing. Please try again.', 'danger')
        return redirect(url_for('listing.renderNewPage'))

# Show Route
@listing.route('/<listing_id>')
def showListing(listing_id):
    listing_item = Listing.query.get_or_404(listing_id)
    current_user = get_current_user()
    
    # Check if listing is approved
    if not listing_item.is_approved and (not current_user or current_user.user_id != listing_item.uploader_id):
        flash('This listing is not available.', 'warning')
        return redirect(url_for('listing.index'))
    
    # Get swap requests for this listing if user is the owner
    swap_requests = []
    user_swap_request = None
    can_swap = False
    swap_message = ""
    user_available_items = []
    
    if current_user:
        if current_user.user_id == listing_item.uploader_id:
            # If user owns this listing, show incoming swap requests
            swap_requests = SwapRequest.query.filter(
                SwapRequest.requested_item_id == listing_id,
                SwapRequest.status == 'Pending'
            ).all()
        else:
            # Check if user can swap with this listing
            can_swap, swap_message = can_user_swap_with_listing(current_user, listing_item)
            
            # If user doesn't own this listing, check if they have a pending swap request
            user_swap_request = SwapRequest.query.filter(
                SwapRequest.requester_id == current_user.user_id,
                SwapRequest.requested_item_id == listing_id,
                SwapRequest.status.in_(['Pending', 'Accepted', 'Rejected'])
            ).first()
            
            # Get user's available items for swap
            if can_swap:
                user_available_items = Listing.query.filter(
                    Listing.uploader_id == current_user.user_id,
                    Listing.is_approved == True,
                    Listing.is_available == True
                ).all()
    
    return render_template("listing/show.html", 
                         listing=listing_item, 
                         current_user=current_user,
                         swap_requests=swap_requests,
                         user_swap_request=user_swap_request,
                         can_swap=can_swap,
                         swap_message=swap_message,
                         user_available_items=user_available_items)

# Utility function to check if user can swap with a listing
def can_user_swap_with_listing(user, listing):
    """Check if a user can create a swap request for a listing"""
    if not user:
        return False, "Please log in to swap items"
    
    if not listing.is_approved or not listing.is_available:
        return False, "This listing is not available for swap"
    
    if user.user_id == listing.uploader_id:
        return False, "You cannot swap with your own listing"
    
    # Check for existing pending request
    existing_request = SwapRequest.query.filter(
        SwapRequest.requester_id == user.user_id,
        SwapRequest.requested_item_id == listing.id,
        SwapRequest.status == 'Pending'
    ).first()
    
    if existing_request:
        return False, "You already have a pending swap request for this listing"
    
    return True, "Can swap"

# Edit Route
@listing.route("/<listing_id>/edit")
@login_required
def renderEditPage(listing_id):
    listing_item = Listing.query.get_or_404(listing_id)
    current_user = get_current_user()
    
    # Check if user owns this listing
    if current_user.user_id != listing_item.uploader_id:
        flash('You can only edit your own listings.', 'danger')
        return redirect(url_for('listing.showListing', listing_id=listing_id))
    
    return render_template("listing/edit.html", listing=listing_item, current_user=current_user)

# Update route
@listing.route("/<listing_id>", methods=["POST"])
@login_required
def updateListing(listing_id):
    try:
        listing_item = Listing.query.get_or_404(listing_id)
        current_user = get_current_user()
        
        # Check if user owns this listing
        if current_user.user_id != listing_item.uploader_id:
            flash('You can only edit your own listings.', 'danger')
            return redirect(url_for('listing.showListing', listing_id=listing_id))
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category')
        item_type = request.form.get('type')
        size = request.form.get('size')
        image_url = request.form.get('image_url', '').strip()
        point_value = request.form.get('point_value', type=int)
        
        # Validation
        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('listing.renderEditPage', listing_id=listing_id))
        
        if category and category not in ['Men', 'Women', 'Kids']:
            flash('Valid category is required.', 'danger')
            return redirect(url_for('listing.renderEditPage', listing_id=listing_id))
        
        if item_type and item_type not in ['Shirt', 'Pants', 'Dress', 'Others']:
            flash('Valid item type is required.', 'danger')
            return redirect(url_for('listing.renderEditPage', listing_id=listing_id))
        
        if size and size not in ['S', 'M', 'L', 'XL']:
            flash('Valid size is required.', 'danger')
            return redirect(url_for('listing.renderEditPage', listing_id=listing_id))
        
        if point_value is not None and point_value < 0:
            flash('Point value must be positive.', 'danger')
            return redirect(url_for('listing.renderEditPage', listing_id=listing_id))
        
        # Update listing
        listing_item.title = title
        listing_item.description = description
        if category:
            listing_item.category = category
        if item_type:
            listing_item.type = item_type
        if size:
            listing_item.size = size
        if image_url:
            listing_item.image_url = image_url
        if point_value is not None:
            listing_item.point_value = point_value
        
        # Reset approval status if significant changes were made
        listing_item.is_approved = False
        
        db.session.commit()
        
        flash('Listing updated successfully! It will need admin approval again.', 'success')
        return redirect(url_for('listing.showListing', listing_id=listing_id))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the listing. Please try again.', 'danger')
        return redirect(url_for('listing.renderEditPage', listing_id=listing_id))

# Create Swap Request route
@listing.route("/<listing_id>/swap", methods=["POST"])
@login_required
def createSwapRequest(listing_id):
    try:
        requested_listing = Listing.query.get_or_404(listing_id)
        current_user = get_current_user()
        
        # Validation checks
        if not requested_listing.is_approved or not requested_listing.is_available:
            return jsonify({'error': 'This listing is not available for swap.'}), 400
        
        if current_user.user_id == requested_listing.uploader_id:
            return jsonify({'error': 'You cannot swap with your own listing.'}), 400
        
        # Check for existing pending request
        existing_request = SwapRequest.query.filter(
            SwapRequest.requester_id == current_user.user_id,
            SwapRequest.requested_item_id == listing_id,
            SwapRequest.status == 'Pending'
        ).first()
        
        if existing_request:
            return jsonify({'error': 'You already have a pending swap request for this listing.'}), 400
        
        # Get form data
        swap_type = request.form.get('swap_type')
        offered_item_id = request.form.get('offered_item_id')
        
        if swap_type not in ['direct_swap', 'point_redemption']:
            return jsonify({'error': 'Invalid swap type.'}), 400
        
        # Handle direct swap
        if swap_type == 'direct_swap':
            if not offered_item_id:
                return jsonify({'error': 'Offered item is required for direct swap.'}), 400
            
            # Validate offered item
            offered_item = Listing.query.get(offered_item_id)
            if not offered_item:
                return jsonify({'error': 'Offered item not found.'}), 400
            
            if offered_item.uploader_id != current_user.user_id:
                return jsonify({'error': 'You can only offer your own items.'}), 400
            
            if not offered_item.is_approved or not offered_item.is_available:
                return jsonify({'error': 'Your offered item is not available for swap.'}), 400
            
            # Create direct swap request
            swap_request = SwapRequest(
                requester_id=current_user.user_id,
                requested_item_id=listing_id,
                offered_item_id=offered_item_id,
                swap_type='direct_swap',
                points_used=0
            )
        
        # Handle point redemption
        else:  # point_redemption
            points_needed = requested_listing.point_value
            if current_user.points < points_needed:
                return jsonify({'error': f'Insufficient points. You need {points_needed} points but only have {current_user.points}.'}), 400
            
            # Create point redemption request
            swap_request = SwapRequest(
                requester_id=current_user.user_id,
                requested_item_id=listing_id,
                offered_item_id=None,
                swap_type='point_redemption',
                points_used=points_needed
            )
        
        db.session.add(swap_request)
        db.session.commit()
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': f'Swap request sent successfully!',
                'swap_id': swap_request.id
            })
        else:
            flash(f'Swap request sent successfully!', 'success')
            return redirect(url_for('listing.showListing', listing_id=listing_id))
        
    except Exception as e:
        db.session.rollback()
        error_msg = 'An error occurred while creating the swap request. Please try again.'
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'danger')
            return redirect(url_for('listing.showListing', listing_id=listing_id))

# Accept Swap Request route
@listing.route("/swaps/<swap_id>/accept", methods=["POST"])
@login_required
def acceptSwapRequest(swap_id):
    try:
        swap_request = SwapRequest.query.get_or_404(swap_id)
        current_user = get_current_user()
        
        # Verify user is the owner of the requested item
        if current_user.user_id != swap_request.requested_item.uploader_id:
            return jsonify({'error': 'You can only accept swaps for your own items.'}), 403
        
        if swap_request.status != 'Pending':
            return jsonify({'error': 'This swap request is no longer pending.'}), 400
        
        # Process the swap based on type
        if swap_request.is_direct_swap():
            # Direct swap: exchange items
            requested_item = swap_request.requested_item
            offered_item = swap_request.offered_item
            
            # Verify both items are still available
            if not requested_item.is_available or not offered_item.is_available:
                return jsonify({'error': 'One or both items are no longer available.'}), 400
            
            # Mark both items as swapped
            requested_item.mark_as_swapped()
            offered_item.mark_as_swapped()
            
            # Award points to both users (bonus for successful swap)
            swap_bonus = 10
            swap_request.requester.add_points(swap_bonus)
            current_user.add_points(swap_bonus)
            
        else:  # point_redemption
            # Point redemption: deduct points and mark item as redeemed
            requester = swap_request.requester
            
            # Double-check user has enough points
            if requester.points < swap_request.points_used:
                return jsonify({'error': 'Requester has insufficient points.'}), 400
            
            # Deduct points from requester
            requester.deduct_points(swap_request.points_used)
            
            # Award points to item owner
            current_user.add_points(swap_request.points_used)
            
            # Mark item as redeemed
            swap_request.requested_item.mark_as_redeemed()
        
        # Accept the swap request
        swap_request.accept()
        
        # Update user session data
        update_user_session(current_user.user_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Swap request accepted successfully!',
                'new_points': current_user.points
            })
        else:
            flash('Swap request accepted successfully!', 'success')
            return redirect(url_for('user.mySwaps'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = 'An error occurred while accepting the swap request.'
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'danger')
            return redirect(url_for('user.mySwaps'))

# Reject Swap Request route
@listing.route("/swaps/<swap_id>/reject", methods=["POST"])
@login_required
def rejectSwapRequest(swap_id):
    try:
        swap_request = SwapRequest.query.get_or_404(swap_id)
        current_user = get_current_user()
        
        # Verify user is the owner of the requested item
        if current_user.user_id != swap_request.requested_item.uploader_id:
            return jsonify({'error': 'You can only reject swaps for your own items.'}), 403
        
        if swap_request.status != 'Pending':
            return jsonify({'error': 'This swap request is no longer pending.'}), 400
        
        # Reject the swap request
        swap_request.reject()
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Swap request rejected.'
            })
        else:
            flash('Swap request rejected.', 'info')
            return redirect(url_for('user.mySwaps'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = 'An error occurred while rejecting the swap request.'
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'danger')
            return redirect(url_for('user.mySwaps'))

# Cancel Swap Request route  
@listing.route("/swaps/<swap_id>/cancel", methods=["POST"])
@login_required
def cancelSwapRequest(swap_id):
    try:
        swap_request = SwapRequest.query.get_or_404(swap_id)
        current_user = get_current_user()
        
        # Verify user is the requester
        if current_user.user_id != swap_request.requester_id:
            return jsonify({'error': 'You can only cancel your own swap requests.'}), 403
        
        if swap_request.status != 'Pending':
            return jsonify({'error': 'This swap request is no longer pending.'}), 400
        
        # Cancel the swap request
        swap_request.cancel()
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Swap request cancelled.'
            })
        else:
            flash('Swap request cancelled.', 'info')
            return redirect(url_for('user.mySwaps'))
        
    except Exception as e:
        db.session.rollback()
        error_msg = 'An error occurred while cancelling the swap request.'
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'danger')
            return redirect(url_for('user.mySwaps'))

# API endpoint for getting listing data (for AJAX calls)
@listing.route("/api/<listing_id>")
def getListingAPI(listing_id):
    listing_item = Listing.query.get_or_404(listing_id)
    
    # Check if listing is approved or if user owns it
    current_user = get_current_user()
    if not listing_item.is_approved and (not current_user or current_user.user_id != listing_item.uploader_id):
        return jsonify({'error': 'Listing not found'}), 404
    
    return jsonify(listing_item.to_dict())

# API endpoint for getting user's available items for swap
@listing.route("/api/user-items/<user_id>")
@login_required
def getUserAvailableItems(user_id):
    current_user = get_current_user()
    
    # Users can only get their own items or if they're making a swap request
    if current_user.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get user's available listings
    available_items = Listing.query.filter(
        Listing.uploader_id == user_id,
        Listing.is_approved == True,
        Listing.is_available == True
    ).all()
    
    items_data = [item.to_dict() for item in available_items]
    return jsonify({'items': items_data})

# API endpoint for swap request details
@listing.route("/api/swaps/<swap_id>")
@login_required
def getSwapDetails(swap_id):
    swap_request = SwapRequest.query.get_or_404(swap_id)
    current_user = get_current_user()
    
    # Check if user has permission to view this swap
    if (current_user.user_id != swap_request.requester_id and 
        current_user.user_id != swap_request.requested_item.uploader_id):
        return jsonify({'error': 'Access denied'}), 403
    
    swap_data = swap_request.to_dict()
    
    # Add related item details
    swap_data['requested_item'] = swap_request.requested_item.to_dict()
    swap_data['requester'] = {
        'user_id': swap_request.requester.user_id,
        'username': swap_request.requester.username,
        'points': swap_request.requester.points
    }
    
    if swap_request.offered_item:
        swap_data['offered_item'] = swap_request.offered_item.to_dict()
    
    return jsonify(swap_data)

# Search/Filter routes for listings
@listing.route("/search")
def searchListings():
    # Get search parameters
    search_query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    item_type = request.args.get('type', '')
    size = request.args.get('size', '')
    min_points = request.args.get('min_points', 0, type=int)
    max_points = request.args.get('max_points', 1000, type=int)
    
    # Build query
    query = Listing.query.filter(
        Listing.is_approved == True,
        Listing.is_available == True
    )
    
    if search_query:
        query = query.filter(
            or_(
                Listing.title.contains(search_query),
                Listing.description.contains(search_query)
            )
        )
    
    if category:
        query = query.filter_by(category=category)
    
    if item_type:
        query = query.filter_by(type=item_type)
    
    if size:
        query = query.filter_by(size=size)
    
    query = query.filter(
        Listing.point_value >= min_points,
        Listing.point_value <= max_points
    )
    
    listings = query.order_by(Listing.created_at.desc()).all()
    current_user = get_current_user()
    
    return render_template("listing/index.html", 
                         listings=listings, 
                         current_user=current_user,
                         search_params={
                             'q': search_query,
                             'category': category,
                             'type': item_type,
                             'size': size,
                             'min_points': min_points,
                             'max_points': max_points
                         })
from flask import render_template, Blueprint, redirect, url_for, request, flash, jsonify
from app import db
from app.models.users import User
from app.models.listings import Listing
from app.models.swaps import SwapRequest
from app.routes.auth import admin_required, get_current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin = Blueprint('admin', __name__)

@admin.route("/")
@admin_required
def renderAdmin():
    """Admin dashboard with statistics and overview"""
    current_user = get_current_user()
    
    # Get basic statistics
    total_users = User.query.count()
    total_listings = Listing.query.count()
    pending_listings = Listing.query.filter_by(is_approved=False).count()
    approved_listings = Listing.query.filter_by(is_approved=True).count()
    total_swaps = SwapRequest.query.count()
    pending_swaps = SwapRequest.query.filter_by(status='Pending').count()
    completed_swaps = SwapRequest.query.filter_by(status='Accepted').count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_month = User.query.filter(User.created_at >= thirty_days_ago).count()
    new_listings_month = Listing.query.filter(Listing.created_at >= thirty_days_ago).count()
    
    # Get recent listings pending approval
    recent_pending_listings = Listing.query.filter_by(
        is_approved=False
    ).order_by(desc(Listing.created_at)).limit(5).all()
    
    # Get recent users
    recent_users = User.query.filter(
        User.is_admin == False
    ).order_by(desc(User.created_at)).limit(5).all()
    
    # Category distribution
    category_stats = db.session.query(
        Listing.category,
        func.count(Listing.id).label('count')
    ).filter_by(is_approved=True).group_by(Listing.category).all()
    
    stats = {
        'total_users': total_users,
        'total_listings': total_listings,
        'pending_listings': pending_listings,
        'approved_listings': approved_listings,
        'total_swaps': total_swaps,
        'pending_swaps': pending_swaps,
        'completed_swaps': completed_swaps,
        'new_users_month': new_users_month,
        'new_listings_month': new_listings_month,
        'category_stats': dict(category_stats),
        'recent_pending_listings': recent_pending_listings,
        'recent_users': recent_users
    }
    
    return render_template("admin/admin.html", current_user=current_user, stats=stats)

@admin.route("/users")
@admin_required
def manageUsers():
    """Manage users page"""
    current_user = get_current_user()
    
    # Get filter parameters
    search = request.args.get('search', '').strip()
    admin_filter = request.args.get('admin_filter', 'all')
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Build query
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )
    
    if admin_filter == 'admins':
        query = query.filter_by(is_admin=True)
    elif admin_filter == 'users':
        query = query.filter_by(is_admin=False)
    
    # Apply sorting
    if sort_by == 'username':
        order_column = User.username
    elif sort_by == 'email':
        order_column = User.email
    elif sort_by == 'points':
        order_column = User.points
    else:  # created_at
        order_column = User.created_at
    
    if order == 'desc':
        order_column = desc(order_column)
    
    users = query.order_by(order_column).all()
    
    return render_template("admin/users.html", 
                         current_user=current_user, 
                         users=users,
                         search=search,
                         admin_filter=admin_filter,
                         sort_by=sort_by,
                         order=order)

@admin.route("/listings")
@admin_required  
def manageListings():
    """Manage listings page"""
    current_user = get_current_user()
    
    # Get filter parameters
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    approval_filter = request.args.get('approval', 'all')
    
    # Build query
    query = Listing.query
    
    if search:
        query = query.filter(
            db.or_(
                Listing.title.contains(search),
                Listing.description.contains(search)
            )
        )
    
    if status_filter != 'all':
        if status_filter == 'available':
            query = query.filter_by(is_available=True)
        elif status_filter == 'unavailable':
            query = query.filter_by(is_available=False)
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    if approval_filter != 'all':
        if approval_filter == 'approved':
            query = query.filter_by(is_approved=True)
        elif approval_filter == 'pending':
            query = query.filter_by(is_approved=False)
    
    listings = query.order_by(desc(Listing.created_at)).all()
    
    return render_template("admin/listings.html",
                         current_user=current_user,
                         listings=listings,
                         search=search,
                         status_filter=status_filter,
                         category_filter=category_filter,
                         approval_filter=approval_filter)

@admin.route("/swaps")
@admin_required
def manageSwaps():
    """Manage swap requests page"""
    current_user = get_current_user()
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    
    # Build query
    query = SwapRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter.title())
    
    if type_filter != 'all':
        query = query.filter_by(swap_type=type_filter)
    
    swaps = query.order_by(desc(SwapRequest.created_at)).all()
    
    return render_template("admin/swaps.html",
                         current_user=current_user,
                         swaps=swaps,
                         status_filter=status_filter,
                         type_filter=type_filter)

@admin.route("/listings/<listing_id>/approve", methods=["POST"])
@admin_required
def approveListing(listing_id):
    """Approve a listing"""
    try:
        listing = Listing.query.get_or_404(listing_id)
        listing.approve()
        
        if request.is_json:
            return jsonify({'success': True, 'message': f'Listing "{listing.title}" approved successfully'})
        else:
            flash(f'Listing "{listing.title}" approved successfully', 'success')
            return redirect(request.referrer or url_for('admin.manageListings'))
            
    except Exception as e:
        db.session.rollback()
        error_msg = 'Error approving listing'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'danger')
            return redirect(request.referrer or url_for('admin.manageListings'))

@admin.route("/listings/<listing_id>/reject", methods=["POST"])
@admin_required
def rejectListing(listing_id):
    """Reject/Delete a listing"""
    try:
        listing = Listing.query.get_or_404(listing_id)
        listing_title = listing.title
        
        # Check if listing has any swap requests
        swap_requests = SwapRequest.query.filter(
            db.or_(
                SwapRequest.requested_item_id == listing_id,
                SwapRequest.offered_item_id == listing_id
            )
        ).all()
        
        # Cancel any pending swap requests
        for swap in swap_requests:
            if swap.status == 'Pending':
                swap.cancel()
        
        db.session.delete(listing)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': f'Listing "{listing_title}" rejected and removed'})
        else:
            flash(f'Listing "{listing_title}" rejected and removed', 'info')
            return redirect(request.referrer or url_for('admin.manageListings'))
            
    except Exception as e:
        db.session.rollback()
        error_msg = 'Error rejecting listing'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'danger')
            return redirect(request.referrer or url_for('admin.manageListings'))

@admin.route("/users/<user_id>/toggle-admin", methods=["POST"])
@admin_required
def toggleUserAdmin(user_id):
    """Toggle user admin status"""
    try:
        user = User.query.get_or_404(user_id)
        current_user = get_current_user()
        
        # Prevent admin from removing their own admin status
        if user.user_id == current_user.user_id:
            error_msg = 'You cannot modify your own admin status'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            else:
                flash(error_msg, 'warning')
                return redirect(request.referrer or url_for('admin.manageUsers'))
        
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'granted' if user.is_admin else 'removed'
        message = f'Admin privileges {status} for user "{user.username}"'
        
        if request.is_json:
            return jsonify({'success': True, 'message': message, 'is_admin': user.is_admin})
        else:
            flash(message, 'success')
            return redirect(request.referrer or url_for('admin.manageUsers'))
            
    except Exception as e:
        db.session.rollback()
        error_msg = 'Error updating user admin status'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'danger')
            return redirect(request.referrer or url_for('admin.manageUsers'))

@admin.route("/users/<user_id>/adjust-points", methods=["POST"])
@admin_required
def adjustUserPoints(user_id):
    """Adjust user points"""
    try:
        user = User.query.get_or_404(user_id)
        points_adjustment = request.form.get('points_adjustment', type=int)
        
        if points_adjustment is None:
            error_msg = 'Points adjustment value is required'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            else:
                flash(error_msg, 'warning')
                return redirect(request.referrer or url_for('admin.manageUsers'))
        
        old_points = user.points
        user.points = max(0, user.points + points_adjustment)  # Ensure points don't go negative
        db.session.commit()
        
        action = 'added' if points_adjustment > 0 else 'deducted'
        message = f'{abs(points_adjustment)} points {action} for user "{user.username}" (was {old_points}, now {user.points})'
        
        if request.is_json:
            return jsonify({'success': True, 'message': message, 'new_points': user.points})
        else:
            flash(message, 'success')
            return redirect(request.referrer or url_for('admin.manageUsers'))
            
    except Exception as e:
        db.session.rollback()
        error_msg = 'Error adjusting user points'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'danger')
            return redirect(request.referrer or url_for('admin.manageUsers'))

@admin.route("/analytics")
@admin_required
def analytics():
    """Admin analytics dashboard"""
    current_user = get_current_user()
    
    # Time-based analytics
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # User growth
    user_growth = {
        'total': User.query.count(),
        'last_30_days': User.query.filter(User.created_at >= thirty_days_ago).count(),
        'last_7_days': User.query.filter(User.created_at >= seven_days_ago).count()
    }
    
    # Listing stats
    listing_stats = {
        'total': Listing.query.count(),
        'approved': Listing.query.filter_by(is_approved=True).count(),
        'pending': Listing.query.filter_by(is_approved=False).count(),
        'available': Listing.query.filter_by(is_available=True, is_approved=True).count()
    }
    
    # Swap activity
    swap_stats = {
        'total': SwapRequest.query.count(),
        'pending': SwapRequest.query.filter_by(status='Pending').count(),
        'completed': SwapRequest.query.filter_by(status='Accepted').count(),
        'direct_swaps': SwapRequest.query.filter_by(swap_type='direct_swap').count(),
        'point_redemptions': SwapRequest.query.filter_by(swap_type='point_redemption').count()
    }
    
    # Top users by points
    top_users = User.query.filter_by(is_admin=False).order_by(desc(User.points)).limit(10).all()
    
    # Category popularity
    category_popularity = db.session.query(
        Listing.category,
        func.count(Listing.id).label('count')
    ).filter_by(is_approved=True).group_by(Listing.category).all()
    
    analytics_data = {
        'user_growth': user_growth,
        'listing_stats': listing_stats,
        'swap_stats': swap_stats,
        'top_users': top_users,
        'category_popularity': dict(category_popularity)
    }
    
    return render_template("admin/analytics.html", 
                         current_user=current_user, 
                         analytics=analytics_data)

@admin.route("/api/stats")
@admin_required
def getStatsAPI():
    """API endpoint for dashboard statistics"""
    # Get basic statistics
    stats = {
        'users': {
            'total': User.query.count(),
            'active_today': User.query.filter(User.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)).count()
        },
        'listings': {
            'total': Listing.query.count(),
            'pending': Listing.query.filter_by(is_approved=False).count(),
            'approved': Listing.query.filter_by(is_approved=True).count()
        },
        'swaps': {
            'total': SwapRequest.query.count(),
            'pending': SwapRequest.query.filter_by(status='Pending').count(),
            'completed': SwapRequest.query.filter_by(status='Accepted').count()
        }
    }
    
    return jsonify(stats)
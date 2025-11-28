from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models import Member
import uuid


class CookieAuthentication(BaseAuthentication):
    """
    Custom authentication class that uses HttpOnly cookies
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using session cookie
        """
        session_id = request.COOKIES.get('sessionid')
        
        if not session_id:
            return None
        
        # Get member_id from session
        member_id = request.session.get('member_id')
        
        if not member_id:
            return None
        
        try:
            member = Member.objects.get(id=member_id)
            return (member, None)
        except Member.DoesNotExist:
            raise AuthenticationFailed('Invalid session')
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthenticated response.
        """
        return 'Cookie'

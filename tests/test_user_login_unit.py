"""
Unit tests for user authentication utility
"""

def check_password_changed(user, new_pass) -> bool:
    return user.check_password(new_pass)

class TestChangePasswordUnit:
    def test_change_password_success(self, unregistered_user):
        """
        Checks if password was changed correctly
        """
        new_pass = "new password"
        unregistered_user.set_password(new_pass)
        assert check_password_changed(unregistered_user, new_pass)

    def test_change_wrong_password(self, unregistered_user):
        """
        Checks if a wrong password is accepted
        """
        new_pass = "new password"
        unregistered_user.set_password(new_pass)
        random_str = "random string"
        assert not check_password_changed(unregistered_user, random_str)

    def test_change_empty_password(self, unregistered_user):
        """
        Checks if an empty password was changed correctly
        """
        new_pass = ""
        unregistered_user.set_password(new_pass)
        assert check_password_changed(unregistered_user, new_pass)

A service provider specific module (eg. Azure AD) is required for module to be useful.

The specific module HAS to implement the method `res.users.get_directory_groups()` which is supposed to get the
directory group memberships from an external directory during user login. The specific module MAY implement the method
`auth.oauth.provider.refresh_groups()` that fetches groups from an external directory in bulk.

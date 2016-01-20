from unittest import TestCase

from django.contrib.auth.models import User, Group

from hs_core.hydroshare import resource
from hs_core.hydroshare import users
from hs_core.models import GenericResource
from hs_core.testing import MockIRODSTestCaseMixin


class TestDeleteResource(MockIRODSTestCaseMixin, TestCase):

    def setUp(self):
        super(TestDeleteResource, self).setUp()
        self.group, _ = Group.objects.get_or_create(name='Hydroshare Author')
        # create a user
        self.user = users.create_account(
            'test_user@email.com',
            username='testuser',
            first_name='some_first_name',
            last_name='some_last_name',
            superuser=False,
            groups=[])

    def tearDown(self):
        self.user.delete()
        self.group.delete()
        super(TestDeleteResource, self).tearDown()

    def test_delete_resource(self):
        new_res = resource.create_resource(
            'GenericResource',
            self.user,
            'My Test Resource'
            )

        # there should be one resource at this point
        self.assertEquals(GenericResource.objects.all().count(), 1, msg="Number of resources not equal to 1")

        # delete the resource
        resource.delete_resource(new_res.short_id)

        # there should be no resource at this point
        self.assertEquals(GenericResource.objects.all().count(), 0, msg="Number of resources not equal to 0")






import datetime
from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.template import RequestContext, Template, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

from mezzanine.core.fields import FileField, RichTextField
from mezzanine.core.models import Orderable, SiteRelated
from mezzanine.core.request import current_request
from mezzanine.pages.models import Page
from mezzanine.utils.models import upload_to
from mezzanine.conf import settings


DEFAULT_COPYRIGHT = ('&copy {{% now "Y" %}} {copy}').format(copy=settings.XDCI_DEFAULT_COPYRIGHT)


class SiteConfiguration(SiteRelated):
    '''
    A model to edit sitewide content
    '''
    col1_heading = models.CharField(max_length=200, default="Contact us")
    col1_content = RichTextField()
    col2_heading = models.CharField(max_length=200, default="Follow")
    col2_content = RichTextField(blank=True,
                                 help_text="If present will override the "
                                           "social network icons.")
    col3_heading = models.CharField(max_length=200, default="Subscribe")
    col3_content = RichTextField()
    twitter_link = models.CharField(max_length=2000, blank=True)
    facebook_link = models.CharField(max_length=2000, blank=True)
    pinterest_link = models.CharField(max_length=2000, blank=True)
    youtube_link = models.CharField(max_length=2000, blank=True)
    github_link = models.CharField(max_length=2000, blank=True)
    linkedin_link = models.CharField(max_length=2000, blank=True)
    vk_link = models.CharField(max_length=2000, blank=True)
    gplus_link = models.CharField(max_length=2000, blank=True)
    has_social_network_links = models.BooleanField(default=False, blank=True)
    copyright = models.TextField(default=DEFAULT_COPYRIGHT)

    class Meta:
        verbose_name = _('Site Configuration')
        verbose_name_plural = _('Site Configuration')

    def save(self, *args, **kwargs):
        '''
        Set has_social_network_links
        '''
        if (self.twitter_link or self.facebook_link or self.pinterest_link or
            self.youtube_link or self.github_link or self.linkedin_link or
            self.vk_link or self.gplus_link):
            self.has_social_network_links = True
        else:
            self.has_social_network_links = False
        super(SiteConfiguration, self).save(*args, **kwargs)

    def render_copyright(self):
        '''
        Render the footer
        '''
        c = RequestContext(current_request())
        try:
            t = Template(self.copyright)
        except TemplateSyntaxError:
            return ''
        return t.render(c)


class HomePage(Page):
    '''
    A home page page type
    '''
    MESSAGE_TYPE_CHOICES = (('warning', 'Warning'), ('information', 'Information'))
    heading = models.CharField(max_length=100)
    slide_in_one_icon = models.CharField(max_length=50, blank=True)
    slide_in_one = models.CharField(max_length=200, blank=True)
    slide_in_two_icon = models.CharField(max_length=50, blank=True)
    slide_in_two = models.CharField(max_length=200, blank=True)
    slide_in_three_icon = models.CharField(max_length=50, blank=True)
    slide_in_three = models.CharField(max_length=200, blank=True)
    header_background = FileField(verbose_name=_("Header Background"),
        upload_to=upload_to("theme.HomePage.header_background", "homepage"),
        format="Image", max_length=255, blank=True)
    header_image = FileField(verbose_name=_("Header Image (optional)"),
        upload_to=upload_to("theme.HomePage.header_image", "homepage"),
        format="Image", max_length=255, blank=True, null=True)
    welcome_heading = models.CharField(max_length=100, default="Welcome")
    content = RichTextField()
    recent_blog_heading = models.CharField(max_length=100, default="Latest blog posts")
    number_recent_posts = models.PositiveIntegerField(default=3,
        help_text="Number of recent blog posts to show")

    # The following date fields are used for duration during which the message will be displayed
    message_start_date = models.DateField(null=True, help_text="Date from which the message will "
                                                               "be displayed")
    message_end_date = models.DateField(null=True, help_text="Date on which the message will no "
                                                             "more be displayed")

    # this must be True for the message to be displayed
    show_message = models.BooleanField(default=False, help_text="Check to show message")

    # use message type to change background color of the message
    message_type = models.CharField(max_length=100, choices=MESSAGE_TYPE_CHOICES,
                                    default='Information')

    class Meta:
        verbose_name = _("Home page")
        verbose_name_plural = _("Home pages")

    @property
    def can_show_message(self):
        if not self.show_message:
            return False
        message = strip_tags(self.content).strip()
        if not message:
            return False
        today = datetime.datetime.combine(datetime.datetime.today(), datetime.time())
        today = timezone.make_aware(today)
        today = today.date()
        if self.message_start_date and self.message_end_date:
            if self.message_start_date <= today <= self.message_end_date:
                return True

        return False


class IconBox(Orderable):
    '''
    An icon box on a HomePage
    '''
    homepage = models.ForeignKey(HomePage, related_name="boxes")
    icon = models.CharField(max_length=50,
        help_text="Enter the name of a font awesome icon, i.e. "
                  "fa-eye. A list is available here "
                  "http://fontawesome.io/")
    title = models.CharField(max_length=200)
    link_text = models.CharField(max_length=100)
    link = models.CharField(max_length=2000, blank=True,
        help_text="Optional, if provided clicking the box will go here.")


class QuotaMessage(models.Model):
    # warning_content_prepend prepends the content to form a warning message to be emailed to the
    # user and displayed when the user is logged in; grace_period_cotent_prepend prepends the
    # content when over quota within grace period and less than 125% of hard limit quota;
    # enforce_content_prepend prepends the content to form an enforcement message to inform users
    # after grace period or when they are over hard limit quota
    warning_content_prepend = models.TextField(default=('Your quota for {s_name} resources is '
                                                        '{{allocated}}{{unit}} in {{zone}} zone. You '
                                                        'currently have resources that consume '
                                                        '{{used}}{{unit}}, {{percent}}% of your quota. '
                                                        'Once your quota reaches 100% you will no '
                                                        'longer be able to create new resources in '
                                                        '{s_name}. '
                                                       ).format(s_name=settings.XDCI_SITE_NAME_MIXED))
    grace_period_content_prepend = models.TextField(default=('You have exceeded your {s_name} '
                                                             'quota. Your quota for {s_name} '
                                                             'resources is {{allocated}}{{unit}} in '
                                                             '{{zone}} zone. You currently have '
                                                             'resources that consume {{used}}{{unit}}, '
                                                             '{{percent}}% of your quota. You have a '
                                                             'grace period until {{cut_off_date}} to '
                                                             'reduce your use to below your quota, '
                                                             'or to acquire additional quota, after '
                                                             'which you will no longer be able to '
                                                             'create new resources in {s_name}. '
                                                            ).format(s_name=settings.XDCI_SITE_NAME_MIXED))
    enforce_content_prepend = models.TextField(default=('Your action to add content to {s_name} '
                                                        'was refused because you have exceeded your '
                                                        'quota. Your quota for {s_name} resources '
                                                        'is {{allocated}}{{unit}} in {{zone}} zone. You '
                                                        'currently have resources that consume '
                                                        '{{used}}{{unit}}, {{percent}}% of your quota. '
                                                       ).format(s_name=settings.XDCI_SITE_NAME_MIXED))
    content = models.TextField(default=('To request additional quota, please contact '
                                        '{{email}}. We will try to accommodate '
                                        'reasonable requests for additional quota. If you have a '
                                        'large quota request you may need to contribute toward the '
                                        'costs of providing the additional space you need. See '
                                        'https://{pages}/{about}/policies/'
                                        'quota/ for more information about the quota policy.'
                                       ).format(pages=settings.XDCI_PAGES_DOMAIN_NAME,
                                                about=settings.XDCI_ABOUT_PATH))
    # quota soft limit percent value for starting to show quota usage warning. Default is 80%
    soft_limit_percent = models.IntegerField(default=80)
    # quota hard limit percent value for hard quota enforcement. Default is 125%
    hard_limit_percent = models.IntegerField(default=125)
    # grace period, default is 7 days
    grace_period = models.IntegerField(default=7)


class UserQuota(models.Model):
    # ForeignKey relationship makes it possible to associate multiple UserQuota models to
    # a User with each UserQuota model defining quota for a set of iRODS zones. By default,
    # the UserQuota model instance defines quota in hydroshareZone and hydroshareuserZone,
    # categorized as hydroshare_internal in zone field in UserQuota model, however,
    # another UserQuota model instance could be defined in a third-party federated zone as needed.
    user = models.ForeignKey(User,
                             editable=False,
                             null=False,
                             on_delete=models.CASCADE,
                             related_name='quotas',
                             related_query_name='quotas')

    allocated_value = models.BigIntegerField(default=20)
    used_value = models.BigIntegerField(default=0)
    unit = models.CharField(max_length=10, default="GB")
    zone = models.CharField(max_length=100, default=settings.XDCI_ZONE)
    # remaining_grace_period to be quota-enforced. Default is -1 meaning the user is below
    # soft quota limit and thus grace period has not started. When grace period is 0, quota
    # enforcement takes place
    remaining_grace_period = models.IntegerField(default=-1)
    class Meta:
        verbose_name = _("User quota")
        verbose_name_plural = _("User quotas")
        unique_together = ('user', 'zone')

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    picture = models.ImageField(upload_to='profile', null=True, blank=True)
    middle_name = models.CharField(max_length=1024, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    title = models.CharField(
        max_length=1024, null=True, blank=True,
        help_text='e.g. Assistant Professor, Program Director, Adjunct Professor, Software Developer.')
    user_type = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        default='Unspecified'
    )
    subject_areas = models.CharField(
        max_length=1024, null=True, blank=True,
        help_text=('A comma-separated list of subject areas you are interested in researching. e.g. "{subject_areas}"'
                  ).format(subject_areas=settings.XDCI_EXAMPLE_SUBJECT_AREAS))
    organization = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="The name of the organization you work for."
    )
    phone_1 = models.CharField(max_length=1024, null=True, blank=True)
    phone_1_type = models.CharField(max_length=1024, null=True, blank=True, choices=(
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Mobile', 'Mobile'),
    ))
    phone_2 = models.CharField(max_length=1024, null=True, blank=True)
    phone_2_type = models.CharField(max_length=1024, null=True, blank=True, choices=(
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Mobile', 'Mobile'),
    ))
    public = models.BooleanField(default=True, help_text='Uncheck to make your profile contact information and '
                                                         'details private.')
    cv = models.FileField(upload_to='profile',
                          help_text='Upload your Curriculum Vitae if you wish people to be able to download it.',
                          null=True, blank=True)
    details = models.TextField("Description",
                               help_text=('Tell the {s_name} community a little about yourself.'
                                         ).format(s_name=settings.XDCI_SITE_NAME_MIXED),
                               null=True, blank=True)

    GENDER_NO_DISCLOSURE = 'ND'
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER = 'O'
    GENDER_CHOICES = (
        (GENDER_NO_DISCLOSURE, 'Prefer not to disclose'),
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    )
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, default=None, null=True, blank=True)
    date_of_birth = models.CharField(max_length=1024, null=True, blank=True)
    address_1 = models.CharField(max_length=1024, null=True, blank=True)
    address_2 = models.CharField(max_length=1024, null=True, blank=True)
    city = models.CharField(max_length=1024, null=True, blank=True)
    zipcode = models.CharField(max_length=1024, null=True, blank=True)
    last_four_ss = models.PositiveSmallIntegerField( null=True, blank=True, validators=[MaxValueValidator(9999)])
    emergency_name = models.CharField(max_length=1024, null=True, blank=True)
    emergency_relationship = models.CharField(max_length=1024, null=True, blank=True)
    emergency_email = models.CharField(max_length=1024, null=True, blank=True)
    emergency_phone_1 = models.CharField(max_length=1024, null=True, blank=True)
    emergency_phone_2 = models.CharField(max_length=1024, null=True, blank=True)

    state = models.CharField(max_length=1024, null=True, blank=True)
    country = models.CharField(max_length=1024, null=True, blank=True)

    create_irods_user_account = models.BooleanField(default=False,
                                                    help_text=('Check to create an iRODS user account in {s_name} user '
                                                               'iRODS space for staging large files (>2GB) using iRODS '
                                                               'clients such as Cyberduck (https://cyberduck.io/) '
                                                               'and icommands (https://docs.irods.org/master/icommands/user/).'
                                                               'Uncheck to delete your iRODS user account. '
                                                               'Note that deletion of your iRODS user account deletes all '
                                                               'of your files under this account as well.'
                                                              ).format(s_name=settings.XDCI_SITE_NAME_MIXED))

def force_unique_emails(sender, instance, **kwargs):
    if instance:
        email = instance.email
        username = instance.username

        if not email:
            raise ValidationError("Email required.")
        else:
            if sender.objects.filter(username=username).exclude(pk=instance.id).exists():
                raise ValidationError("Username already in use.")
        if sender.objects.filter(email=email).exclude(pk=instance.id).count():
            raise ValidationError("Email already in use.")

pre_save.connect(force_unique_emails, sender=User)

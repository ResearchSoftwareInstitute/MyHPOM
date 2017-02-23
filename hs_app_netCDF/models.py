import json

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation

from mezzanine.pages.page_processors import processor_for

from dominate.tags import legend, table, tbody, tr, td, th, h4, div, strong

from hs_core.models import BaseResource, ResourceManager
from hs_core.models import resource_processor, CoreMetaData, AbstractMetaDataElement
from hs_core.hydroshare.utils import get_resource_file_name_and_extension


# Define original spatial coverage metadata info
class OriginalCoverage(AbstractMetaDataElement):
    PRO_STR_TYPES = (
        ('', '---------'),
        ('WKT String', 'WKT String'),
        ('Proj4 String', 'Proj4 String')
    )

    term = 'OriginalCoverage'
    """
    _value field stores a json string. The content of the json as box coverage info
         _value = "{'northlimit':northenmost coordinate value,
                    'eastlimit':easternmost coordinate value,
                    'southlimit':southernmost coordinate value,
                    'westlimit':westernmost coordinate value,
                    'units:units applying to 4 limits (north, east, south & east),
                    'projection': name of the projection (optional)}"
    """
    _value = models.CharField(max_length=1024, null=True)
    projection_string_type = models.CharField(max_length=20, choices=PRO_STR_TYPES, null=True)
    projection_string_text = models.TextField(null=True, blank=True)
    datum = models.CharField(max_length=300, blank=True)

    class Meta:
        # OriginalCoverage element is not repeatable
        unique_together = ("content_type", "object_id")

    @property
    def value(self):
        return json.loads(self._value)

    @classmethod
    def create(cls, **kwargs):
        """
        The '_value' subelement needs special processing. (Check if the 'value' includes the
        required information and convert 'value' dict as Json string to be the '_value'
        subelement value.) The base class create() can't do it.

        :param kwargs: the 'value' in kwargs should be a dictionary
                       the '_value' in kwargs is a serialized json string
        """
        value_arg_dict = None
        if 'value' in kwargs:
            value_arg_dict = kwargs['value']
        elif '_value' in kwargs:
            value_arg_dict = json.loads(kwargs['_value'])

        if value_arg_dict:
            # check that all the required sub-elements exist and create new original coverage meta
            for value_item in ['units', 'northlimit', 'eastlimit', 'southlimit', 'westlimit']:
                if value_item not in value_arg_dict:
                    raise ValidationError("For original coverage meta, one or more bounding "
                                          "box limits or 'units' is missing.")

            value_dict = {k: v for k, v in value_arg_dict.iteritems()
                          if k in ('units', 'northlimit', 'eastlimit', 'southlimit',
                                   'westlimit', 'projection')}

            value_json = json.dumps(value_dict)
            if 'value' in kwargs:
                del kwargs['value']
            kwargs['_value'] = value_json
            return super(OriginalCoverage, cls).create(**kwargs)
        else:
            raise ValidationError('Coverage value is missing.')

    @classmethod
    def update(cls, element_id, **kwargs):
        """
        The '_value' subelement needs special processing. (Convert 'value' dict as Json string
        to be the '_value' subelement value) and the base class update() can't do it.

        :param kwargs: the 'value' in kwargs should be a dictionary
        """

        ori_cov = OriginalCoverage.objects.get(id=element_id)
        if 'value' in kwargs:
            value_dict = ori_cov.value

            for item_name in ('units', 'northlimit', 'eastlimit', 'southlimit',
                              'westlimit', 'projection'):
                if item_name in kwargs['value']:
                    value_dict[item_name] = kwargs['value'][item_name]

            value_json = json.dumps(value_dict)
            del kwargs['value']
            kwargs['_value'] = value_json
            super(OriginalCoverage, cls).update(element_id, **kwargs)

    def get_html_form(self, resource):
        """Generates html form code for this metadata element so that this element can be edited"""

        from .forms import OriginalCoverageForm

        ori_coverage_data_dict = dict()
        ori_coverage_data_dict['projection'] = self.value.get('projection', None)
        ori_coverage_data_dict['datum'] = self.datum
        ori_coverage_data_dict['projection_string_type'] = self.projection_string_type
        ori_coverage_data_dict['projection_string_text'] = self.projection_string_text
        ori_coverage_data_dict['units'] = self.value['units']
        ori_coverage_data_dict['northlimit'] = self.value['northlimit']
        ori_coverage_data_dict['eastlimit'] = self.value['eastlimit']
        ori_coverage_data_dict['southlimit'] = self.value['southlimit']
        ori_coverage_data_dict['westlimit'] = self.value['westlimit']

        originalcov_form = OriginalCoverageForm(
            initial=ori_coverage_data_dict, allow_edit=True,
            res_short_id=resource.short_id if resource else None,
            element_id=self.id if self else None)

        return originalcov_form

    def get_html(self, pretty=True):
        """Generates html code for displaying data for this metadata element"""

        root_div = div(cls="col-xs-6 col-sm-6", style="margin-bottom:40px;")

        def get_th(heading_name):
            return th(heading_name, cls="text-muted")

        with root_div:
            legend('Spatial Reference')
            with table(cls='custom-table'):
                with tbody():
                    with tr():
                        get_th('Coordinate Reference System')
                        td(self.value.get('projection', ''))
                    with tr():
                        get_th('Datum')
                        td(self.datum)
                    with tr():
                        get_th('Coordinate String Type')
                        td(self.projection_string_type)
                    with tr():
                        get_th('Coordinate String Text')
                        td(self.projection_string_text)
            h4('Extent')
            with table(cls='custom-table'):
                with tbody():
                    with tr():
                        get_th('North')
                        td(self.value['northlimit'])
                    with tr():
                        get_th('West')
                        td(self.value['westlimit'])
                    with tr():
                        get_th('South')
                        td(self.value['southlimit'])
                    with tr():
                        get_th('East')
                        td(self.value['eastlimit'])
                    with tr():
                        get_th('Unit')
                        td(self.value['units'])

        return root_div.render(pretty=pretty)


# Define netCDF variable metadata
class Variable(AbstractMetaDataElement):
    # variable types are defined in OGC enhanced_data_model_extension_standard
    # left is the given value stored in database right is the value for the drop down list
    VARIABLE_TYPES = (
        ('Char', 'Char'),  # 8-bit byte that contains uninterpreted character data
        ('Byte', 'Byte'),  # integer(8bit)
        ('Short', 'Short'),  # signed integer (16bit)
        ('Int', 'Int'),  # signed integer (32bit)
        ('Float', 'Float'),  # floating point (32bit)
        ('Double', 'Double'),  # floating point(64bit)
        ('Int64', 'Int64'),  # integer(64bit)
        ('Unsigned Byte', 'Unsigned Byte'),
        ('Unsigned Short', 'Unsigned Short'),
        ('Unsigned Int', 'Unsigned Int'),
        ('Unsigned Int64', 'Unsigned Int64'),
        ('String', 'String'),  # variable length character string
        ('User Defined Type', 'User Defined Type'),  # compound, vlen, opaque, enum
        ('Unknown', 'Unknown')
    )
    term = 'Variable'
    # required variable attributes
    name = models.CharField(max_length=1000)
    unit = models.CharField(max_length=1000)
    type = models.CharField(max_length=1000, choices=VARIABLE_TYPES)
    shape = models.CharField(max_length=1000)
    # optional variable attributes
    descriptive_name = models.CharField(max_length=1000, null=True, blank=True,
                                        verbose_name='long name')
    method = models.TextField(null=True, blank=True, verbose_name='comment')
    missing_value = models.CharField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def remove(cls, element_id):
        raise ValidationError("The variable of the resource can't be deleted.")

    def get_html(self, pretty=True):
        """Generates html code for displaying data for this metadata element"""

        root_div = div(cls="col-xs-12 pull-left", style="margin-top:10px;")

        def get_th(heading_name):
            return th(heading_name, cls="text-muted")

        with root_div:
            with div(cls="custom-well"):
                strong(self.name)
                with table(cls='custom-table'):
                    with tbody():
                        with tr():
                            get_th('Unit')
                            td(self.unit)
                        with tr():
                            get_th('Type')
                            td(self.type)
                        with tr():
                            get_th('Shape')
                            td(self.shape)
                        if self.descriptive_name:
                            with tr():
                                get_th('Long Name')
                                td(self.descriptive_name)
                        if self.missing_value:
                            with tr():
                                get_th('Missing Value')
                                td(self.missing_value)
                        if self.method:
                            with tr():
                                get_th('Comment')
                                td(self.method)

        return root_div.render(pretty=pretty)


# Define the netCDF resource
class NetcdfResource(BaseResource):
    objects = ResourceManager("NetcdfResource")

    @property
    def metadata(self):
        md = NetcdfMetaData()
        return self._get_metadata(md)

    @classmethod
    def get_supported_upload_file_types(cls):
        # 3 file types are supported
        return (".nc",)

    @classmethod
    def allow_multiple_file_upload(cls):
        # can upload only 1 file
        return False

    @classmethod
    def can_have_multiple_files(cls):
        # can have only 1 file
        return False

    # add resource-specific HS terms
    def get_hs_term_dict(self):
        # get existing hs_term_dict from base class
        hs_term_dict = super(NetcdfResource, self).get_hs_term_dict()
        # add new terms for NetCDF res
        hs_term_dict["HS_NETCDF_FILE_NAME"] = ""
        for res_file in self.files.all():
            _, f_fullname, f_ext = get_resource_file_name_and_extension(res_file)
            if f_ext.lower() == '.nc':
                hs_term_dict["HS_NETCDF_FILE_NAME"] = f_fullname
                break
        return hs_term_dict

    class Meta:
        verbose_name = 'Multidimensional (NetCDF)'
        proxy = True

processor_for(NetcdfResource)(resource_processor)


class NetCDFMetaDataMixin(models.Model):
    """This class must be the first class in the multi-inheritance list of classes"""
    variables = GenericRelation(Variable)
    ori_coverage = GenericRelation(OriginalCoverage)

    class Meta:
        abstract = True

    @property
    def originalCoverage(self):
        return self.ori_coverage.all().first()

    def has_all_required_elements(self):
        if not super(NetCDFMetaDataMixin, self).has_all_required_elements():  # check required meta
            return False
        if not self.variables.all():
            return False
        if not (self.coverages.all().filter(type='box').first() or
                self.coverages.all().filter(type='point').first()):
            return False
        return True

    def get_required_missing_elements(self):  # show missing required meta
        missing_required_elements = super(NetCDFMetaDataMixin, self).get_required_missing_elements()
        if not (self.coverages.all().filter(type='box').first() or
                self.coverages.all().filter(type='point').first()):
            missing_required_elements.append('Spatial Coverage')
        if not self.variables.all().first():
            missing_required_elements.append('Variable')

        return missing_required_elements

    def delete_all_elements(self):
        super(NetCDFMetaDataMixin, self).delete_all_elements()
        self.ori_coverage.all().delete()
        self.variables.all().delete()

    @classmethod
    def get_supported_element_names(cls):
        # get the names of all core metadata elements
        elements = super(NetCDFMetaDataMixin, cls).get_supported_element_names()
        # add the name of any additional element to the list
        elements.append('Variable')
        elements.append('OriginalCoverage')
        return elements


# define the netcdf metadata
class NetcdfMetaData(NetCDFMetaDataMixin, CoreMetaData):
    # variables = GenericRelation(Variable)
    # ori_coverage = GenericRelation(OriginalCoverage)

    # @classmethod
    # def get_supported_element_names(cls):
    #     # get the names of all core metadata elements
    #     elements = super(NetcdfMetaData, cls).get_supported_element_names()
    #     # add the name of any additional element to the list
    #     elements.append('Variable')
    #     elements.append('OriginalCoverage')
    #     return elements

    @property
    def resource(self):
        return NetcdfResource.objects.filter(object_id=self.id).first()

    # def has_all_required_elements(self):
    #     if not super(NetcdfMetaData, self).has_all_required_elements():  # check required meta
    #         return False
    #     if not self.variables.all():
    #         return False
    #     if not (self.coverages.all().filter(type='box').first() or
    #             self.coverages.all().filter(type='point').first()):
    #         return False
    #     return True

    # def get_required_missing_elements(self):  # show missing required meta
    #     missing_required_elements = super(NetcdfMetaData, self).get_required_missing_elements()
    #     if not (self.coverages.all().filter(type='box').first() or
    #             self.coverages.all().filter(type='point').first()):
    #         missing_required_elements.append('Spatial Coverage')
    #     if not self.variables.all().first():
    #         missing_required_elements.append('Variable')
    #
    #     return missing_required_elements

    def get_xml(self, pretty_print=True):
        from lxml import etree
        # get the xml string representation of the core metadata elements
        xml_string = super(NetcdfMetaData, self).get_xml(pretty_print=pretty_print)

        # create an etree xml object
        RDF_ROOT = etree.fromstring(xml_string)

        # get root 'Description' element that contains all other elements
        container = RDF_ROOT.find('rdf:Description', namespaces=self.NAMESPACES)

        # inject netcdf resource specific metadata element 'variable' to container element
        for variable in self.variables.all():
            md_fields = {
                "md_element": "netcdfVariable",
                "name": "name",
                "unit": "unit",
                "type": "type",
                "shape": "shape",
                "descriptive_name": "longName",
                "method": "comment",
                "missing_value": "missingValue"
            }  # element name : name in xml
            self.add_metadata_element_to_xml(container, variable, md_fields)

        if self.ori_coverage.all().first():
            ori_cov_obj = self.ori_coverage.all().first()
            hsterms_ori_cov = etree.SubElement(container, '{%s}spatialReference' %
                                               self.NAMESPACES['hsterms'])
            cov_term = '{%s}' + 'box'
            hsterms_coverage_terms = etree.SubElement(hsterms_ori_cov, cov_term %
                                                      self.NAMESPACES['hsterms'])

            hsterms_ori_cov_rdf_Description = etree.SubElement(hsterms_coverage_terms, '{%s}value' %
                                                               self.NAMESPACES['rdf'])
            cov_box = ''

            # add extent info
            if ori_cov_obj.value:
                cov_box = 'northlimit=%s; eastlimit=%s; southlimit=%s; westlimit=%s; unit=%s' \
                        % (ori_cov_obj.value['northlimit'], ori_cov_obj.value['eastlimit'],
                           ori_cov_obj.value['southlimit'], ori_cov_obj.value['westlimit'],
                           ori_cov_obj.value['units'])

            if ori_cov_obj.value.get('projection'):
                cov_box += '; projection_name={}'.format(ori_cov_obj.value['projection'])

            if ori_cov_obj.projection_string_text:
                cov_box += '; projection_string={}'.format(ori_cov_obj.projection_string_text)

            if ori_cov_obj.datum:
                cov_box += '; datum={}'.format(ori_cov_obj.datum)

            hsterms_ori_cov_rdf_Description.text = cov_box

        return etree.tostring(RDF_ROOT, pretty_print=pretty_print)

    def add_metadata_element_to_xml(self, root, md_element, md_fields):
        from lxml import etree
        element_name = md_fields.get('md_element') if md_fields.get('md_element') \
            else md_element.term

        hsterms_newElem = etree.SubElement(
            root,
            "{{{ns}}}{new_element}".format(ns=self.NAMESPACES['hsterms'], new_element=element_name))

        hsterms_newElem_rdf_Desc = etree.SubElement(
            hsterms_newElem, "{{{ns}}}Description".format(ns=self.NAMESPACES['rdf']))

        for md_field in md_fields.keys():
            if hasattr(md_element, md_field):
                attr = getattr(md_element, md_field)
                if attr:
                    field = etree.SubElement(hsterms_newElem_rdf_Desc,
                                             "{{{ns}}}{field}".format(ns=self.NAMESPACES['hsterms'],
                                                                      field=md_fields[md_field]))
                    field.text = str(attr)

    # def delete_all_elements(self):
    #     super(NetcdfMetaData, self).delete_all_elements()
    #     self.ori_coverage.all().delete()
    #     self.variables.all().delete()

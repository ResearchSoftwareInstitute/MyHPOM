**MyHPOM Web Service API Design**

March 19, 2015

Version 1.0

Jeffery S. Horsburgh, Brian Miles, Dan Ames, Jefferson Heard

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Introduction](#introduction)
- [Development Approach](#development-approach)
- [Authentication and Authorization](#authentication-and-authorization)
- [Web Service Interface Definitions](#web-service-interface-definitions)
  - [Resource Management API](#resource-management-api)
  - [User Management and Authorization API](#user-management-and-authorization-api)
  - [Resource Discovery API](#resource-discovery-api)
  - [Social API](#social-api)
  - [DataONE Member Node API](#dataone-member-node-api)
- [Acknowledgements](#acknowledgements)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


Introduction
============

MyHPOM will expose web service Application Programmer Interfaces (APIs) that support interaction between client applications and the main MyHPOM system and facilitate development of these client applications. MyHPOM will also expose web services that conform to the DataONE web service end-point specifications defined in the DataONE architectural documentation (DataONE, 2013). However compliance with DataONE data format specifications will not be guaranteed in the initial version of the MyHPOM API. Data format compliance would need to be added at a later date so that MyHPOM can become a DataONE Member Node as described in the MyHPOM Data Management Plan. As a design principle, the MyHPOM web service APIs will expose the same functionality that can be accomplished through the MyHPOM web user interface so that client applications can mimic that functionality.

Development Approach
====================

In general, MyHPOM web services will be implemented using a Representational State Transfer (REST) based approach using HTTP as the transport protocol and XML and/or JSON for encoding messages. The current development approach is investigating use of the Tastypie (<http://tastypieapi.org/>) web service API framework for the Django (<https://www.djangoproject.com/>) web framework.

Authentication and Authorization
================================

Many of the MyHPOM web service API functions require authorization. The MyHPOM web service APIs will use the same access control scheme as the MyHPOM web user interface. If a user is authorized to do something in the web interface, they will be authorized to do it via the web service APIs as well.

Web Service Interface Definitions
=================================

The following sections describe the MyHPOM web service APIs. The APIs will be versioned, and users will be able to specify the version number in the URL of their REST requests. In each section, a table lists the functions included in each API and then details of each function are given following the table. Note that API endpoints that rely on filtering are formatted according to TastyPie conventions. The formatting of such endpoints are subject to change to reflect the actual API implementation, which may not use TastyPie.

Resource Management API
-----------------------

The MyHPOM Resource Management API will enable client applications to create new resources, retrieve existing resources, get metadata for existing resources, update existing resources, publish resources, and delete resources. The table below lists the REST URLs that will be implemented as part of the MyHPOM Resource Management API.

Table 1. Summary of MyHPOM Resource Management API methods.

| **Release** | **REST Path**                           | **Function**                       | **Parameters**                  |
|-------------|-----------------------------------------|------------------------------------|---------------------------------|
| 1           | GET /resource/{pid}                     | MyHPOM.getResource()           | (pid) --\> OctetStream          |
| 1           | GET /scimeta/{pid}                      | MyHPOM.getScienceMetadata()    | (pid) --\> ScienceMetadata      |
| 1           | GET /sysmeta/{pid}                      | MyHPOM.getSystemMetadata()     | (pid) --\> SystemMetadata       |
| 1           | GET /resourcemap/{pid}                  | MyHPOM.getResourceMap()        | (pid) --\> ResourceMap          |
| 1           | GET /resource/{pid}/files/{filename}    | MyHPOM.getResourceFile()       | (pid, filename) --\> file       |
| 4           | GET /revisions/{pid}                    | MyHPOM.getRevisions()          | (pid) --\> ResourceList         |
| 4           | GET /related/{pid}                      | MyHPOM.getRelated()            | (pid) --\> ResourceList         |
| 1           | GET /checksum/{pid}                     | MyHPOM.getChecksum()           | (pid) --\> Checksum             |
| 1           | POST /resource                          | MyHPOM.createResource()        | (Resource) --\> pid             |
| 1           | PUT /resource/{pid}                     | MyHPOM.updateResource()        | (pid, Resource) --\> pid        |
| 1           | PUT /resource/{pid}/ files/{file}       | MyHPOM.addResourceFile()       | (pid, file) --\> pid            |
| 1           | PUT /scimeta/{pid}                      | MyHPOM.updateScienceMetadata() | (pid, ScienceMetadata) --\> pid |
| 1           | DELETE /resource/{pid}                  | MyHPOM.deleteResource()        | (pid) --\> pid                  |
| 1           | DELETE /resource/{pid}/files/{filename} | MyHPOM.deleteResourceFile()    | (pid, filename) --\> pid        |
| 4           | PUT /publishResource/{pid}              | MyHPOM.publishResource()       | (pid) --\> pid                  |
| 4           | GET /resolveDOI/{doi}                   | MyHPOM.resolveDOI()            | (doi) --\> pid                  |


### MyHPOM.getResource**(*pid*)* --\> OctetStream

Retrieve a resource identified by the pid from MyHPOM. The response must contain the bytes of the indicated resource, and the checksum of the bytes retrieved should match the checksum recorded in the system metadata for that resource. The bytes of the resource will be encoded as a zipped BagIt archive; this archive will contain resource contents as well as science metadata. If the resource does not exist in MyHPOM, then Exceptions.NotFound must be raised. Resources can be any unit of content within MyHPOM that has been assigned a pid.

**REST URL**: GET /resource/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource to be retrieved.

**Returns**: Bytes of the specified resource.

**Return Type**: OctetStream

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request

**Notes**: All resources and resource versions will have a unique internal MyHPOM identifier (pid). A DOI will be assigned to all formally published versions of a resource. For this method, passing in a pid (which is a MyHPOM internal identifer) would return a specific resource version corresponding to the pid. A DOI would have to be resolved using MyHPOM.resolveDOI() to get the pid for the resource, which could then be used with this method. The obsoletion chain will be contained within the system metadata for resources and so it can be traversed by calling MyHPOM.getSystemMetadata().


### MyHPOM.getScienceMetadata**(*pid*)* --\> ScienceMetadata

Describes the resource identified by the pid by returning the associated science metadata object. If the resource does not exist, Exceptions.NotFound must be raised.

**REST URL**: GET /scimeta/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource whose science metadata is to be retrieved.

**Returns**: Science metadata XML document describing the resource.

**Return Type**: ScienceMetadata

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.getSystemMetadata**(*pid*)* --\> SystemMetadata

Describes the resource identified by the pid by returning the associated system metadata object. If the resource does not exist, Exceptions.NotFound must be raised.

**REST URL**: GET /sysmeta/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource whose system metadata is to be retrieved.

**Returns**: System metadata XML document describing the resource.

**Return Type**: SystemMetadata

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.getResourceMap**(*pid*)* --\> ResourceMap

Describes the resource identified by the pid by returning the associated resource map document. If the resource does not exist, Exceptions.NotFound must be raised.

**REST URL**: GET /resourcemap/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource whose resource map is to be retrieved.

**Returns**: Resource map XML document describing the resource.

**Return Type**: ResourceMap

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.getResourceFile**(*pid*, *filename*)* --\> file

Called by clients to get an individual file within a MyHPOM resource.

**REST URL**: GET /resource/{pid}/files/{filename}

**Parameters**: pid – Unique MyHPOM identifier for the resource from which the file will be extracted.

filename – The data bytes of the file that will be extracted from the resource identified by pid

**Returns**: The bytes of the file extracted from the resource, with MIME type corresponding to filename extension.

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist or the file identified by filename does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.getRevisions**(*pid*)* --\> List of pids

Returns a list of pids for resources that are revisions of the resource identified by the specified pid.

**REST URL**: GET /revisions/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource whose revisions are to be retrieved.

**Returns**: List of pids for resources that are revisions of the specified resource.

**Return Type**: List of pids

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The Resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.getRelated**(*pid*)* --\> List of pids

Returns a list of pids for resources that are related to the resource identified by the specified pid.

**REST URL**: GET /related/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource whose related resources are to be retrieved.

**Returns**: List of pids for resources that are related to the specified resource.

**Return Type**: List of pids

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.getChecksum**(*pid*)* --\> Checksum

Returns a checksum for the specified resource using the MD5 algorithm. The result is used to determine if two instances referenced by a pid are identical.

**REST URL**: GET /checksum/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource for which the checksum is to be returned.

**Returns**: Checksum of the resource identified by pid.

**Return Type**: Checksum

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource specified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.createResource**(*resource*)* --\> pid

Called by a client to add a new resource to MyHPOM. The caller must have authorization to write content to MyHPOM. The pid for the resource is assigned by MyHPOM upon inserting the resource.  The create method returns the newly-assigned pid.

**REST URL**: POST /resource

**Parameters**: resource – The data bytes of the resource, encoded as a zipped BagIt archive, to be added to MyHPOM

**Returns**: The pid assigned to the newly created resource

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized to write to MyHPOM

Exceptions.InvalidContent – The content of the resource is incomplete

Exception.ServiceFailure – The service is unable to process the request

**Note**: The calling user will automatically be set as the owner of the created resource.


### MyHPOM.updateResource**(*pid*, *resource*)* --\> pid

Called by clients to update a resource in MyHPOM.

**REST URL**: PUT /resource/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource that is to be updated.

resource – The data bytes of the resource, encoded as a zipped BagIt archive, that will update the existing resource identified by pid

**Returns**: The pid assigned to the updated resource

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.InvalidContent – The content of the resource is incomplete

Exception.ServiceFailure – The service is unable to process the request

**Notes**: For mutable resources (resources that have not been formally published), the update overwrites existing data and metadata using the resource that is passed to this method. If a user wants to create a copy or modified version of a mutable resource this should be done using MyHPOM.createResource().

For immutable resources (formally published resources), this method creates a new resource that is a new version of the formally published resource. MyHPOM will record the update by storing the SystemMetadata.obsoletes and SystemMetadata.obsoletedBy fields for the respective resources in their system metadata. MyHPOM MUST check or set the values of SystemMetadata.obsoletes and SystemMetadata.obsoletedBy so that they accurately represent the relationship between the new and old objects. MyHPOM MUST also set SystemMetadata.dateSysMetadataModified. The modified system metadata entries must then be available in MyHPOM.listObjects() to ensure that any cataloging systems pick up the changes when filtering on SystmeMetadata.dateSysMetadataModified. A formally published resource can only be obsoleted by one newer version. Once a resource is obsoleted, no other resources can obsolete it.


### MyHPOM.addResourceFile**(*pid*, *file*)* --\> pid

Called by clients to update a resource in MyHPOM by adding a single file.

**REST URL**: PUT /resource/{pid}/files/{file}

**Parameters**: pid – Unique MyHPOM identifier for the resource that is to be updated.

file – The data bytes of the file that will be added to the existing resource identified by pid

**Returns**: The pid assigned to the updated resource

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.InvalidContent – The content of the file is invalid

Exception.ServiceFailure – The service is unable to process the request

**Notes**: For mutable resources (resources that have not been formally published), the update adds the file that is passed to this method to the resource. For immutable resources (formally published resources), this method creates a new resource that is a new version of the formally published resource. MyHPOM will record the update by storing the SystemMetadata.obsoletes and SystemMetadata.obsoletedBy fields for the respective resources in their system metadata. MyHPOM MUST check or set the values of SystemMetadata.obsoletes and SystemMetadata.obsoletedBy so that they accurately represent the relationship between the new and old objects. MyHPOM MUST also set SystemMetadata.dateSysMetadataModified. The modified system metadata entries must then be available in MyHPOM.listObjects() to ensure that any cataloging systems pick up the changes when filtering on SystmeMetadata.dateSysMetadataModified. A formally published resource can only be obsoleted by one newer version. Once a resource is obsoleted, no other resources can obsolete it.


### MyHPOM.updateScienceMetadata**(*pid, ScienceMetadata*)* --\> pid

Called by clients to update the science metadata for a resource in MyHPOM.

**REST URL**: PUT /scimeta/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource that is to be updated.

ScienceMetadata – The data bytes of the XML ScienceMetadata that will update the existing Science Metadata for the resource identified by pid

**Returns**: The pid assigned to the resource whose Science Metadata was updated

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.InvalidContent – The content of the resource is incomplete

Exception.ServiceFailure – The service is unable to process the request

**Notes**: For mutable resources (resources that have not been formally published), the update overwrites existing Science Metadata using the ScienceMetadata that is passed to this method. For immutable resources (formally published resources), this method creates a new resource that is a new version of the formally published resource. MyHPOM will record the update by storing the SystemMetadata.obsoletes and SystemMetadata.obsoletedBy fields for the respective resources in their system metadata. MyHPOM MUST check or set the values of SystemMetadata.obsoletes and SystemMetadata.obsoletedBy so that they accurately represent the relationship between the new and old objects. MyHPOM MUST also set SystemMetadata.dateSysMetadataModified. The modified system metadata entries must then be available in MyHPOM.listObjects() to ensure that any cataloging systems pick up the changes when filtering on SystmeMetadata.dateSysMetadataModified. A formally published resource can only be obsoleted by one newer version. Once a resource is obsoleted, no other resources can obsolete it.


### MyHPOM.deleteResource**(*pid*)* --\> pid

Deletes a resource managed by MyHPOM. The caller must be an owner of the resource or an administrator to perform this function. The operation removes the resource from further interaction with MyHPOM services and interfaces. The implementation may delete the resource bytes, and should do so since a delete operation may be in response to a problem with the resource (e.g., it contains malicious content, is inappropriate, or is subject to a legal request). If the resource does not exist, the Exceptions.NotFound exception is raised.

**REST URL**: DELETE /resource/{pid}

**Parameters**: pid – The unique MyHPOM identifier of the resource to be deleted

**Returns**: The pid of the resource that was deleted

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: Only MyHPOM administrators will be able to delete formally published resources.


### MyHPOM.deleteResourceFile**(*pid, filename*)* --\> pid

Deletes an individual file from a MyHPOM resource. If the file does not exist, the Exceptions.NotFound exception is raised.

**REST URL**: DELETE /resource/{pid}/files/{filename}

**Parameters**: pid – The unique MyHPOM identifier for the resource from which the file will be deleted

filename – Name of the file to be deleted from the resource

**Returns**: The pid of the resource from which the file was deleted

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist or the file identified by file does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: For mutable resources (resources that have not been formally published), this method modifies the resource by deleting the file. For immutable resources (formally published resources), this method creates a new resource that is a new version of the formally published resource. MyHPOM will record the update by storing the SystemMetadata.obsoletes and SystemMetadata.obsoletedBy fields for the respective resources in their system metadata. MyHPOM MUST check or set the values of SystemMetadata.obsoletes and SystemMetadata.obsoletedBy so that they accurately represent the relationship between the new and old objects. MyHPOM MUST also set SystemMetadata.dateSysMetadataModified. The modified system metadata entries must then be available in MyHPOM.listObjects() to ensure that any cataloging systems pick up the changes when filtering on SystemMetadata.dateSysMetadataModified. A formally published resource can only be obsoleted by one newer version. Once a resource is obsoleted, no other resources can obsolete it.


### MyHPOM.publishResource**(*pid*)* --\> pid

Formally publishes a resource in MyHPOM. Triggers the creation of a DOI for the resource, and triggers the exposure of the resource to the MyHPOM DataONE Member Node. The user must be an owner of a resource or an adminstrator to perform this action.

**REST URL**: PUT /publishResource/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource to be formally published.

**Returns**: The pid of the resource that was published

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: This is different than just giving public access to a resource via access control rules.


### MyHPOM.resolveDOI**(*doi*)* --\> pid

Takes as input a DOI and returns the internal MyHPOM identifier (pid) for a resource. This method will be used to get the MyHPOM pid for a resource identified by a doi for further operations using the web service API.

**REST URL**: GET /resolveDOI/{doi}

**Parameters**: doi – A doi assigned to a resource in MyHPOM.

**Returns**: The pid of the resource that was published

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: All MyHPOM methods (except this one) will use MyHPOM internal identifiers (pids). This method exists so that a program can resolve the pid for a DOI.


User Management and Authorization API
-------------------------------------

The User Management and Authorization API will enable client applications to set access rules and ownership for resources, create and update user accounts, create and update groups, get information about users or groups, and retrieve lists of resources associated with users and groups. The table below lists the REST URLs that will be implemented as part of the MyHPOM User Management and Authorization API. The following assume that each Resource has a single owner. However other users can be given “Full” permissions with all of the privileges of ownership. A single owner is needed for the purpose of disk space quotas so that a Resource only counts against the quota of one user. In all other respects, a user with “Full” permissions over a resource and an owner as described below are the same.

Table 2. MyHPOM user management and authorization API URLs and methods.

| **Release** | **REST Path**                                                                                                                      | **Function**                  | **Parameters**                                            |
|-------------|------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|-----------------------------------------------------------|
| 1           | PUT /resource/owner/{pid}?user={userID}                                                                                            | MyHPOM.setResourceOwner() | (pid, userID) --\> pid                                    |
| 1           | PUT /resource/accessRules/{pid}/?principaltype=(user|group)&principleID={id}&access=(edit|view|donotdistribute)&allow=(true|false) | MyHPOM.setAccessRules()   | (pid, principalType, principleID, access, allow) --\> pid |
| 1           | POST /accounts                                                                                                                     | MyHPOM.createAccount()    | (user) --\> userID                                        |
| 1           | PUT /accounts/{userID}                                                                                                             | MyHPOM.updateAccount()    | (userID, user) --\> userID                                |
| 1           | GET /accounts/{userID}                                                                                                             | MyHPOM.getUserInfo()      | (userID) --\> user                                        |
| 1           | GET /accounts?query={query}[&status={status}&start={start}&count={count}]                                                          | MyHPOM.listUsers()        | (query, status, start, count) --\> userList               |
| 1           | GET /group/{groupID}                                                                                                               | MyHPOM.getGroupInfo()     | (groupID) --\> group                                      |
| 1           | GET /groups?query={query}[&status={status}&start={start}&count={count}]                                                            | MyHPOM.listGroups()       | (query, status, start, count) --\> groupList              |
| 1           | POST /groups                                                                                                                       | MyHPOM.createGroup()      | (group) --\> groupID                                      |
| 1           | PUT /groups                                                                                                                        | MyHPOM.updateGroup()      | (groupID, group) --\> groupID                             |
| 1           | PUT /groups/{groupID}/owner/?user={userID}                                                                                         | MyHPOM.setGroupOwner()    | (groupID, userID) --\> groupID                            |
| 1           | DELETE /groups/{groupID}/owner/?user={userID}                                                                                      | MyHPOM.deleteGroupOwner() | (groupID, userID) --\> groupID                            |
| 1           | GET /resourceList?groups\_\_contains={groupID}                                                                                     | MyHPOM.getResourceList()  | (queryType, groupID) --\> resourceList                    |
| 1           | GET /resourceList?creator={userID}                                                                                                 | MyHPOM.getResourceList()  | (queryType, userID) --\> resourceList                     |
| 1           | GET /resourceList?sharedWith={userID}                                                                                              | MyHPOM.getResourceList()  | (queryType, userID) --\> resourceList                     |
| 1           | GET /resourceList?creationDate\_\_range={fromDate},{toDate}                                                                        | MyHPOM.getResourceList()  | (queryType, fromDate, toDate) --\> resourceList           |


### MyHPOM.setResourceOwner**(*pid, userID*)* --\> pid

Changes ownership of the specified resource to the user specified by a userID.

**REST URL**: PUT /resource/owner/{pid}?user={userID}

**Parameters**: pid – Unique MyHPOM identifier for the resource to be modified

userID – ID for the user to be set as an owner of the resource identified by pid

**Returns**: The pid of the resource that was modified

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: This can only be done by the resource owner or a MyHPOM administrator.


### MyHPOM.setAccessRules**(*pid, principalType, principalID, access, allow*)* --\> pid

Set the access permissions for an object identified by pid. Triggers a change in the system metadata. Successful completion of this operation in indicated by a HTTP response of 200. Unsuccessful completion of this operation must be indicated by returning an appropriate exception such as NotAuthorized.

**REST URL**: PUT /resource/accessRules/{pid}/?principaltype=(user|group)&principleID={id}&access=(edit|view|donotdistribute)&allow=(true|false)

**Parameters**: pid – Unique MyHPOM identifier for the resource to be modified

principalType – The type of principal (user or group)

principalID – Identifier for the user or group to be granted access

access – Permission to be assigned to the resource for the principal

allow – True for granting the permission, False to revoke

**Returns**: The pid of the resource that was modified

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exceptions.NotFound – The principal identified by principalID does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: “Do not distribute” is an attribute of the resource that is set by a user with “Full” permissions and only applies to users with “Edit” and “View” privileges. There is no “share” privilege in MyHPOM. Share permission is implicit unless prohibited by the “Do not distribute” attribute. The only permissions in MyHPOM are “View”, “Edit” and “Full”.


### MyHPOM.createAccount**(*user*)* --\> userID

Create a new user within the MyHPOM system.

**REST URL**: POST /accounts

**Parameters**: user – An object containing the attributes of the user to be created

**Returns**: The userID of the user that was created

**Return Type**: userID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.InvalidContent – The content of the user object is invalid

Exception.ServiceFailure – The service is unable to process the request

**Note**: This would be done via a JSON object (user) that is in the POST request. Should set a random password, and then send an email to make them verify the account. Unverified accounts can't login and are automatically deleted after a specified time (according to policy).


### MyHPOM.updateAccount**(*userID, user*)* --\> userID

Update an existing user within the MyHPOM system. The user calling this method must have write access to the account details.

**REST URL**: PUT /accounts/{userID}

**Parameters**: userID – ID of the existing user to be modified

user – An object containing the modified attributes of the user to be modified

**Returns**: The userID of the user that was modified

**Return Type**: userID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The user identified by userID does not exist

Exceptions.InvalidContent – The content of the user object is invalid

Exception.ServiceFailure – The service is unable to process the request

**Note**: This would be done via a JSON object (user) that is in the PUT request.


### MyHPOM.getUserInfo**(*userID*)* --\> user

Get the information about a user identified by userID. This would be their profile information, groups they belong to, etc.

**REST URL**: GET /accounts/{userID}

**Parameters**: userID – ID of the existing user to be modified

**Returns**: An object containing the details for the user

**Return Type**: user

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The user identified by userID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.listUsers**(*query, status, start, count*)* --\> userList

List the users that match search criteria.

**REST URL**: GET /accounts?query={query}[&status={status}&start={start}&count={count}]

**Parameters**: query – a string specifying the query to perform

status – (optional) parameter to filter users returned based on status

start=0 – (optional) the zero-based index of the first value, relative to the first record of the resultset that matches the parameters

count=100 – (optional) the maximum number of results that should be returned in the response

**Returns**: An object containing a list of userIDs that match the query. If none match, an empty list is returned.

**Return Type**: userList

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.getGroupInfo**(*groupID*)* --\> group

Get the information about a group identified by groupID. For a group this would be its description and membership list.

**REST URL**: GET /group/{groupID}

**Parameters**: groupID – ID of the existing user to be modified

**Returns**: An object containing the details for the group

**Return Type**: group

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The group identified by groupID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.listGroups**(*query, status, start, count*)* --\> groupList

List the groups that match search criteria.

**REST URL**: GET /groups?query={query}[&status={status}&start={start}&count={count}]

**Parameters**: query – a string specifying the query to perform

status – (optional) parameter to filter groups returned based on status

start=0 – (optional) the zero-based index of the first value, relative to the first record of the resultset that matches the parameters

count=100 – (optional) the maximum number of results that should be returned in the response

**Returns**: An object containing a list of groupIDs that match the query. If none match, an empty list is returned.

**Return Type**: groupList

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.createGroup**(*group*)* --\> groupID

Create a group within MyHPOM. Groups are lists of users that allow all members of the group to be referenced by listing solely the name of the group. Group names must be unique within MyHPOM. Groups can only be modified by users listed as group owners.

**REST URL**: POST /groups

**Parameters**: group – An object containing the attributes of the group to be created

**Returns**: The groupID of the group that was created

**Return Type**: groupID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.InvalidContent – The content of the group object is invalid

Exceptions.GroupNameNotUnique – The name of the group already exists in MyHPOM

Exception.ServiceFailure – The service is unable to process the request

**Note**: This would be done via a JSON object (group) that is in the POST request. May want to add an email verification step to avoid automated creation of fake groups. The creating user would automatically be set as the owner of the created group.


### MyHPOM.updateGroup**(*groupID, group*)* --\> groupID

Modify details of group identified by groupID or add or remove members to/from the group. Group members can be modified only by an owner of the group, otherwise a NotAuthorized exception is thrown. Group members are provided as a list of users that replace the group membership.

**REST URL**: PUT /groups/{groupID}

**Parameters**: groupID – groupID of the existing group to be modified

group – An object containing the modified attributes of the group to be modified and the modified list of userIDs in the group membership

**Returns**: The groupID of the group that was modified

**Return Type**: groupID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The group identified by groupID does not exist

Exceptions.InvalidContent – The content of the group object is invalid

Exception.ServiceFailure – The service is unable to process the request

**Note**: This would be done via a JSON object (group) that is in the PUT request.


### MyHPOM.setGroupOwner**(*groupID, userID*)* --\> groupID

Adds ownership of the group identified by groupID to the user specified by userID. This can only be done by a group owner or MyHPOM administrator.

**REST URL**: PUT /groups/{groupID}/owner/?user={userID}

**Parameters**: groupID – groupID of the existing group to be modified

userID – userID of the existing user to be set as the owner of the group

**Returns**: The groupID of the group that was modified

**Return Type**: groupID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The group identified by groupID does not exist

Exceptions.NotFound – The user identified by userID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.deleteGroupOwner**(*groupID, userID*)* --\> groupID

Removes a group owner identified by a userID from a group specified by groupID. This can only be done by a group owner or MyHPOM administrator.

**REST URL**: DELETE /groups/{groupID}/owner/?user={userID}

**Parameters**: groupID – groupID of the existing group to be modified

userID – userID of the existing user to be removed as the owner of the group

**Returns**: The groupID of the group that was modified

**Return Type**: groupID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The group identified by groupID does not exist

Exceptions.NotFound – The user identified by userID does not exist

Exceptions.InvalidRequest – The request would result in removal of the last remaining owner of the group

Exception.ServiceFailure – The service is unable to process the request

**Note**: A group must have at least one owner.


### MyHPOM.getResourceList**(*queryType, groupID*)* --\> resourceList

Return a list of pids for Resources that have been shared with a group identified by groupID.

**REST URL**: GET /resourceList?groups\_\_contains={groupID}

**Parameters**: queryType – string specifying the type of query being performed

groupID – groupID of the group whose list of shared resources is to be returned

**Returns**: A list of pids for resources that have been shared with the group identified by groupID. If no resources have been shared with a group, an empty list is returned.

**Return Type**: resourceList

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The group identified by groupID does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: See http://django-tastypie.readthedocs.org/en/latest/resources.html\#basic-filtering for implementation details and example. We may want to modify this method to return more than just the pids for resources so that some metadata for the list of resources returned could be displayed without having to call MyHPOM.getScienceMetadata() and MyHPOM.GetSystemMetadata() for every resource in the returned list.


### MyHPOM.getResourceList**(*queryType, userID*)* --\> resourceList

Return a list of pids for Resources that a user identified by userID has created.

**REST URL**: GET /resourceList?creator={userID}

**Parameters**: queryType – string specifying the type of query being performed

userID – userID of the user whose list of created resources is to be returned

**Returns**: A list of pids for resources that have been created by the user. If no resources have been created by the user, an empty list is returned.

**Return Type**: resourceList

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The user identified by userID does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: See http://django-tastypie.readthedocs.org/en/latest/resources.html\#basic-filtering for implementation details and example. We may want to modify this method to return more than just the pids for resources so that some metadata for the list of resources returned could be displayed without having to call MyHPOM.getScienceMetadata() and MyHPOM.GetSystemMetadata() for every resource in the returned list.


### MyHPOM.getResourceList**(*queryType, userID*)* --\> resourceList

Return a list of pids for Resources that have been shared with a user identified by userID.

**REST URL**: GET /resourceList?sharedWith={userID}

**Parameters**: queryType – string specifying the type of query being performed

userID – userID of the user whose list of shared resources is to be returned

**Returns**: A list of pids for resources that have been shared with the user. If no resources have been shared with the user, an empty list is returned.

**Return Type**: resourceList

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The user identified by userID does not exist

Exception.ServiceFailure – The service is unable to process the request

**Note**: See http://django-tastypie.readthedocs.org/en/latest/resources.html\#basic-filtering for implementation details and example. We may want to modify this method to return more than just the pids for resources so that some metadata for the list of resources returned could be displayed without having to call MyHPOM.getScienceMetadata() and MyHPOM.GetSystemMetadata() for every resource in the returned list.


### MyHPOM.getResourceList**(*queryType, fromDate, toDate*)* --\> resourceList

Return a list of pids for Resources whose creation date lies within the specified range.

**REST URL**: GET /resourceList?creationDate\_\_range={fromDate},{toDate}

**Parameters**: queryType – string specifying the type of query being performed

fromDate – the beginning date for the date range

toDate – the ending date for the date range

**Returns**: A list of pids for resources that were created within the given date range. If no resources were created within the given date range, an empty list is returned.

**Return Type**: resourceList

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.InvalidDateRange – The date range provided by the user is invalid

Exception.ServiceFailure – The service is unable to process the request

**Note**: See http://django-tastypie.readthedocs.org/en/latest/resources.html\#basic-filtering for implementation details and example. We may want to modify this method to return more than just the pids for resources so that some metadata for the list of resources returned could be displayed without having to call MyHPOM.getScienceMetadata() and MyHPOM.GetSystemMetadata() for every resource in the returned list.


Resource Discovery API
----------------------

The table below lists the REST URLs that will be implemented as part of the MyHPOM Resource Discovery API.

Table 3. MyHPOM resource discovery API URLs and methods.

| **Release** | **REST Path**                                                                                                      | **Function**                   | **Parameters**                                                   |
|-------------|--------------------------------------------------------------------------------------------------------------------|--------------------------------|------------------------------------------------------------------|
| 2           | GET /resourceList [?fromDate={fromDate}&toDate={toDate} &resourceType={resourceType} &start={start}&count={count}] | MyHPOM.listResources()     | (fromDate, toDate, resourceType, start, count) --\> resourceList |
| 2           | GET /resourceTypes                                                                                                 | MyHPOM.listResourceTypes() | () --\> resourceTypeList                                         |
| 2           | GET /formats                                                                                                       | MyHPOM.listFormats()       | () --\> resourceFormatList                                       |
| 2           | GET /search/{queryType}/{query}                                                                                    | MyHPOM.search()            | (queryType, query) --\> resourceList                             |
| 2           | GET /search                                                                                                        | MyHPOM.listSearchEngines() | () --\> searchEngineList                                         |


### MyHPOM.listResources**(*fromDate, toDate, resourceType, start, count*)* --\> resourceList

Return a list of pids for Resources whose creation date lies within the specified range, and optionally are of a particular resource type. This method is required to support cataloging of resources contained within MyHPOM.

**REST URL**: GET /resourceList [?fromDate={fromDate}&toDate={toDate} &resourceType={resourceType} &start={start}&count={count}]

**Parameters**: fromDate – (optional) the beginning date for the date range

toDate – (optional) the ending date for the date range

resourceType – (optional) a type of resource for which to return results

start=0 – (optional) the zero-based index of the first value, relative to the first record of the resultset that matches the parameters

count=100 – (optional) the maximum number of results that should be returned in the response

**Returns**: A list of pids for resources that meet the given criteria. If no resources meet the criteria, an empty list is returned.

**Return Type**: resourceList

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exception.ServiceFailure – The service is unable to process the request

**Note**: This method is primarily to support outside services that would want to harvest the MyHPOM metadata catalog.


### MyHPOM.listResourceTypes**()* --\> resourceTypeList

Returns a list of all resource types registered in the MyHPOM resource type vocabulary

**REST URL**: GET /resourceTypes

**Parameters**: None

**Returns**: A list of resourceTypes supported by MyHPOM

**Return Type**: resourceTypeList

**Raises**: Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.listFormats**()* --\> resourceFormatList

Returns a list of all resource formats registered in the MyHPOM resource format vocabulary

**REST URL**: GET /formats

**Parameters**: None

**Returns**: A list of resource formats supported by MyHPOM

**Return Type**: resourceFormatList

**Raises**: Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.search**(**queryType, query**)* --\> resourceList

Search the MyHPOM metadata catalog and return a list of pids for resources that match the search criteria. Search may be implemented using more than one type of search engine. The queryType parameter indicates which search engine should be targeted. The value and form of query is determined by the search engine.

**REST URL**: GET /search/{queryType}/{query}

**Parameters**: queryType – the search engine to be used for the search

query – a string containing the query to be executed on the search engine

**Returns**: A list of pids for resources that match the criteria in the query. If no resources match the query criteria, an empty list is returned.

**Return Type**: resourceList

**Raises**: Exception.InvalidQueryType – the query type is invalid

Exception.InvalidQuery – the query string is invalid

Exception.ServiceFailure – The service is unable to process the request

**Note**: We may want to modify this method to return more than just the pids for resources so that some metadata for the list of resources returned could be displayed without having to call MyHPOM.getScienceMetadata() and MyHPOM.GetSystemMetadata() for every resource in the returned list. ***Also, this method is still pending selection of the underlying metadata catalog and search engine(s).***


Social API
----------

The table below lists the REST URLs that will be implemented as part of the MyHPOM Social API.

Table 4. MyHPOM social API URLs and methods.

| **Release** | **REST Path**                                             | **Function**                      | **Parameters**                              |
|-------------|-----------------------------------------------------------|-----------------------------------|---------------------------------------------|
| 1           | POST /resource/endorse/{pid}/{userID}                     | MyHPOM.endorseResource()      | (pid, userID) --\> pid                      |
| 4           | POST /followUser/{userID}/{followerID}                    | MyHPOM.followUser()           | (userID, followerID) --\> userID            |
| 4           | DELETE /followUser/{userID}/{followerID}                  | MyHPOM.deleteFollowUser()     | (userID, followerID) --\> userID            |
| 4           | POST /followResource/{pid}/{followerID}                   | MyHPOM.followResource()       | (pid, followerID) --\> pid                  |
| 4           | DELETE /followResource/{pid}/{followerID}                 | MyHPOM.deleteFollowResource() | (pid, followerID) --\> pid                  |
| 4           | POST /followGroup/{groupID}/{followerID}                  | MyHPOM.followGroup()          | (groupID, followerID) --\> groupID          |
| 4           | DELETE /followGroup/{groupID}/{followerID}                | MyHPOM.deleteFollowGroup()    | (groupID, followerID) --\> groupID          |
| 1           | POST /resource/annotation/{pid}/{userID}                  | MyHPOM.annotateResource()     | (pid, annotation, userID) --\> annotationID |
| 1           | GET /resource/annotations/{pid}                           | MyHPOM.getAnnotations()       | (pid) --\> annotationList                   |
| 1           | POST /resource/annotation/endorse/{annotationID}/{userID} | MyHPOM.endorseAnnotation()    | (annotationID, userID) --\> annotationID    |


### MyHPOM.endorseResource**(*pid, userID*)* --\> pid

Create an endorsement or (+1) for a resource in MyHPOM identified by pid for the user identified by userID

**REST URL**: POST /resource/endorse/{pid}/{userID}

**Parameters**: pid – Unique MyHPOM identifier for the resource being endorsed

userID – userID of the user that is endorsing the resource identified by pid

**Returns**: The pid of the resource that was endorsed

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exceptions.NotFound – The user identified by userID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.followUser**(*userID, followerID*)* --\> userID

Start following a MyHPOM user identified by userID.

**REST URL**: POST /followUser/{userID}/{followerID}

**Parameters**: userID – userID of the MyHPOM user to be followed

followerID – userID of the MyHPOM user requesting to follow the user identified by userID

**Returns**: The userID of the MyHPOM user being followed

**Return Type**: userID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The user identified by userID does not exist

Exceptions.NotFound – The user identified by followerID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.deleteFollowUser**(*userID, followerID*)* --\> userID

Stop following a MyHPOM user identified by userID.

**REST URL**: DELETE /followUser/{userID}/{followerID}

**Parameters**: userID – userID of the MyHPOM user being followed

followerID – userID of the MyHPOM user following the user identified by userID

**Returns**: The userID of the MyHPOM user being followed

**Return Type**: userID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The user identified by userID does not exist

Exceptions.NotFound – The user identified by followerID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.followResource**(*pid, followerID*)* --\> pid

Start following a MyHPOM resource identified by pid.

**REST URL**: POST /followResource/{pid}/{followerID}

**Parameters**: pid – Unique MyHPOM identifier for the resource to be followed

followerID – userID of the MyHPOM user requesting to follow the resource identified by pid

**Returns**: The pid of the MyHPOM resource being followed

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exceptions.NotFound – The user identified by followerID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.deleteFollowResource**(*pid, followerID*)* --\> pid

Stop following a MyHPOM resource identified by pid.

**REST URL**: DELETE /followResource/{pid}/{followerID}

**Parameters**: pid – Unique MyHPOM identifier for the resource being followed

followerID – userID of the MyHPOM user following the resource identified by pid

**Returns**: The pid of the MyHPOM resource being followed

**Return Type**: pid

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exceptions.NotFound – The user identified by followerID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.followGroup**(*groupID, followerID*)* --\> groupID

Start following a MyHPOM group identified by groupID.

**REST URL**: POST /followGroup/{groupID}/{followerID}

**Parameters**: groupID – Unique MyHPOM identifier for the group to be followed

followerID – userID of the MyHPOM user requesting to follow the group identified by groupID

**Returns**: The groupID of the MyHPOM group being followed

**Return Type**: groupID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The group identified by groupID does not exist

Exceptions.NotFound – The user identified by followerID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.deleteFollowGroup**(*groupID, followerID*)* --\> groupID

Stop following a MyHPOM group identified by groupID.

**REST URL**: DELETE /followGroup/{groupID}/{followerID}

**Parameters**: groupID – Unique MyHPOM identifier for the group being followed

followerID – userID of the MyHPOM user following the group identified by groupID

**Returns**: The groupID of the MyHPOM group being followed

**Return Type**: groupID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The group identified by groupID does not exist

Exceptions.NotFound – The user identified by followerID does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.annotateResource**(*pid, annotation, userID, previousAnnotationID*)* --\> annotationID

Create a comment about a resource in MyHPOM identified by pid.

**REST URL**: POST /resource/annotation/{pid}/{userID}

**Parameters**: pid – Unique MyHPOM identifier for the resource being annotated
annotation – an object containing the annotation to be applied to the resource identified by pid
userID – userID of the MyHPOM user creating the annotation
previousAnnotationID - (optional) AnnotationID of the previous comment on this resource that this comment follows on from. If omitted the comment is a new comment on a resource.

**Returns**: The annotationID of the annotation that is created

**Return Type**: annotationID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exceptions.InvalidContent – The content of the annotation object is invalid

Exceptions.NotFound – The user identified by userID does not exist

Exception.ServiceFailure – The service is unable to process the request

Exceptions.NotFound - The previousAnnotationID is not an annotation of the resource identified by pid


### MyHPOM.getAnnotations**(*pid*)* --\> annotationList

Get the list of annotations for a resource identified by pid.

**REST URL**: GET /resource/annotations/{pid}

**Parameters**: pid – Unique MyHPOM identifier for the resource whose annotations are to be retrieved

**Returns**: An object containing a list of annotations that have been added to a MyHPOM resource identified by pid.

**Return Type**: annotationList

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The resource identified by pid does not exist

Exception.ServiceFailure – The service is unable to process the request


### MyHPOM.endorseAnnotation**(*annotationID, userID*)* --\> annotationID

Create an endorsement or (+1) by a user identified by userID for an annotation identified by annotationID.

**REST URL**: POST /resource/annotation/endorse/{annotationID}/{userID}

**Parameters**: annotationID – Unique MyHPOM identifier for the annotation to be endorsed

userID – userID of the MyHPOM user creating the annotation endorsement

**Returns**: The annotationID of the annotation that is endorsed

**Return Type**: annotationID

**Raises**: Exceptions.NotAuthorized – The user is not authorized

Exceptions.NotFound – The annotation identified by annotationID does not exist

Exceptions.NotFound – The user identified by userID does not exist

Exception.ServiceFailure – The service is unable to process the request

DataONE Member Node API
-----------------------

The MyHPOM Data Management Plan states that MyHPOM will implement the DataONE Member Node APIs and become a DataONE Member Node. Most of the methods in the previous sections have equivalent methods in the DataONE Member Node APIs. MyHPOM will have to implement that additional methods described in the DataONE API documentation to become a fully compliant DataONE Member Node (see [http://mule1.dataone.org/ArchitectureDocs-current/apis/MN\_APIs.html\#](http://mule1.dataone.org/ArchitectureDocs-current/apis/MN_APIs.html)).

Acknowledgements
================

This work was supported by the National Science Foundation under collaborative grants OCI-1148453 and OCI-1148090 for the development of MyHPOM (<http://www.hydroshare.org>). Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

DataONE (2013). DataONE APIs. <http://mule1.dataone.org/ArchitectureDocs-current/apis/index.html>.

import os

from .component import CompositeComponent, ExternalControl
from .aws.llambda import Lambda
from .aws.iam import IAMRole, RoleInlinePolicy
from .aws.api_gateway import DomainName, BasePathMapping, RestApi
from .aws.acm import SslCertificate


class ApiLambda(Lambda):

    def __init__(self):
        super().__init__(name=f"upload-api-{os.environ['DEPLOYMENT_STAGE']}")


class ApiLambdaRole(IAMRole):
    def __init__(self):
        super().__init__(name=f"upload-api-{os.environ['DEPLOYMENT_STAGE']}", trust_document=None)

    def set_it_up(self):
        raise ExternalControl("Use \"make deploy\" to set this up")


class ApiLambdaRolePolicy(RoleInlinePolicy):
    def __init__(self):
        super().__init__(role_name=f"upload-api-{os.environ['DEPLOYMENT_STAGE']}",
                         name=f"upload-api-{os.environ['DEPLOYMENT_STAGE']}",
                         policy_document=None)

    def set_it_up(self):
        raise ExternalControl("Use \"make deploy\" to set this up")


class ApiSSLCert(SslCertificate):
    def __init__(self):
        wildcard_cert_domain = ".".join(['*'] + os.environ['API_HOST'].split('.')[1:])
        super().__init__(domain=wildcard_cert_domain)


class ApiDomain(DomainName):
    def __init__(self):
        super().__init__(domain=os.environ['API_HOST'])


class UploadRestApi(RestApi):
    def __init__(self, quiet=False):
        super().__init__(name='upload.api_server', stage=os.environ['DEPLOYMENT_STAGE'], quiet=quiet)


class ApiBasePathMapping(BasePathMapping):
    def __init__(self):
        rest_api = UploadRestApi(quiet=True)
        super().__init__(
            domain_name=os.environ['API_HOST'],
            base_path='',
            rest_api_id=rest_api.id
        )


class UploadApi(CompositeComponent):

    SUBCOMPONENTS = {
        'api-lambda': ApiLambda,
        'apl-lambda-role': ApiLambdaRole,
        'apl-lambda-role-policy': ApiLambdaRolePolicy,
        'ssl-cert': ApiSSLCert,
        'rest-api': UploadRestApi,
        'custom-domain': ApiDomain,
        'base-path-mapping': ApiBasePathMapping,
    }

    def __str__(self):
        return "Upload API:"

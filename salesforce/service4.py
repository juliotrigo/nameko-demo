import operator

from nameko.rpc import RpcProxy
from nameko.events import event_handler
from nameko_salesforce.streaming import handle_sobject_notification
from nameko_salesforce.api import SalesforceAPI
from nameko_redis import Redis
from ddebounce import skip_duplicates

from source_tracker import SourceTracker
from tasks import ScheduleTask, task


print("BASIC UP AND DOWN SYNC")
print("SOURCE TRACKING")
print("SKIP DUPLICATES")
print("ASYNC TASKS")


def skip_duplicate_key(sobject_type, record_type, notification):
    return 'salesforce:skip_duplicate({})'.format(notification['event']['replayId'])


class SalesforceService:

    name = 'salesforce'

    contacts_rpc = RpcProxy('contacts')

    salesforce = SalesforceAPI()

    source_tracker = SourceTracker()

    redis = Redis('lock')

    schedule_task = ScheduleTask()

    @event_handler('contacts', 'contact_created')
    def handle_platform_contact_created(self, payload):

        if self.source_tracker.is_sourced_from_salesforce():
            print("Ignoring event that was sourced from salesforce")
            return

        self.schedule_task(self.create_on_salesforce, payload)

    @handle_sobject_notification(
        'Contact', exclude_current_user=True,
        notify_for_operation_update=False
    )
    @skip_duplicates(operator.attrgetter('redis'), key=skip_duplicate_key)
    def handle_sf_contact_created(self, sobject_type, record_type, notification):
        self.schedule_task(self.create_on_platform, notification)

    @task
    def create_on_salesforce(self, payload):
        result = self.salesforce.Contact.create(
            {'LastName': payload['contact']['name']}
        )
        print('Created {} on salesforce'.format(result))

    @task
    def create_on_platform(self, payload):
        with self.source_tracker.sourced_from_salesforce():
            contact = self.contacts_rpc.create_contact(
                {'name': payload['sobject']['Name']}
            )
        print('Created {} on platform'.format(contact))
